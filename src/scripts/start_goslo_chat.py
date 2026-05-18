"""Start the GOSLO Chat bot — the parrot lady's chat body (nanobot instance).

Usage:
  python src/scripts/start_goslo_chat.py              # Telegram channel (default)
  python src/scripts/start_goslo_chat.py --force-config  # Regenerate config
  python src/scripts/start_goslo_chat.py --no-mode-hook  # Disable Live/Chat mode switching

This is GOSLO's second body: when the Live voice AR body (Brain Agent) is
offline, this chat bot keeps the parrot lady present.  It runs as a separate
nanobot instance with its own config, workspace, and personality (ParrotSoul).

Mode-aware behavior (enabled by default):
  - Checks Redis `parrot.goslo.mode` on every incoming message
  - If active_body=live → forwards message to Brain, replies with a brief note
  - If active_body=chat → processes normally through agent loop

Prerequisites:
  - Redis running (docker compose -f infra/docker-compose.dev.yml up -d)
  - nanobot installed: pip install -e ../nanobot[parrot]
  - GEMINI_API_KEY set
  - TELEGRAM_BOT_TOKEN set (for Telegram channel)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

GOSLO_NANOBOT_DIR = Path.home() / ".nanobot-goslo"
GOSLO_WORKSPACE = Path.home() / ".nanobot" / "goslo-workspace"
FORK_CONFIG = Path(__file__).resolve().parents[3] / "nanobot" / "config" / "goslo_config.json"
GOOGLE_WORKSPACE_SERVER_KEY = "google_workspace"
GITHUB_SERVER_KEY = "github"
GOOGLE_WORKSPACE_ACCOUNT_ENVS = (
    "GOOGLE_WORKSPACE_ACCOUNT_EMAIL",
    "GOOGLE_ACCOUNT_EMAIL",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_if_changed(path: Path, payload: dict[str, Any], *, mode: int = 0o600) -> bool:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == text:
                return False
        except UnicodeDecodeError:
            pass
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(text, encoding="utf-8")
    try:
        os.chmod(path, mode)
    except OSError:
        pass
    return True


def _is_placeholder(value: object) -> bool:
    text = str(value or "").strip()
    return not text or (text.startswith("${") and text.endswith("}"))


def _google_credentials_candidates() -> list[Path]:
    paths: list[Path] = []
    for env_name in ("GOOGLE_WORKSPACE_CREDENTIALS_DIR", "PARROT_GOOGLE_CREDENTIALS_DIR"):
        if env_value := os.getenv(env_name):
            base = Path(env_value).expanduser()
            paths.extend([base / "credentials_python.json", base / "credentials.json"])

    bases = [
        Path.home() / ".nanobot" / "google-workspace-credentials",
        Path.home() / ".local" / "share" / "google-workspace-mcp" / "credentials",
    ]
    for base in bases:
        paths.extend([base / "credentials_python.json", base / "credentials.json"])
    return paths


def _load_google_workspace_credential() -> dict[str, Any] | None:
    for path in _google_credentials_candidates():
        if not path.exists():
            continue
        try:
            data = _read_json(path)
        except Exception:
            continue
        if data.get("refresh_token") and data.get("client_id") and data.get("client_secret"):
            return data
    return None


def _google_workspace_config_dir() -> Path:
    base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "google-workspace-mcp"


def _google_workspace_data_dir() -> Path:
    base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "google-workspace-mcp"


def _email_slug(email: str) -> str:
    safe = email.replace("/", "").replace("\\", "")
    return safe.replace("@", "_at_").replace(".", "_dot_")


def _existing_google_workspace_account_email() -> str:
    accounts_path = _google_workspace_config_dir() / "accounts.json"
    if not accounts_path.exists():
        return ""
    try:
        accounts = _read_json(accounts_path).get("accounts", [])
    except Exception:
        return ""
    for account in accounts:
        email = str(account.get("email", "")).strip()
        if "@" in email:
            return email
    return ""


def _google_workspace_account_email(credential: dict[str, Any] | None) -> str:
    for env_name in GOOGLE_WORKSPACE_ACCOUNT_ENVS:
        email = os.getenv(env_name, "").strip()
        if "@" in email:
            return email
    if credential:
        for key in ("account", "email", "account_email"):
            email = str(credential.get(key, "")).strip()
            if "@" in email:
                return email
    return _existing_google_workspace_account_email()


def _ensure_google_workspace_mcp_state() -> None:
    credential = _load_google_workspace_credential()
    if not credential:
        return

    email = _google_workspace_account_email(credential)
    if not email:
        print(
            "Google Workspace credential found, but no account email is recorded. "
            "Set GOOGLE_WORKSPACE_ACCOUNT_EMAIL or rerun scripts/google_oauth.py."
        )
        return

    accounts_path = _google_workspace_config_dir() / "accounts.json"
    try:
        accounts_data = _read_json(accounts_path) if accounts_path.exists() else {"accounts": []}
    except Exception:
        accounts_data = {"accounts": []}
    accounts = accounts_data.setdefault("accounts", [])
    if not any(account.get("email") == email for account in accounts):
        accounts.append(
            {
                "email": email,
                "category": "personal",
                "description": "ParrotCarriers Google Workspace account",
            }
        )
    if _write_json_if_changed(accounts_path, accounts_data):
        print(f"Google Workspace MCP account registry written to {accounts_path}")

    native_credential = {
        "type": "authorized_user",
        "client_id": credential["client_id"],
        "client_secret": credential["client_secret"],
        "refresh_token": credential["refresh_token"],
    }
    if credential.get("scopes"):
        native_credential["scopes"] = credential["scopes"]

    credential_path = _google_workspace_data_dir() / "credentials" / f"{_email_slug(email)}.json"
    if _write_json_if_changed(credential_path, native_credential):
        print(f"Google Workspace MCP credential written to {credential_path}")


def _sync_google_workspace_config(config: dict[str, Any], template_config: dict[str, Any]) -> bool:
    servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    template_servers = template_config.get("tools", {}).get("mcpServers", {})
    template_google = template_servers.get(GOOGLE_WORKSPACE_SERVER_KEY)
    if not template_google:
        return False

    existing = servers.get(GOOGLE_WORKSPACE_SERVER_KEY) or {}
    merged = json.loads(json.dumps(template_google))
    merged_env = dict(merged.get("env") or {})
    for key, value in (existing.get("env") or {}).items():
        if not _is_placeholder(value):
            merged_env[key] = value

    credential = _load_google_workspace_credential()
    for key in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"):
        env_value = os.getenv(key, "").strip()
        if env_value:
            merged_env[key] = env_value
    if credential:
        merged_env["GOOGLE_CLIENT_ID"] = credential.get("client_id", merged_env.get("GOOGLE_CLIENT_ID", ""))
        merged_env["GOOGLE_CLIENT_SECRET"] = credential.get(
            "client_secret",
            merged_env.get("GOOGLE_CLIENT_SECRET", ""),
        )
    gws_binary = os.getenv("GWS_BINARY_PATH", "").strip() or shutil.which("gws")
    if gws_binary:
        merged_env["GWS_BINARY_PATH"] = gws_binary

    if _is_placeholder(merged_env.get("GOOGLE_CLIENT_ID")) or _is_placeholder(
        merged_env.get("GOOGLE_CLIENT_SECRET")
    ):
        removed = servers.pop(GOOGLE_WORKSPACE_SERVER_KEY, None) is not None
        if removed:
            print("Google Workspace MCP disabled: no OAuth client credentials found.")
        return removed

    merged["env"] = merged_env
    changed = servers.get(GOOGLE_WORKSPACE_SERVER_KEY) != merged
    servers[GOOGLE_WORKSPACE_SERVER_KEY] = merged
    return changed


def _sync_github_mcp_config(config: dict[str, Any]) -> bool:
    servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    if github_token:
        github_env = servers.setdefault(GITHUB_SERVER_KEY, {}).setdefault("env", {})
        if github_env.get("GITHUB_PERSONAL_ACCESS_TOKEN") != github_token:
            github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token
            return True
        return False

    if GITHUB_SERVER_KEY in servers:
        servers.pop(GITHUB_SERVER_KEY, None)
        print("GitHub MCP disabled: GITHUB_TOKEN is not set.")
        return True
    return False


def _sync_telegram_channel(config: dict[str, Any]) -> bool:
    channels = config.setdefault("channels", {})
    telegram = channels.setdefault("telegram", {})
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if telegram_token:
        changed = telegram.get("token") != telegram_token or telegram.get("enabled") is not True
        telegram["enabled"] = True
        telegram["token"] = telegram_token
        return changed

    changed = telegram.get("enabled") is not False or not _is_placeholder(telegram.get("token"))
    telegram["enabled"] = False
    telegram["token"] = ""
    if changed:
        print("Telegram channel disabled: TELEGRAM_BOT_TOKEN is not set.")
    return changed


def _ensure_goslo_workspace() -> None:
    GOSLO_WORKSPACE.mkdir(parents=True, exist_ok=True)
    defaults = {
        "SOUL.md": "# GOSLO Chat\n\nLocal laptop chat workspace placeholder.\n",
        "AGENTS.md": "# Agents\n\nGOSLO chat body runs here when enabled.\n",
        "USER.md": "# User\n\nLaptop sandbox user profile placeholder.\n",
        "TOOLS.md": "# Tools\n\nUse configured nanobot tools conservatively.\n",
    }
    for name, text in defaults.items():
        path = GOSLO_WORKSPACE / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")


def setup_config(force: bool = False) -> Path:
    """Ensure the GOSLO nanobot config exists. Returns path to config.json."""
    config_file = GOSLO_NANOBOT_DIR / "config.json"
    if not FORK_CONFIG.exists():
        print(f"ERROR: Config template not found at {FORK_CONFIG}")
        sys.exit(1)
    template_config = _read_json(FORK_CONFIG)

    if force or not config_file.exists():
        GOSLO_NANOBOT_DIR.mkdir(parents=True, exist_ok=True)

        config = json.loads(json.dumps(template_config))

        gemini_key = (os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()
        if gemini_key:
            config.setdefault("providers", {}).setdefault("gemini", {})["apiKey"] = gemini_key

        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config written to {config_file}")
    else:
        print(f"Using existing config at {config_file}")
        try:
            config = _read_json(config_file)
        except Exception as exc:
            print(f"ERROR: Could not read existing config at {config_file}: {exc}")
            sys.exit(1)

    changed = _sync_telegram_channel(config)
    changed = _sync_google_workspace_config(config, template_config) or changed
    changed = _sync_github_mcp_config(config) or changed

    gemini_key = (os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()
    if gemini_key:
        providers = config.setdefault("providers", {}).setdefault("gemini", {})
        if providers.get("apiKey") != gemini_key:
            providers["apiKey"] = gemini_key
            changed = True

    if changed:
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config updated at {config_file}")

    _ensure_google_workspace_mcp_state()
    _ensure_goslo_workspace()

    return config_file


def run_gateway_with_mode_hook(
    config_file: Path,
    enable_mode_hook: bool = True,
    *,
    verbose: bool = False,
) -> None:
    """Start the nanobot gateway in-process with GOSLO mode hook installed."""
    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.channels.manager import ChannelManager
    from nanobot.config.loader import load_config, set_config_path
    from nanobot.cron.service import CronService
    from nanobot.cron.types import CronJob, CronPayload
    from nanobot.heartbeat.service import HeartbeatService
    from nanobot.nanobot import _make_provider
    from nanobot.session.manager import SessionManager

    import logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    set_config_path(config_file)
    config = load_config(config_file)
    config.agents.defaults.workspace = str(GOSLO_WORKSPACE)

    print(f"\n=== GOSLO Chat Bot (ParrotSoul) ===")
    print(f"  Config:    {config_file}")
    print(f"  Workspace: {GOSLO_WORKSPACE}")
    print(f"  Mode hook: {'enabled' if enable_mode_hook else 'disabled'}")
    print(f"  Verbose logs: {'enabled' if verbose else 'disabled'}")
    print()

    bus = MessageBus()

    try:
        provider = _make_provider(config)
    except Exception as e:
        print(f"ERROR: Failed to create provider: {e}")
        sys.exit(1)

    session_manager = SessionManager(config.workspace_path)
    cron_store_path = config.workspace_path / "cron" / "jobs.json"
    cron = CronService(cron_store_path)

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=config.agents.defaults.model,
        max_iterations=config.agents.defaults.max_tool_iterations,
        context_window_tokens=config.agents.defaults.context_window_tokens,
        web_config=config.tools.web,
        context_block_limit=config.agents.defaults.context_block_limit,
        max_tool_result_chars=config.agents.defaults.max_tool_result_chars,
        provider_retry_mode=config.agents.defaults.provider_retry_mode,
        exec_config=config.tools.exec,
        cron_service=cron,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        session_manager=session_manager,
        mcp_servers=config.tools.mcp_servers,
        channels_config=config.channels,
        timezone=config.agents.defaults.timezone,
    )

    async def on_cron_job(job: CronJob) -> str | None:
        if job.name == "dream":
            try:
                await agent.dream.run()
            except Exception:
                pass
            return None
        resp = await agent.process_direct(
            f"[Scheduled Task] {job.payload.message}",
            session_key=f"cron:{job.id}",
            channel=job.payload.channel or "cli",
            chat_id=job.payload.to or "direct",
        )
        return resp.content if resp else ""

    cron.on_job = on_cron_job

    _original_publish = bus.publish_outbound

    async def _publish_and_archive(msg):
        await _original_publish(msg)
        if msg.content:
            try:
                from parrot.memory.conversation_writer import write_nanobot_turn
                await write_nanobot_turn(
                    "assistant", msg.content,
                    group_id="goslo", source="goslo_chat",
                )
            except ImportError:
                pass
            except Exception:
                pass

    bus.publish_outbound = _publish_and_archive  # type: ignore[assignment]

    channels = ChannelManager(config, bus)

    if enable_mode_hook:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            from nanobot.channels.goslo_mode import install_mode_hook
            n = install_mode_hook(channels, redis_url=redis_url)
            print(f"  Mode hook installed on {n} channel(s)")
        except Exception as e:
            print(f"  WARNING: Failed to install mode hook: {e}")
            print(f"  GOSLO Chat will always respond (no Live/Chat switching)")

    hb_cfg = config.gateway.heartbeat
    heartbeat = HeartbeatService(
        workspace=config.workspace_path,
        provider=provider,
        model=agent.model,
        on_execute=lambda t: agent.process_direct(t, session_key="heartbeat", channel="cli", chat_id="direct"),
        on_notify=lambda _: asyncio.sleep(0),
        interval_s=hb_cfg.interval_s,
        enabled=hb_cfg.enabled,
        timezone=config.agents.defaults.timezone,
    )

    dream_cfg = config.agents.defaults.dream
    if dream_cfg.model_override:
        agent.dream.model = dream_cfg.model_override
    agent.dream.max_batch_size = dream_cfg.max_batch_size
    agent.dream.max_iterations = dream_cfg.max_iterations
    cron.register_system_job(CronJob(
        id="dream",
        name="dream",
        schedule=dream_cfg.build_schedule(config.agents.defaults.timezone),
        payload=CronPayload(kind="system_event"),
    ))

    if channels.enabled_channels:
        print(f"  Channels: {', '.join(channels.enabled_channels)}")
    else:
        print("  WARNING: No channels enabled")

    async def run():
        try:
            await cron.start()
            await heartbeat.start()
            await asyncio.gather(
                agent.run(),
                channels.start_all(),
            )
        except KeyboardInterrupt:
            print("\nShutting down GOSLO Chat...")
        finally:
            await channels.stop_all()
            await heartbeat.stop()
            await cron.stop()

    asyncio.run(run())


def main():
    from dotenv import load_dotenv
    load_dotenv()
    parser = argparse.ArgumentParser(description="Start the GOSLO Chat bot")
    parser.add_argument("--force-config", action="store_true", help="Regenerate config from template")
    parser.add_argument("--no-mode-hook", action="store_true", help="Disable Live/Chat mode switching")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose nanobot/GOSLO chat logs")
    args = parser.parse_args()

    config_file = setup_config(force=args.force_config)
    run_gateway_with_mode_hook(
        config_file,
        enable_mode_hook=not args.no_mode_hook,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
