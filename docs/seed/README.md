# vibecode-agent

The autonomous deploy agent for Vibecode. Powered by the Claude Agent SDK.

## Architecture

```
deploy-portal (frontend)
    │  POST /api/jobs
    │  WebSocket ws://…?jobId=xxx
    ▼
vibecode-agent (this repo)  ← you are here
    │  runDeployAgent()
    │  Claude Agent SDK (query loop)
    ▼
Claude Sonnet 4.6
    │  calls tools via in-process MCP
    ▼
AWS Tools:  ensure_ecr_repo, get_ecr_login_password,
            get_deploy_status, force_ecs_redeploy, get_secret
Repo Tools: clone_repo, detect_app_type
Bash:       general-purpose (docker build/push, terraform, etc.)
```

## How the loop works

1. `deploy-portal` POSTs a `DeployJob` to `/api/jobs`
2. Server assigns a `jobId`, immediately returns it to the frontend
3. Frontend connects a WebSocket using that `jobId`
4. `runDeployAgent()` starts — internally the Agent SDK drives:
   - gather context (clone repo, detect type)
   - take action (build image, push to ECR, run terraform, deploy ECS)
   - verify (health check)
   - repeat until done
5. Every agent message streams over WebSocket in real time
6. Destructive operations (terraform apply, prod deploys) pause and wait
   for the user to click Approve in the portal

## Permission model

| Tool | Behavior |
|------|----------|
| Bash, Read, Glob, list_ecr_repos, get_deploy_status, clone_repo, run_terraform_plan | Auto-allow |
| push_to_production, run_terraform_apply, delete_ecr_repo, rotate_secrets | Require human approval |
| Everything else | Auto-allow + audit log |

## Getting started

```bash
npm install

# Local test (interactive terminal approval)
ANTHROPIC_API_KEY=sk-... tsx src/test-run.ts

# Full server
ANTHROPIC_API_KEY=sk-... \
AWS_REGION=us-east-1 \
AWS_ACCOUNT_ID=123456789012 \
npm run dev
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `AWS_REGION` | No | Defaults to us-east-1 |
| `AWS_ACCOUNT_ID` | Yes | Your AWS account ID |
| `VIBECODE_WORKSPACE` | No | Where repos are cloned (default: /tmp/vibecode-jobs) |
| `PORT` | No | Server port (default: 3001) |

## Key files

```
src/
  agent.ts         ← core: query() call, permission gate, prompt builder
  system-prompt.ts ← agent personality and operating rules
  server.ts        ← Express + WebSocket bridge to deploy-portal
  test-run.ts      ← local smoke test

tools/
  aws.ts           ← typed AWS tools (ECR, ECS, Secrets Manager)
  repo.ts          ← typed repo tools (clone, detect)

types/
  index.ts         ← DeployJob, AgentMessage, DeployResult
```

## What to build next

- **Job persistence**: Write transcript + result to DynamoDB after each run
- **Audit log**: Persist every tool call with input/output for SOC2
- **Queue**: Add BullMQ or SQS in front of runJob() for concurrency control
- **CLAUDE.md**: Drop a `CLAUDE.md` in your infra repo with Vibecode-specific
  conventions; the agent will read it automatically via settingSources: ['project']
- **Subagents**: Spin off a dedicated terraform subagent for long plan/apply cycles
  so they run in an isolated context window
