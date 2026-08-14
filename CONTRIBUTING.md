# Contributing to Portal‑OS v4

Portal‑OS is a modular, multi‑domain operating substrate built on SIM cognitive architecture, TEC orchestration, Umbrella governance, and Class‑C planetary compute. Contributions must preserve architectural clarity, modularity, and domain separation.

## Principles
- Maintain strict separation between kernel, identity, governance, routing, substrate, TEC, suites, shell, SIM, and Umbrella layers.
- Document all new modules in `docs/`.
- Add tests for kernel, identity, routing, TEC, and SIM pipeline changes.
- Follow Umbrella invariants and identity physics rules when modifying core logic.
- Keep SIM → Portal‑OS deterministic build behavior intact.

## Workflow
1. Fork the repository.
2. Create a feature branch.
3. Add or modify modules.
4. Add tests where applicable.
5. Update documentation.
6. Submit a pull request.

## Code Style
- Python: PEP8 + project-specific invariants.
- JSON/YAML: 2-space indentation.
- Markdown: clean, readable, minimal.

## Reporting Issues
Use GitHub Issues. Tag modules:
- `kernel`
- `identity`
- `governance`
- `routing`
- `substrate`
- `tec`
- `sim`
- `umbrella`
- `docs`

## Roadmap
See `docs/roadmap.md`.
