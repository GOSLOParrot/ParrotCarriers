# nanobot: Ultra-Lightweight Personal AI Assistant

## Description
**nanobot** is an ultra-lightweight, extensible personal AI assistant. Inspired by OpenClaw but implemented with 99% fewer lines of code, it acts as a central brain that connects multiple Large Language Models (LLMs) to various chat platforms (Telegram, Discord, WeChat, Feishu, etc.). It supports tool usage, Model Context Protocol (MCP), token-based memory consolidation, scheduled tasks (Cron), and an interactive CLI. 

**When to Use This Documentation:**
*   You need to configure `nanobot` to connect to a new messaging channel (e.g., WhatsApp, Discord, Slack, Feishu).
*   You want to understand how to route different LLM providers (OpenAI, Anthropic, OpenRouter) to the agent.
*   You are troubleshooting configuration issues in `~/.nanobot/config.json`.
*   You need to review CLI commands for deployment, login, and gateway management.
*   You are debugging memory, provider, or streaming lifecycle hooks based on recent repository releases.

---

## Table of Contents
1. [Quick Reference & Code Examples](#quick-reference--code-examples)
2. [Key Concepts](#key-concepts)
3. [Practical Usage Guidance](#practical-usage-guidance)
4. [Known Issues & Troubleshooting](#known-issues--troubleshooting)
5. [Available References](#available-references)

---

## Quick Reference & Code Examples

Here are the most practical examples for installing, configuring, and extending `nanobot`. Configuration is managed primarily in `~/.nanobot/config.json`.

### 1. Installation & Initialization
Install via `uv` or `pip`, then run the onboarding wizard.
```bash
# Install via pip
pip install -U nanobot-ai

# Start the interactive setup wizard
nanobot onboard --wizard

# Start an interactive CLI chat session
nanobot agent
```

### 2. Base Configuration (Provider & Model)
Configure your LLM provider and default model in `~/.nanobot/config.json`.
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

### 3. Starting the Chat Gateway
When connecting nanobot to messaging apps (Telegram, Discord, WhatsApp), you must run the gateway.
```bash
# Start the gateway daemon to listen for channel messages
nanobot gateway
```

### 4. Telegram Channel Configuration
Set up Telegram using a Bot Token from `@BotFather`.
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

### 5. Discord Channel Configuration
Configure Discord with strict mentioning rules to avoid spamming groups.
```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"],
      "groupPolicy": "mention"
    }
  }
}
```

### 6. WhatsApp Login
WhatsApp requires node.js and a QR code scan.
```bash
# Terminal 1: Generate QR code and link device
nanobot channels login whatsapp

# Terminal 2: Run the gateway
nanobot gateway
```

### 7. Feishu (Lark) Channel Configuration
Feishu uses a WebSocket long connection (no public IP required). Enable `streaming` for token-by-token replies (requires `cardkit:card:write` permission).
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "allowFrom": ["ou_YOUR_OPEN_ID"],
      "groupPolicy": "mention",
      "streaming": true
    }
  }
}
```

### 8. Running Multiple Instances
Use the `--dir` flag to run completely isolated instances of nanobot.
```bash
# Initialize a secondary bot in a specific directory
nanobot onboard --dir ~/.nanobot-work

# Run the gateway for the secondary bot
nanobot --dir ~/.nanobot-work gateway
```

---

## Key Concepts

*   **Architecture De-coupling:** As of `v0.1.4.post6`, nanobot uses native `openai` and `anthropic` SDKs (removing the `litellm` dependency) for better prompt cache optimization, reasoning token management (e.g., OpenAI o1/o3), and Gemini thought signatures.
*   **Channels:** The abstraction layer that connects nanobot to user platforms. Supported channels include CLI, Telegram, Discord, Matrix, WhatsApp, Feishu, Slack, DingTalk, QQ, Email, WeCom, and WeChat.
*   **Gateway:** The process (`nanobot gateway`) responsible for maintaining WebSocket/Long-polling connections to external channels and routing inbound messages to the agent.
*   **Memory Consolidation:** To keep context lightweight, `nanobot` automatically consolidates memory (running async background tasks) based on token usage. 
*   **Tools & MCP (Model Context Protocol):** `nanobot` supports native tools (filesystem, shell execution, web search) and connects to external MCP servers to extend its capabilities safely.

---

## Practical Usage Guidance

### 1. File Structure & Path Management
*   **Config Directory:** By default, configuration, state, and memory live in `~/.nanobot/`.
*   **Config File:** Always validate `~/.nanobot/config.json` when adding new channels. Ensure JSON syntax is strictly valid.
*   **Workspace Guard:** If you use the shell/exec tools, nanobot has strict guards against home-expanded (`~`) paths to prevent destructive actions.

### 2. Provider Routing
*   Auto-detection is the default: if `provider` is omitted from `agents.defaults`, nanobot routes the model based on the prefix. 
*   **Cost & Cache Optimization:** If using Anthropic, prompt caching is handled natively. Ensure you match the correct model strings (e.g., `claude-3-5-sonnet-latest`).

### 3. Channel Access Control
Always enforce the `allowFrom` array in your channel configs! 
*   Use `["YOUR_USER_ID"]` to restrict bot usage to yourself. 
*   Use `["*"]` *only* if you want the bot to be publicly accessible.
*   For groups, control chattiness using `"groupPolicy": "mention"`.

---

## Known Issues & Troubleshooting

*   **WhatsApp Bridge Errors:** If upgrading `nanobot-ai` versions, WhatsApp users must delete their local bridge and re-login:
    `rm -rf ~/.nanobot/bridge && nanobot channels login whatsapp`
*   **WeChat/Weixin Output Limiting:** Mentioned in GitHub issue `#2772` — WeChat limits message returns. Use the latest `v0.1.4.post6` version for the fully integrated WeChat plugin which supports HTTP long-poll.
*   **Tool Calling Output Only Text:** If the bot isn't utilizing tools properly (Issue `#2775`), ensure that you are using a provider model that explicitly supports structured tool calling (e.g., top-tier Claude, OpenAI, or Gemini models).
*   **Email Channel Security:** Older versions had an email injection vulnerability. Always use `v0.1.4.post6` or newer, which enforces SPF/DKIM verification by default and encapsulates email content in `[EMAIL-CONTEXT]` to prevent prompt injection.

---

## Available References

When interacting with the repository structure, refer to the following underlying source paths:
*   `references/README.md` - Complete capability matrices and integration guides.
*   `references/releases.md` - Detailed changelogs (especially for `v0.1.4.post5` and `v0.1.4.post6` architectural changes).
*   `references/issues.md` - Ongoing community bugs and feature requests.
*   `references/file_structure.md` - Complete layout of Python modules (`nanobot/channels`, `nanobot/providers`, `nanobot/tools`).
