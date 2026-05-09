"""Read-only App v1 Web smoke monitor.

This FastAPI app is intentionally small and local-first. It exposes the same
facade read models that Unity should consume, plus a bounded L2-B snapshot for
debug visualization. It does not edit Google, Obsidian, Graphiti, L2-B, or the
IntentWorkspace payloads.
"""

from __future__ import annotations

from pathlib import Path

from parrot.brain.app_first_version import AppFirstVersionFacade
from parrot.brain.l2b_monitor import build_l2b_snapshot

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - only matters on deployments without [http]
    FastAPI = None  # type: ignore[assignment]
    HTMLResponse = None  # type: ignore[assignment]
    StaticFiles = None  # type: ignore[assignment]


def build_app():  # type: ignore[no-untyped-def]
    """Build the read-only smoke monitor app."""
    if FastAPI is None:
        raise RuntimeError("fastapi not installed; install parrotcarriers[http]")

    app = FastAPI(title="GOSLO App V1 Smoke Monitor")
    asset_root = _pixel_asset_root()
    if asset_root.exists():
        app.mount("/pixel-assets", StaticFiles(directory=str(asset_root)), name="pixel-assets")

    @app.get("/", response_class=HTMLResponse)
    async def index():  # type: ignore[no-untyped-def]
        return _index_html()

    @app.get("/api/app/canvas")
    async def app_canvas():  # type: ignore[no-untyped-def]
        return AppFirstVersionFacade().canvas_snapshot().as_json()

    @app.get("/api/app/modules")
    async def app_modules():  # type: ignore[no-untyped-def]
        return [status.as_json() for status in AppFirstVersionFacade().list_module_statuses()]

    @app.get("/api/l2b/snapshot")
    async def l2b_snapshot(limit: int = 80):  # type: ignore[no-untyped-def]
        return build_l2b_snapshot(limit=max(1, min(limit, 200))).as_json()

    @app.get("/health")
    async def health():  # type: ignore[no-untyped-def]
        return {"ok": True, "service": "app-v1-monitor"}

    return app


def _pixel_asset_root() -> Path:
    return Path("codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace").resolve()


def _index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GOSLO App V1 Monitor</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #111116;
      --panel: #1a1a22;
      --panel-2: #24232f;
      --ink: #ece9f7;
      --muted: #a9a3bd;
      --accent: #9d7cff;
      --ok: #83e6b2;
      --warn: #ffd37a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(17,17,22,.96), rgba(17,17,22,.98)),
        url('/pixel-assets/curated/00_previews/Paper_UI_preview.png');
      color: var(--ink);
      font: 14px/1.45 ui-monospace, SFMono-Regular, Consolas, monospace;
      image-rendering: pixelated;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 22px;
      border-bottom: 1px solid #302b43;
      background: rgba(18, 17, 25, .92);
    }
    h1 { margin: 0; font-size: 18px; letter-spacing: 0; }
    button {
      border: 1px solid #5d4a93;
      background: #211b33;
      color: var(--ink);
      padding: 8px 11px;
      border-radius: 6px;
      cursor: pointer;
    }
    main {
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 14px;
      padding: 14px;
    }
    section {
      border: 1px solid #39314c;
      background: rgba(26, 26, 34, .94);
      border-radius: 6px;
      min-height: 140px;
      overflow: hidden;
    }
    h2 {
      margin: 0;
      padding: 10px 12px;
      font-size: 13px;
      color: #dcd4ff;
      background: #242032;
      border-bottom: 1px solid #39314c;
    }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding: 10px; }
    .card { background: var(--panel-2); border: 1px solid #343042; border-radius: 5px; padding: 10px; min-height: 86px; }
    .name { color: var(--accent); font-weight: 700; }
    .state { margin-top: 6px; color: var(--ok); }
    .warn { color: var(--warn); }
    .muted { color: var(--muted); }
    pre { margin: 0; padding: 12px; white-space: pre-wrap; color: #d6d0e8; }
    .wide { grid-column: 1 / -1; }
    @media (max-width: 900px) { main { grid-template-columns: 1fr; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>GOSLO App V1 Monitor</h1>
    <button onclick="refresh()">Refresh</button>
  </header>
  <main>
    <section>
      <h2>Module Rail</h2>
      <div id="modules" class="grid"></div>
    </section>
    <section>
      <h2>Canvas Workspace</h2>
      <pre id="workspace">loading...</pre>
    </section>
    <section>
      <h2>Paper Notes</h2>
      <pre id="paper">loading...</pre>
    </section>
    <section>
      <h2>Photo / Awareness</h2>
      <pre id="photo">loading...</pre>
    </section>
    <section class="wide">
      <h2>L2-B Topology</h2>
      <pre id="l2b">loading...</pre>
    </section>
  </main>
  <script>
    async function getJson(url) {
      const res = await fetch(url, {cache: 'no-store'});
      if (!res.ok) throw new Error(`${url}: ${res.status}`);
      return res.json();
    }
    function card(status) {
      const health = status.health === 'ok' ? 'state' : 'state warn';
      return `<div class="card"><div class="name">${status.module_id}</div>` +
        `<div class="${health}">${status.state}</div>` +
        `<div class="muted">${status.summary || ''}</div></div>`;
    }
    async function refresh() {
      const [canvas, l2b] = await Promise.all([
        getJson('/api/app/canvas'),
        getJson('/api/l2b/snapshot?limit=60')
      ]);
      document.getElementById('modules').innerHTML = canvas.module_statuses.map(card).join('');
      document.getElementById('workspace').textContent = JSON.stringify({
        active_workspace_id: canvas.active_workspace_id,
        workspaces: canvas.workspaces
      }, null, 2);
      document.getElementById('paper').textContent = JSON.stringify(canvas.paper_notes, null, 2);
      document.getElementById('photo').textContent = JSON.stringify(canvas.photo_refs, null, 2);
      document.getElementById('l2b').textContent = JSON.stringify(l2b, null, 2);
    }
    refresh().catch(err => {
      document.getElementById('modules').innerHTML =
        `<div class="card"><div class="name">error</div><div class="state warn">${err.message}</div></div>`;
    });
  </script>
</body>
</html>"""


create_app = build_app

__all__ = ["build_app", "create_app"]
