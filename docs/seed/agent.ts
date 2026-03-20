/**
 * vibecode-agent/src/agent.ts
 *
 * The core deploy agent. Accepts a DeployJob and streams
 * messages back via an AsyncGenerator — wire this to your
 * WebSocket / SSE layer in deploy-portal.
 */

import {
  query,
  createSdkMcpServer,
  tool,
} from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import type { DeployJob, AgentMessage, ToolPermission } from "../types/index";
import { awsTools } from "../tools/aws";
import { repoTools } from "../tools/repo";
import { SYSTEM_PROMPT } from "./system-prompt";

// ─── Permission Gate ──────────────────────────────────────────────────────────
//
// This is your authorization layer. Auto-approve safe ops,
// gate destructive ones behind human approval.
//
// In a real deploy-portal, REQUIRE_APPROVAL ops would pause
// the stream and send a WebSocket event to the frontend, then
// wait for the user to click "Approve" before continuing.

const REQUIRE_APPROVAL = new Set([
  "push_to_production",
  "run_terraform_apply",
  "delete_ecr_repo",
  "rotate_secrets",
]);

const AUTO_ALLOW = new Set([
  "Bash",
  "Read",
  "Glob",
  "list_ecr_repos",
  "get_deploy_status",
  "clone_repo",
  "run_terraform_plan", // plan is read-only, apply requires approval
]);

async function canUseTool(
  toolName: string,
  input: Record<string, unknown>,
  onApprovalRequired: (tool: string, input: unknown) => Promise<boolean>
): Promise<{ behavior: "allow" | "deny"; message?: string }> {
  if (AUTO_ALLOW.has(toolName)) {
    return { behavior: "allow" };
  }

  if (REQUIRE_APPROVAL.has(toolName)) {
    const approved = await onApprovalRequired(toolName, input);
    return approved
      ? { behavior: "allow" }
      : { behavior: "deny", message: `User denied ${toolName}` };
  }

  // Default: allow but log for audit
  console.log(`[AUDIT] Tool called: ${toolName}`, input);
  return { behavior: "allow" };
}

// ─── Agent Runner ─────────────────────────────────────────────────────────────

export async function* runDeployAgent(
  job: DeployJob,
  onApprovalRequired: (tool: string, input: unknown) => Promise<boolean>
): AsyncGenerator<AgentMessage> {
  // Build the in-process MCP server with all Vibecode tools
  const vibeServer = createSdkMcpServer({
    name: "vibecode-tools",
    version: "1.0.0",
    tools: [...awsTools, ...repoTools],
  });

  const prompt = buildPrompt(job);

  for await (const message of query({
    prompt,
    options: {
      model: "claude-sonnet-4-6", // Sonnet 4.6 — good balance of speed + capability
      allowedTools: [
        "Bash",
        "Read",
        "Glob",
        "mcp__vibecode-tools__*", // wildcard: allow all vibecode tools
      ],
      mcpServers: {
        "vibecode-tools": vibeServer,
      },
      maxTurns: 40, // deploy tasks can be multi-step; cap prevents runaway
      canUseTool: async (toolName, input) => {
        const result = await canUseTool(
          toolName,
          input as Record<string, unknown>,
          onApprovalRequired
        );
        return result.behavior === "allow"
          ? { behavior: "allow" as const, updatedInput: input }
          : { behavior: "deny" as const, message: result.message };
      },
    },
  })) {
    // Normalize to your AgentMessage type and yield upstream
    yield normalizeMessage(message);
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildPrompt(job: DeployJob): string {
  return `
Deploy the following application:

- Repo URL: ${job.repoUrl}
- App name: ${job.appName}
- Target environment: ${job.environment}
- AWS region: ${job.region ?? "us-east-1"}
${job.envVars ? `- Environment variables:\n${Object.entries(job.envVars).map(([k, v]) => `  ${k}=${v}`).join("\n")}` : ""}
${job.notes ? `- Additional notes: ${job.notes}` : ""}

Steps to follow:
1. Clone the repo
2. Detect the app type (Node, Python, etc.) and confirm a Dockerfile exists or generate one
3. Build and push the Docker image to ECR
4. Run terraform plan — pause and wait for approval before apply
5. Deploy to ECS (staging) or (production) based on environment
6. Verify the deployment health check passes
7. Report the final service URL

If any step fails, explain what went wrong and what you tried.
`.trim();
}

// Normalize raw SDK messages into your app's type
function normalizeMessage(raw: unknown): AgentMessage {
  const msg = raw as Record<string, unknown>;
  return {
    type: (msg.type as string) ?? "unknown",
    subtype: msg.subtype as string | undefined,
    text:
      msg.type === "assistant"
        ? extractText(msg.message)
        : msg.result as string | undefined,
    toolName: msg.type === "tool_use" ? (msg.name as string) : undefined,
    toolInput: msg.type === "tool_use" ? msg.input : undefined,
    raw,
  };
}

function extractText(message: unknown): string | undefined {
  const m = message as Record<string, unknown>;
  if (!Array.isArray(m?.content)) return undefined;
  return (m.content as Array<Record<string, unknown>>)
    .filter((b) => b.type === "text")
    .map((b) => b.text as string)
    .join("");
}
