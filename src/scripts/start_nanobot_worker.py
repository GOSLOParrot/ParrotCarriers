"""Start the Nanobot worker with ParrotCarriers Bus + WeChat channels.

Usage:
  python src/scripts/start_nanobot_worker.py            # use real nanobot gateway
  python src/scripts/start_nanobot_worker.py --stub      # use stub consumer (no LLM)
  python src/scripts/start_nanobot_worker.py --no-weixin # disable WeChat channel

This script:
  1. Resolves the parrot_config.json from the nanobot fork
  2. Injects OPENROUTER_API_KEY into the config if set
  3. Starts the nanobot gateway with parrot_bus + weixin channels

Prerequisites:
  - Redis running (docker compose -f infra/docker-compose.dev.yml up -d)
  - nanobot installed: pip install -e ../nanobot[parrot]
  - OPENROUTER_API_KEY set (or edit ~/.nanobot-parrot/config.json manually)
  - For WeChat: run 'nanobot channels login weixin' first to scan QR code
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PARROT_NANOBOT_DIR = Path.home() / ".nanobot-parrot"
FORK_CONFIG = Path(__file__).resolve().parents[3] / "nanobot" / "config" / "parrot_config.json"
GOOGLE_WORKSPACE_SERVER_KEY = "google_workspace"
LEGACY_GOOGLE_WORKSPACE_SERVER_KEY = "google-workspace"
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


def _load_fork_config() -> dict[str, Any]:
    if not FORK_CONFIG.exists():
        print(f"ERROR: Config template not found at {FORK_CONFIG}")
        sys.exit(1)
    return _read_json(FORK_CONFIG)


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
    """Bridge Parrot's OAuth export into @aaronsb/google-workspace-mcp layout."""
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

    credential_path = (
        _google_workspace_data_dir()
        / "credentials"
        / f"{_email_slug(email)}.json"
    )
    if _write_json_if_changed(credential_path, native_credential):
        print(f"Google Workspace MCP credential written to {credential_path}")


def _sync_google_workspace_config(
    config: dict[str, Any],
    template_config: dict[str, Any],
) -> bool:
    servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    template_servers = template_config.get("tools", {}).get("mcpServers", {})
    template_google = template_servers.get(GOOGLE_WORKSPACE_SERVER_KEY)
    if not template_google:
        return False

    existing = servers.get(GOOGLE_WORKSPACE_SERVER_KEY) or {}
    legacy = servers.pop(LEGACY_GOOGLE_WORKSPACE_SERVER_KEY, None)
    if legacy:
        existing = {**legacy, **existing}

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

    merged["env"] = merged_env
    changed = servers.get(GOOGLE_WORKSPACE_SERVER_KEY) != merged or legacy is not None
    servers[GOOGLE_WORKSPACE_SERVER_KEY] = merged
    return changed


def setup_config(force: bool = False, enable_weixin: bool = True) -> Path:
    """Ensure the nanobot parrot config exists. Returns path to config.json."""
    config_file = PARROT_NANOBOT_DIR / "config.json"
    template_config = _load_fork_config()

    if force or not config_file.exists():
        PARROT_NANOBOT_DIR.mkdir(parents=True, exist_ok=True)

        config = json.loads(json.dumps(template_config))

        gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        if gemini_key:
            config.setdefault("providers", {}).setdefault("gemini", {})["apiKey"] = gemini_key

        redis_url = os.getenv("REDIS_URL", "")
        if redis_url:
            config.setdefault("channels", {}).setdefault("parrot_bus", {})["redisUrl"] = redis_url

        github_token = os.getenv("GITHUB_TOKEN", "")
        if github_token:
            servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
            servers.setdefault("github", {}).setdefault("env", {})["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token

        # Google Workspace MCP is enabled by default in parrot_config.json.
        # Bridge Parrot's OAuth export into MCP's account registry on startup.
        servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
        if GOOGLE_WORKSPACE_SERVER_KEY in servers:
            servers[GOOGLE_WORKSPACE_SERVER_KEY].setdefault("env", {})

        if not enable_weixin:
            channels = config.get("channels", {})
            if "weixin" in channels:
                channels["weixin"]["enabled"] = False

        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config written to {config_file}")
    else:
        print(f"Using existing config at {config_file}")
        try:
            config = _read_json(config_file)
        except Exception as exc:
            print(f"ERROR: Could not read existing config at {config_file}: {exc}")
            sys.exit(1)

    changed = _sync_google_workspace_config(config, template_config)

    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if gemini_key:
        providers = config.setdefault("providers", {}).setdefault("gemini", {})
        if providers.get("apiKey") != gemini_key:
            providers["apiKey"] = gemini_key
            changed = True

    redis_url = os.getenv("REDIS_URL", "")
    if redis_url:
        parrot_bus = config.setdefault("channels", {}).setdefault("parrot_bus", {})
        if parrot_bus.get("redisUrl") != redis_url:
            parrot_bus["redisUrl"] = redis_url
            changed = True

    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_token:
        servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
        github_env = servers.setdefault("github", {}).setdefault("env", {})
        if github_env.get("GITHUB_PERSONAL_ACCESS_TOKEN") != github_token:
            github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token
            changed = True

    channels = config.setdefault("channels", {})
    if "weixin" in channels:
        next_weixin = enable_weixin
        if channels["weixin"].get("enabled") != next_weixin:
            channels["weixin"]["enabled"] = next_weixin
            changed = True

    if changed:
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Config updated at {config_file}")

    _ensure_google_workspace_mcp_state()

    return config_file


def run_gateway(config_file: Path, enable_weixin: bool = True) -> None:
    """Start the nanobot gateway subprocess."""
    nanobot_exe = shutil.which("nanobot")
    if nanobot_exe is None:
        print("ERROR: 'nanobot' command not found.")
        print("  Install with: pip install -e ../nanobot[parrot]")
        sys.exit(1)

    channels = ["parrot_bus"]
    if enable_weixin:
        channels.append("weixin")

    print(f"\nStarting nanobot gateway with channels: {', '.join(channels)}")
    print(f"  Config: {config_file}")
    if enable_weixin:
        print("  WeChat: enabled (ensure QR login completed)")
    print()

    subprocess.run(
        [nanobot_exe, "gateway", "--config", str(config_file), "--verbose"],
        check=False,
    )


def run_stub() -> None:
    """Start the built-in stub consumer (no LLM, echo-only)."""
    print("\nStarting Nanobot STUB consumer (no LLM, echo-only)...")
    from parrot.bus.nanobot_consumer import run_nanobot_consumer

    asyncio.run(run_nanobot_consumer())


def main():
    parser = argparse.ArgumentParser(description="Start the Nanobot worker")
    parser.add_argument("--stub", action="store_true", help="Use stub consumer (no LLM)")
    parser.add_argument("--force-config", action="store_true", help="Regenerate config from template")
    # --no-weixin flag: 
    # Use this during P1/dev to run a pure backend Worker (parrot_bus only).
    # Omit this flag and run `nanobot channels login weixin` first if you want Maid to also chat on WeChat.
    parser.add_argument("--no-weixin", action="store_true", help="Disable WeChat channel")
    args = parser.parse_args()

    if args.stub:
        run_stub()
    else:
        enable_weixin = not args.no_weixin
        config_file = setup_config(force=args.force_config, enable_weixin=enable_weixin)
        run_gateway(config_file, enable_weixin=enable_weixin)


if __name__ == "__main__":
    main()
