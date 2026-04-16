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
import sys
from pathlib import Path

GOSLO_NANOBOT_DIR = Path.home() / ".nanobot-goslo"
GOSLO_WORKSPACE = Path.home() / ".nanobot" / "goslo-workspace"
FORK_CONFIG = Path(__file__).resolve().parents[3] / "nanobot" / "config" / "goslo_config.json"


def setup_config(force: bool = False) -> Path:
    """Ensure the GOSLO nanobot config exists. Returns path to config.json."""
    config_file = GOSLO_NANOBOT_DIR / "config.json"

    if force or not config_file.exists():
        GOSLO_NANOBOT_DIR.mkdir(parents=True, exist_ok=True)

        if not FORK_CONFIG.exists():
            print(f"ERROR: Config template not found at {FORK_CONFIG}")
            sys.exit(1)

        config = json.loads(FORK_CONFIG.read_text(encoding="utf-8"))

        gemini_key = (os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")).strip()
        if gemini_key:
            config.setdefault("providers", {}).setdefault("gemini", {})["apiKey"] = gemini_key

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if telegram_token:
            config.setdefault("channels", {}).setdefault("telegram", {})["token"] = telegram_token

        github_token = os.getenv("GITHUB_TOKEN", "").strip()
        if github_token:
            servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
            servers.setdefault("github", {}).setdefault("env", {})["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token

        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config written to {config_file}")
    else:
        print(f"Using existing config at {config_file}")

    return config_file


def run_gateway_with_mode_hook(config_file: Path, enable_mode_hook: bool = True) -> None:
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
    logging.basicConfig(level=logging.DEBUG)

    set_config_path(config_file)
    config = load_config(config_file)
    config.agents.defaults.workspace = str(GOSLO_WORKSPACE)

    if not GOSLO_WORKSPACE.exists():
        print(f"ERROR: GOSLO workspace not found at {GOSLO_WORKSPACE}")
        print("  Create it with SOUL.md, AGENTS.md, USER.md")
        sys.exit(1)

    print(f"\n=== GOSLO Chat Bot (ParrotSoul) ===")
    print(f"  Config:    {config_file}")
    print(f"  Workspace: {GOSLO_WORKSPACE}")
    print(f"  Mode hook: {'enabled' if enable_mode_hook else 'disabled'}")
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
    args = parser.parse_args()

    config_file = setup_config(force=args.force_config)
    run_gateway_with_mode_hook(config_file, enable_mode_hook=not args.no_mode_hook)


if __name__ == "__main__":
    main()
