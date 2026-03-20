/**
 * vibecode-agent/tools/aws.ts
 *
 * Custom typed tools for AWS operations.
 * These give the agent precise, auditable actions instead of
 * raw AWS CLI — you control exactly what surface is exposed.
 */

import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import {
  ECRClient,
  CreateRepositoryCommand,
  DescribeRepositoriesCommand,
  GetAuthorizationTokenCommand,
} from "@aws-sdk/client-ecr";
import {
  ECSClient,
  DescribeServicesCommand,
  UpdateServiceCommand,
  DescribeTasksCommand,
} from "@aws-sdk/client-ecs";
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from "@aws-sdk/client-secrets-manager";

const region = process.env.AWS_REGION ?? "us-east-1";
const ecr = new ECRClient({ region });
const ecs = new ECSClient({ region });
const secrets = new SecretsManagerClient({ region });

// ─── ECR Tools ───────────────────────────────────────────────────────────────

const ensureEcrRepo = tool(
  "ensure_ecr_repo",
  "Create an ECR repository if it doesn't exist. Returns the repo URI.",
  { appName: z.string().describe("Application name, used as repo name") },
  async ({ appName }) => {
    try {
      const res = await ecr.send(
        new DescribeRepositoriesCommand({ repositoryNames: [appName] })
      );
      const uri = res.repositories![0].repositoryUri!;
      return { content: [{ type: "text", text: `ECR repo exists: ${uri}` }] };
    } catch {
      // repo doesn't exist, create it
      const res = await ecr.send(
        new CreateRepositoryCommand({
          repositoryName: appName,
          imageScanningConfiguration: { scanOnPush: true },
          encryptionConfiguration: { encryptionType: "AES256" },
        })
      );
      const uri = res.repository!.repositoryUri!;
      return { content: [{ type: "text", text: `Created ECR repo: ${uri}` }] };
    }
  }
);

const getEcrLoginPassword = tool(
  "get_ecr_login_password",
  "Get a temporary ECR login token for docker login. Use this before docker push.",
  {},
  async () => {
    const res = await ecr.send(new GetAuthorizationTokenCommand({}));
    const token = res.authorizationData![0].authorizationToken!;
    const password = Buffer.from(token, "base64").toString().split(":")[1];
    const endpoint = `${process.env.AWS_ACCOUNT_ID}.dkr.ecr.${region}.amazonaws.com`;
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ password, endpoint }),
        },
      ],
    };
  }
);

// ─── ECS Tools ───────────────────────────────────────────────────────────────

const getDeployStatus = tool(
  "get_deploy_status",
  "Check the current status of an ECS service deployment.",
  {
    cluster: z.string().describe("ECS cluster name"),
    service: z.string().describe("ECS service name"),
  },
  async ({ cluster, service }) => {
    const res = await ecs.send(
      new DescribeServicesCommand({ cluster, services: [service] })
    );
    const svc = res.services?.[0];
    if (!svc) {
      return { content: [{ type: "text", text: `Service not found: ${service}` }] };
    }
    const summary = {
      status: svc.status,
      runningCount: svc.runningCount,
      desiredCount: svc.desiredCount,
      pendingCount: svc.pendingCount,
      deployments: svc.deployments?.map((d) => ({
        status: d.status,
        runningCount: d.runningCount,
        desiredCount: d.desiredCount,
        rolloutState: d.rolloutState,
      })),
    };
    return { content: [{ type: "text", text: JSON.stringify(summary, null, 2) }] };
  }
);

const forceEcsRedeploy = tool(
  "force_ecs_redeploy",
  "Force a new ECS deployment with the latest task definition (used after pushing a new image).",
  {
    cluster: z.string(),
    service: z.string(),
  },
  async ({ cluster, service }) => {
    await ecs.send(
      new UpdateServiceCommand({
        cluster,
        service,
        forceNewDeployment: true,
      })
    );
    return {
      content: [
        { type: "text", text: `Triggered redeploy for ${service} in ${cluster}` },
      ],
    };
  }
);

// ─── Secrets Manager Tools ───────────────────────────────────────────────────

const getSecret = tool(
  "get_secret",
  "Retrieve a secret value from AWS Secrets Manager by name.",
  { secretName: z.string().describe("Full secret name or ARN") },
  async ({ secretName }) => {
    const res = await secrets.send(
      new GetSecretValueCommand({ SecretId: secretName })
    );
    const value = res.SecretString ?? Buffer.from(res.SecretBinary!).toString();
    return { content: [{ type: "text", text: value }] };
  }
);

// ─── Export ──────────────────────────────────────────────────────────────────

export const awsTools = [
  ensureEcrRepo,
  getEcrLoginPassword,
  getDeployStatus,
  forceEcsRedeploy,
  getSecret,
];
