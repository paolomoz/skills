---
name: railway-deploy
description: Deploy a monorepo to Railway with multiple services using Dockerfiles, config-as-code, and the Railway CLI/GraphQL API. Use when deploying apps to Railway, setting up Railway projects, or fixing Railway build failures.
---

# Railway Deploy

## Instructions

Deploy a monorepo (or single app) to Railway as separate services with Dockerfiles and config-as-code.

### Prerequisites

1. Install the Railway CLI: `npm i -g @railway/cli`
2. Authenticate: `railway login` (opens browser)
3. Verify: `railway whoami`

### Step 1: Create Dockerfiles

Create a `Dockerfile` in each service directory. Example patterns:

**Python FastAPI backend:**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Next.js frontend:**
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["sh", "-c", "npm start -- -H 0.0.0.0 -p ${PORT:-3000}"]
```

Key rules:
- Always bind to `0.0.0.0` (not localhost) so Railway can route traffic
- Use `${PORT:-<default>}` — Railway injects the `PORT` env var

### Step 2: Create `railway.json` config-as-code files

Create a `railway.json` in each service directory to explicitly declare the Dockerfile builder and watch patterns. **This is critical** — without it, Railway defaults to Railpack and may fail.

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": ["<service-dir>/**"]
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE"
  }
}
```

`watchPatterns` prevent changes in one service from triggering rebuilds of another.

### Step 3: Provision Railway project via CLI

```bash
# Create project
railway init --name <project-name>

# Add services linked to GitHub repo
railway add --service backend --repo <owner>/<repo>
railway add --service frontend --repo <owner>/<repo>
```

### Step 4: Set root directories via GraphQL API

**The CLI `railway environment edit --service-config` command for root directories is unreliable.** Use the GraphQL API instead:

1. Get the auth token from `~/.railway/config.json` (key: `user.token`)
2. Get service IDs and environment ID from `railway status --json`
3. Set root directories:

```bash
RAILWAY_TOKEN="<token>"
ENV_ID="<environment-id>"

# Set root directory for a service
curl -s https://backboard.railway.com/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { serviceInstanceUpdate(serviceId: \"<service-id>\", environmentId: \"'"$ENV_ID"'\", input: { rootDirectory: \"<dir>\" }) }"}'
```

Repeat for each service. Verify with:
```bash
curl -s https://backboard.railway.com/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { project(id: \"<project-id>\") { services { edges { node { id name serviceInstances { edges { node { rootDirectory } } } } } } } }"}'
```

### Step 5: Set environment variables

```bash
railway variables --service backend \
  --set "KEY1=value1" \
  --set "KEY2=value2"

railway variables --service frontend \
  --set "BACKEND_URL=http://backend.railway.internal:8000"
```

Read secrets from `.env` files rather than hardcoding them.

### Step 6: Configure networking

- **Frontend**: Generate a public domain: `railway domain --service frontend --json`
- **Backend**: Keep private — the frontend proxies requests via Railway's internal network (`http://<service>.railway.internal:<port>`)
- **CORS**: Set `CORS_ORIGINS` on the backend to the frontend's public domain

```bash
railway variables --service backend \
  --set 'CORS_ORIGINS=["https://<frontend-domain>.up.railway.app"]'
```

### Step 7: Deploy

Push to GitHub — Railway auto-builds from the linked repo. Or trigger manually:

```bash
railway redeploy --service backend --yes
railway redeploy --service frontend --yes
```

### Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Error creating build plan with Railpack" | Railway not detecting Dockerfile | Add `railway.json` with `"builder": "DOCKERFILE"` and/or set `RAILWAY_DOCKERFILE_PATH=Dockerfile` env var |
| Root directory not set | CLI `environment edit` silently fails | Use GraphQL API `serviceInstanceUpdate` mutation instead |
| Frontend can't reach backend | Private networking misconfigured | Ensure `BACKEND_URL=http://<backend-service>.railway.internal:<port>` on frontend |
| CORS errors | Backend doesn't allow frontend origin | Set `CORS_ORIGINS` env var on backend to frontend's public domain |
| Build succeeds but container crashes | Not binding to `0.0.0.0` or wrong port | Bind to `0.0.0.0` and use `${PORT}` env var |
