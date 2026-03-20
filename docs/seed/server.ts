/**
 * vibecode-agent/src/server.ts
 *
 * Thin Express + WebSocket server.
 * deploy-portal POSTs a job → server spawns the agent → streams
 * messages back over WebSocket in real time.
 *
 * Each job runs in its own async context; concurrency is handled
 * by Node's event loop (add a queue/worker pool for high volume).
 */

import express from "express";
import { WebSocketServer, WebSocket } from "ws";
import { createServer } from "http";
import { v4 as uuidv4 } from "uuid";
import { runDeployAgent } from "./agent";
import type { DeployJob, AgentMessage, DeployResult } from "../types/index";

const app = express();
app.use(express.json());

const httpServer = createServer(app);
const wss = new WebSocketServer({ server: httpServer });

// In-memory map of pending approval requests.
// jobId → resolve function called when the user clicks Approve/Deny in the portal.
const pendingApprovals = new Map<string, (approved: boolean) => void>();

// Active WebSocket connections keyed by jobId
const jobSockets = new Map<string, WebSocket>();

// ─── REST: Submit a deploy job ────────────────────────────────────────────────

app.post("/api/jobs", async (req, res) => {
  const job: DeployJob = {
    ...req.body,
    jobId: uuidv4(),
    submittedAt: new Date(),
  };

  res.json({ jobId: job.jobId, status: "queued" });

  // Fire and forget — the WebSocket carries progress
  runJob(job).catch((err) => {
    console.error(`Job ${job.jobId} crashed:`, err);
  });
});

// ─── REST: Approve / deny a pending tool call ─────────────────────────────────

app.post("/api/jobs/:jobId/approve", (req, res) => {
  const { jobId } = req.params;
  const { approved } = req.body as { approved: boolean };
  const resolve = pendingApprovals.get(jobId);
  if (!resolve) {
    res.status(404).json({ error: "No pending approval for this job" });
    return;
  }
  pendingApprovals.delete(jobId);
  resolve(approved);
  res.json({ ok: true });
});

// ─── WebSocket: clients connect with ?jobId=xxx ───────────────────────────────

wss.on("connection", (ws, req) => {
  const url = new URL(req.url!, `http://localhost`);
  const jobId = url.searchParams.get("jobId");
  if (!jobId) { ws.close(); return; }
  jobSockets.set(jobId, ws);
  ws.on("close", () => jobSockets.delete(jobId));
});

// ─── Job runner ───────────────────────────────────────────────────────────────

async function runJob(job: DeployJob): Promise<void> {
  const transcript: AgentMessage[] = [];
  const startMs = Date.now();

  function send(event: string, payload: unknown) {
    const ws = jobSockets.get(job.jobId);
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ event, ...payload as object }));
    }
  }

  send("job:started", { jobId: job.jobId, appName: job.appName });

  // The approval callback: pauses the agent stream until the user responds
  async function onApprovalRequired(toolName: string, input: unknown): Promise<boolean> {
    return new Promise((resolve) => {
      pendingApprovals.set(job.jobId, resolve);
      send("approval:required", {
        jobId: job.jobId,
        toolName,
        input,
      });
    });
  }

  try {
    for await (const message of runDeployAgent(job, onApprovalRequired)) {
      transcript.push(message);

      // Stream each message to the portal in real time
      send("agent:message", { jobId: job.jobId, message });
    }

    const result: DeployResult = {
      jobId: job.jobId,
      success: true,
      durationMs: Date.now() - startMs,
      transcript,
    };
    send("job:complete", { jobId: job.jobId, result });

  } catch (err) {
    const result: DeployResult = {
      jobId: job.jobId,
      success: false,
      errorMessage: String(err),
      durationMs: Date.now() - startMs,
      transcript,
    };
    send("job:failed", { jobId: job.jobId, result });
  }
}

// ─── Start ───────────────────────────────────────────────────────────────────

const PORT = process.env.PORT ?? 3001;
httpServer.listen(PORT, () => {
  console.log(`Vibecode agent server listening on :${PORT}`);
});
