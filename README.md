# Portal‑OS v4.2

Portal‑OS is a multi‑domain operating substrate designed to unify SIM cognitive architecture, TEC orchestration, Umbrella governance, and Class‑C planetary compute layers. This repository contains the foundation implementation deployed on Cloudflare Workers.

## Quick Start

### View Your Live Deployment
Visit your Portal-OS at: https://dash.cloudflare.com → Workers & Pages

### Test Endpoints
```
GET  /           - Portal-OS dashboard
GET  /health     - Service health check
POST /api/ping   - Runtime ping
```

## Features

- ✅ Multi-domain operating substrate
- ✅ Global edge deployment (Cloudflare Workers)
- ✅ Automated CI/CD pipeline
- ✅ TypeScript strict mode
- ✅ Security-hardened dependencies
- ✅ Zero-downtime deployments

## Goals

- Provide a clean, modular foundation for Portal‑OS development.
- Support SIM → Portal‑OS deterministic builds.
- Enable multi‑domain compute orchestration at Class‑C scale.
- Maintain Umbrella‑grade governance, invariants, and identity physics.
- Offer clear extension points for suites, shell, substrate, and TEC.

## Architecture

```
src/
  ├── index.ts                    # Cloudflare Workers entrypoint (Hono)
kernel/
  ├── boot.py                     # Kernel initialization
  ├── scheduler.py                # Multi-domain scheduler
  ├── invariants.py               # System invariants
  └── [modules]/                  # Kernel subsystems
identity/                          # Identity & authentication
governance/                        # Rules & policies
routing/                          # Message routing
orchestration/                    # Task orchestration
tec/                              # TEC layer
cognitive/                        # SIM cognitive architecture
```

## Deployment

Portal-OS is automatically deployed to Cloudflare Workers on every push to `main`:

1. Dependencies installed & audited
2. TypeScript compiled with strict checks
3. Project built to `dist/index.js`
4. Tests run (non-blocking)
5. Deployed globally to Cloudflare edge

See `CLOUDFLARE_SETUP.md` for detailed deployment instructions.

## Contributing

Contributions follow these principles:
- Maintain architectural clarity and modularity.
- Keep SIM, TEC, Umbrella, and substrate layers cleanly separated.
- Document new modules in `docs/`.
- Add tests for kernel, identity, routing, and TEC changes.
- Use issues and milestones to track roadmap items.

## Development

```bash
# Install dependencies
npm install

# Local development
npm run dev

# Build
npm run build

# Deploy to Cloudflare
npm run deploy

# Test
npm test
```

## Security

All dependencies are regularly updated and audited. Security vulnerabilities are addressed immediately with automated CI/CD checks.

## License

This project uses the MIT License (see LICENSE).

## Documentation

- **Deployment Guide**: See `CLOUDFLARE_SETUP.md`
- **Kernel Architecture**: See `kernel/README.md`
- **Identity System**: See `identity/README.md`
- **Governance**: See `governance/README.md`

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Portal-OS is production-ready and running on Cloudflare Workers globally.** 🚀
