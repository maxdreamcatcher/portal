# Portal‑OS v1 Cloudflare Workers Deployment

This guide covers deploying Portal‑OS v1 to Cloudflare Workers.

## Prerequisites

- [Cloudflare Account](https://dash.cloudflare.com)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
- Node.js 18+
- GitHub account with access to this repository

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Wrangler

Update `wrangler.toml` with your Cloudflare account details:

```bash
wrangler whoami
```

### 3. GitHub Secrets (for CI/CD)

Add these secrets to your GitHub repository settings:

- `CLOUDFLARE_API_TOKEN` — Get from [API Tokens](https://dash.cloudflare.com/profile/api-tokens)
- `CLOUDFLARE_ACCOUNT_ID` — Found in Cloudflare dashboard URL: `https://dash.cloudflare.com/{ACCOUNT_ID}`

## Deployment

### Local Development

```bash
npm run dev
```

Runs at `http://localhost:8787`

### Production Deployment

#### Option 1: Manual Deployment

```bash
npm run deploy
```

#### Option 2: Automatic Deployment via GitHub Actions

Push to `main` branch:

```bash
git push origin main
```

The `.github/workflows/deploy.yml` workflow will automatically build and deploy to Cloudflare Workers.

## API Endpoints

- `GET /` — Portal‑OS v1 web interface
- `POST /api/ping` — Runtime ping endpoint
- `GET /health` — Service health check

## Project Structure

```
portal--v4/
├── src/
│   └── index.ts           # Cloudflare Workers entrypoint
├── portal-os-v1/
│   ├── bootstrap.py       # Python OS bootstrap
│   ├── web/               # Web interface (HTML/CSS/JS)
│   └── [modules]/         # OS subsystems
├── wrangler.toml          # Cloudflare Workers config
├── package.json           # Node.js dependencies
└── tsconfig.json          # TypeScript config
```

## Monitoring

Check deployment status:

```bash
wrangler deployments list
```

View logs:

```bash
wrangler tail
```

## Troubleshooting

### Deploy fails with auth error

Ensure `CLOUDFLARE_API_TOKEN` is valid and has Workers deploy permissions.

### Static files not loading

Verify the `portal-os-v1/web/` directory is committed to git and the paths in `src/index.ts` are correct.

### Node.js compatibility

Workers use the Node.js compatibility flag. See `wrangler.toml` for `compatibility_flags = ["nodejs_compat"]`.

## References

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/cli-wrangler/)
- [Hono Framework](https://hono.dev)
