"""
Google Workspace OAuth 认证脚本
用途：替代 nanobot/mcp-inspector，直接用 Python 完成 OAuth2 授权
      生成的 token 存放位置与 @aaronsb/google-workspace-mcp 兼容

用法：python scripts/google_oauth.py
"""
import json
import os
import sys
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

# ----- 运行 OAuth flow -----
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import google.oauth2.credentials
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
# Python 格式（google-auth-library-python standard）
token_data_py = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    "universe_domain": "googleapis.com",
    "account": "",
    "expiry": creds.expiry.isoformat() if creds.expiry else None,
}

# Node.js 格式（@aaronsb/google-workspace-mcp 期望的格式）
import time
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

print(f"\n[SAVED] Token files:")
print(f"  Python: {py_path}")
print(f"  Node:   {node_path}")
print(f"\n[NEXT] ECS install commands:")
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
