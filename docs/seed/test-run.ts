/**
 * vibecode-agent/src/test-run.ts
 *
 * Local smoke test. Run with:
 *   ANTHROPIC_API_KEY=sk-... tsx src/test-run.ts
 *
 * Simulates a deploy job and prints every agent message to stdout.
 * Approval prompts go to stdin so you can test the gate interactively.
 */

import * as readline from "readline";
import { runDeployAgent } from "./agent";
import type { DeployJob } from "../types/index";

const job: DeployJob = {
  jobId: "test-001",
  appName: "my-test-app",
  repoUrl: "https://github.com/davidbmar/deploy-portal",
  environment: "staging",
  region: "us-east-1",
  envVars: {
    NODE_ENV: "staging",
    PORT: "3000",
  },
  submittedBy: "david",
  submittedAt: new Date(),
};

// Approval gate: asks the user Y/N in the terminal
async function onApprovalRequired(toolName: string, input: unknown): Promise<boolean> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    console.log(`\n⚠️  APPROVAL REQUIRED: ${toolName}`);
    console.log("Input:", JSON.stringify(input, null, 2));
    rl.question("Approve? [y/N] ", (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === "y");
    });
  });
}

async function main() {
  console.log(`\n🚀 Starting deploy agent for job: ${job.jobId}\n`);
  console.log("=".repeat(60));

  for await (const message of runDeployAgent(job, onApprovalRequired)) {
    switch (message.type) {
      case "assistant":
        if (message.text) {
          process.stdout.write(`\n🤖 ${message.text}\n`);
        }
        break;
      case "tool_use":
        console.log(`\n🔧 Tool: ${message.toolName}`);
        console.log("   Input:", JSON.stringify(message.toolInput, null, 2));
        break;
      case "tool_result":
        console.log(`   Result: ${JSON.stringify(message.raw)}`);
        break;
      case "result":
        console.log(`\n✅ Done: ${message.text}`);
        break;
      default:
        // system init messages etc — skip
    }
  }

  console.log("\n" + "=".repeat(60));
  console.log("Agent finished.");
}

main().catch(console.error);
