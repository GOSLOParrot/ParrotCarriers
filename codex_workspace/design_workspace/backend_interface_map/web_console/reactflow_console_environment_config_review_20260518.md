# ReactFlow Web Console Environment Config Review (2026-05-18)

Scope: `web/console_app` ReactFlow Console, L2-B operation page, collaboration flow page, 7893 Web BFF, 8790 app-monitor, laptop Castle stack.

## Current Finding

- The ReactFlow Console browser code uses relative `/api` and `/health` paths.
- Before this review, Vite dev mode hard-coded those paths to `http://127.0.0.1:7893`.
- Therefore a laptop dev server was not automatically "true connected to ECS"; it connected to whatever was running on the laptop at `7893`.
- When the built console is served by the ECS/Web BFF origin, same-origin `/api` is ECS. When Vite is used locally, the Vite proxy decides the target.

## Added Configuration Surface

- `web/console_app/vite.config.ts` now reads `PARROT_WEB_CONSOLE_API_TARGET` or `VITE_PARROT_WEB_CONSOLE_API_TARGET`.
- `npm run dev:laptop` loads Vite mode `laptop`.
- `npm run dev:ecs` loads Vite mode `ecs`.
- `web/console_app/env.laptop.example` points the Vite proxy at laptop app-monitor `http://127.0.0.1:18790`.
- `web/console_app/env.ecs.example` points the Vite proxy at ECS app-monitor `http://8.216.45.45:8790`.
- `GET /api/console/config` now returns a browser-safe `environment` snapshot on both 7893 Web BFF and 8790 app-monitor.
- The ReactFlow Console settings popover now shows active profile, service, API target, Graphiti target, runtime data root, and redacted auth/OAuth availability.

## How To Switch

Laptop Castle:

```powershell
powershell -ExecutionPolicy Bypass -File infra\laptop-castle.ps1 -Action up
cd web\console_app
Copy-Item env.laptop.example .env.laptop
npm run dev:laptop
```

After code changes that affect Python services, use `-Action rebuild` instead
of `restart`. The laptop compose stack builds code into Docker images; it does
not live-mount the repo source into `/app`.

```powershell
powershell -ExecutionPolicy Bypass -File infra\laptop-castle.ps1 -Action rebuild
```

Public ECS from local Vite:

```powershell
cd web\console_app
Copy-Item env.ecs.example .env.ecs
npm run dev:ecs
```

One-off override without writing an env file:

```powershell
$env:PARROT_WEB_CONSOLE_API_TARGET = "http://127.0.0.1:18790"
npm run dev
```

## Migration Risks

- Do not copy ECS `.env`, deploy mirrors, LiveKit secrets, token mint secrets, or Google OAuth files wholesale to the laptop.
- If laptop nanobot points at ECS Redis or ECS Graphiti/FalkorDB, it can consume production tasks or write production memory. Laptop stack should use compose service names inside Docker or `127.0.0.1:16379/16380` from host tools.
- Google Calendar/Gmail OAuth is account-scoped. Reusing the same OAuth credentials on laptop can read or mutate the real account if write routes are enabled.
- Photo/Ref paths are safe only when stored relative to a configured runtime root or served through a resolver API. Absolute ECS paths such as `/opt/parrot/...` will not survive Windows/laptop movement.
- Laptop compose maps runtime data to `codex_workspace/local_runtime/castle_laptop/data` on the host and `/app/data` in containers. Browser UI should not treat host file paths as stable external refs.
- Unity `parrot_config.json` is Android build-time config. It is not Web Console environment selection.

## Target Policy

- Web Console environment selection belongs to the Web/BFF configuration layer.
- Browser UI may show target profile and redacted endpoint summaries, but secrets stay in server env.
- Mutating operations must surface their active target before apply: RoomSetting, Obsidian scan/import, Graphiti import/materialize, L2-B drafts, Google Calendar changes, and workflow action gates.
- L2-B remains a buffer/projection layer, not the strict SSOT. Source-to-DSG buffer policy should preserve original Graphiti/source payloads and keep ref identity resolvable.

## Verification Checklist

- `GET /api/console/config` returns `environment.service` on 7893 and 8790.
- ReactFlow settings popover shows `profile / service`.
- `npm run typecheck` passes.
- Target smoke after laptop stack is up:
  - `GET http://127.0.0.1:18790/health`
  - `GET http://127.0.0.1:18790/api/console/config`
  - `GET http://127.0.0.1:18790/api/graphiti/status`
- Target smoke for ECS:
  - `GET http://8.216.45.45:8790/health`
  - `GET http://8.216.45.45:8790/api/console/config`
  - `GET http://8.216.45.45:8790/api/graphiti/status`
