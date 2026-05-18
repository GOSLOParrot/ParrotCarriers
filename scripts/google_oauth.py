"""
Google Workspace OAuth 认证脚本
用途：替代 nanobot/mcp-inspector，直接用 Python 完成 OAuth2 授权
      生成的 token 存放位置与 @aaronsb/google-workspace-mcp 兼容

用法：python scripts/google_oauth.py
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# ----- 读取凭证 -----
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

if not CLIENT_ID or not CLIENT_SECRET:
    # 尝试从 .env 手动读取
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8-sig", errors="replace")
        for line in env_text.splitlines():
            if line.startswith("GOOGLE_CLIENT_ID="):
                CLIENT_ID = line.split("=", 1)[1].strip().strip('"')
            elif line.startswith("GOOGLE_CLIENT_SECRET="):
                CLIENT_SECRET = line.split("=", 1)[1].strip().strip('"')

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET 未设置")
    print("请在 .env 里填好，或者设置环境变量后重跑")
    sys.exit(1)

print(f"CLIENT_ID: {CLIENT_ID[:30]}...")

# ----- OAuth 配置 -----
# 与 @aaronsb/google-workspace-mcp 使用的 scope 保持一致
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# ----- token 保存路径（Windows: %APPDATA%\google-workspace-mcp\credentials\） -----
if sys.platform == "win32":
    creds_dir = Path(os.environ.get("APPDATA", "")) / "google-workspace-mcp" / "credentials"
else:
    creds_dir = Path.home() / ".local" / "share" / "google-workspace-mcp" / "credentials"
creds_dir.mkdir(parents=True, exist_ok=True)

print(f"Token 将保存到: {creds_dir}")


def _email_slug(email: str) -> str:
    safe = email.replace("/", "").replace("\\", "")
    return safe.replace("@", "_at_").replace(".", "_dot_")


def _discover_account_email(creds) -> str:
    env_email = os.getenv("GOOGLE_WORKSPACE_ACCOUNT_EMAIL", "") or os.getenv("GOOGLE_ACCOUNT_EMAIL", "")
    if "@" in env_email:
        return env_email.strip()
    try:
        request = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {creds.token}"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        email = str(payload.get("email", "")).strip()
        return email if "@" in email else ""
    except Exception as exc:
        print(f"[WARN] Could not discover Google account email: {exc}")
        return ""


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_mcp_native_state(account_email: str, creds, scopes: list[str]) -> tuple[Path, Path] | None:
    if not account_email:
        return None
    config_base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    data_base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    config_dir = config_base / "google-workspace-mcp"
    native_creds_dir = data_base / "google-workspace-mcp" / "credentials"
    accounts_path = config_dir / "accounts.json"
    credential_path = native_creds_dir / f"{_email_slug(account_email)}.json"

    try:
        accounts_data = json.loads(accounts_path.read_text(encoding="utf-8")) if accounts_path.exists() else {"accounts": []}
    except Exception:
        accounts_data = {"accounts": []}
    accounts = accounts_data.setdefault("accounts", [])
    if not any(account.get("email") == account_email for account in accounts):
        accounts.append(
            {
                "email": account_email,
                "category": "personal",
                "description": "ParrotCarriers Google Workspace account",
            }
        )
    _write_json(accounts_path, accounts_data)
    _write_json(
        credential_path,
        {
            "type": "authorized_user",
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "refresh_token": creds.refresh_token,
            "scopes": scopes,
        },
    )
    return accounts_path, credential_path

# ----- 运行 OAuth flow -----
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Installing google-auth-oauthlib...")
    os.system(f"{sys.executable} -m pip install google-auth-oauthlib --quiet")
    from google_auth_oauthlib.flow import InstalledAppFlow

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

print(f"Token dir: {creds_dir}")

print("\nStarting OAuth flow...")
print("Browser will open (or copy the URL below)\n")

# 启动本地 server，浏览器会打开授权页面
creds = flow.run_local_server(
    port=0,                        # 随机端口，避免冲突
    prompt="consent",
    access_type="offline",
    open_browser=True,
)

print("\n[OK] Authorization complete!")
print(f"  Token: {creds.token[:30]}...")

# ----- 保存 token -----
account_email = _discover_account_email(creds)
if account_email:
    print(f"  Account: {account_email}")
else:
    print("  Account: <unknown> (set GOOGLE_WORKSPACE_ACCOUNT_EMAIL if ECS Nanobot needs MCP native state)")

# Python 格式（google-auth-library-python standard）
token_data_py = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    "universe_domain": "googleapis.com",
    "account": account_email,
    "expiry": creds.expiry.isoformat() if creds.expiry else None,
}

# Legacy Node.js compatibility receipt used by Parrot Web credential fallback.
token_data_node = {
    "access_token": creds.token,
    "refresh_token": creds.refresh_token,
    "scope": " ".join(SCOPES),
    "token_type": "Bearer",
    "expiry_date": int(time.time() * 1000) + 3600 * 1000,
}

# 保存两种格式
py_path = creds_dir / "credentials_python.json"
node_path = creds_dir / "credentials.json"

py_path.write_text(json.dumps(token_data_py, indent=2))
node_path.write_text(json.dumps(token_data_node, indent=2))
native_paths = _write_mcp_native_state(account_email, creds, token_data_py["scopes"])

print("\n[SAVED] Token files:")
print(f"  Python: {py_path}")
print(f"  Node:   {node_path}")
if native_paths:
    print(f"  MCP accounts: {native_paths[0]}")
    print(f"  MCP credential: {native_paths[1]}")
print("\n[NEXT] ECS install commands:")
print(
    "  ssh root@<ECS_IP> "
    "\"install -d -m 700 -o parrot -g parrot "
    "/home/parrot/.nanobot/google-workspace-credentials\""
)
print(
    f'  scp "{py_path}" "{node_path}" '
    "root@<ECS_IP>:/tmp/"
)
print(
    "  ssh root@<ECS_IP> "
    "\"install -m 600 -o parrot -g parrot "
    "/tmp/credentials_python.json "
    "/home/parrot/.nanobot/google-workspace-credentials/credentials_python.json && "
    "install -m 600 -o parrot -g parrot "
    "/tmp/credentials.json "
    "/home/parrot/.nanobot/google-workspace-credentials/credentials.json && "
    "rm -f /tmp/credentials_python.json /tmp/credentials.json\""
)
print(
    "  ssh root@<ECS_IP> "
    "\"systemctl restart parrot-maid\""
)
