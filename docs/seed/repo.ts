/**
 * vibecode-agent/tools/repo.ts
 *
 * Tools for repo operations. These wrap git/filesystem
 * actions so the agent has typed, auditable entry points
 * rather than raw bash for these specific ops.
 */

import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const WORKSPACE_ROOT = process.env.VIBECODE_WORKSPACE ?? path.join(os.tmpdir(), "vibecode-jobs");

const cloneRepo = tool(
  "clone_repo",
  "Clone a git repository into an isolated workspace directory. Returns the local path.",
  {
    repoUrl: z.string().url().describe("HTTPS or SSH git URL"),
    appName: z.string().describe("Used to name the local directory"),
    ref: z.string().optional().describe("Branch, tag, or commit SHA (default: main)"),
  },
  async ({ repoUrl, appName, ref = "main" }) => {
    const dest = path.join(WORKSPACE_ROOT, appName);
    fs.mkdirSync(WORKSPACE_ROOT, { recursive: true });

    if (fs.existsSync(dest)) {
      fs.rmSync(dest, { recursive: true });
    }

    execSync(`git clone --depth 1 --branch ${ref} ${repoUrl} ${dest}`, {
      stdio: "pipe",
    });

    // List top-level files so the agent can orient itself
    const files = fs.readdirSync(dest);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ localPath: dest, topLevelFiles: files }),
        },
      ],
    };
  }
);

const detectAppType = tool(
  "detect_app_type",
  "Inspect a local repo directory and return the detected runtime and entry point.",
  { localPath: z.string().describe("Absolute path to the cloned repo") },
  async ({ localPath }) => {
    const files = fs.readdirSync(localPath);
    const hasFile = (name: string) => files.includes(name);

    let runtime = "unknown";
    let entryPoint = null;
    let packageManager = null;

    if (hasFile("package.json")) {
      runtime = "node";
      packageManager = hasFile("pnpm-lock.yaml")
        ? "pnpm"
        : hasFile("yarn.lock")
        ? "yarn"
        : "npm";
      const pkg = JSON.parse(
        fs.readFileSync(path.join(localPath, "package.json"), "utf-8")
      );
      entryPoint = pkg.main ?? pkg.scripts?.start ?? null;
    } else if (hasFile("requirements.txt") || hasFile("pyproject.toml")) {
      runtime = "python";
      entryPoint = hasFile("main.py") ? "main.py" : hasFile("app.py") ? "app.py" : null;
    } else if (hasFile("go.mod")) {
      runtime = "go";
    } else if (hasFile("Cargo.toml")) {
      runtime = "rust";
    }

    const hasDockerfile = hasFile("Dockerfile") || hasFile("dockerfile");

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            runtime,
            entryPoint,
            packageManager,
            hasDockerfile,
            files,
          }),
        },
      ],
    };
  }
);

export const repoTools = [cloneRepo, detectAppType];
