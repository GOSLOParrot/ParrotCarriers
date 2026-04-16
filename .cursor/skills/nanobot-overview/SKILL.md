---
name: nanobot-overview
description: Use when researching nanobot upstream architecture (agent loop, spawn subagent, cron, memory consolidation, Python SDK, HKUDS/nanobot)
---

# nanobot Codebase Documentation

This documentation provides an in-depth analysis of the `nanobot` codebase, generated through automated code analysis. It offers a structured overview of the project's architecture, design patterns, core functionalities, and usage examples, making it easier to understand and interact with the nanobot project internals.

## Description

This skill offers a comprehensive analysis of the local `nanobot` codebase. It presents organized documentation derived directly from source code, covering various aspects from architectural design to specific implementation details.

**Path:** `C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228`
**Analysis Depth:** surface
**Files Analyzed:** 0
**Languages:** Python (primarily)

## When to Use This Skill

Use this documentation skill when you need to:
- Understand the `nanobot` codebase architecture and design patterns.
- Find implementation examples and usage patterns within the `nanobot` project.
- Review API documentation extracted directly from the `nanobot` source code.
- Check configuration patterns and best practices employed in `nanobot`.
- Explore test examples for real-world usage of `nanobot` components.
- Navigate the `nanobot` codebase structure efficiently.

## Table of Contents

*   [Description](#description)
*   [When to Use This Skill](#when-to-use-this-skill)
*   [Key Concepts](#key-concepts)
*   [鈿?Quick Reference - Code Examples](#鈿?quick-reference---code-examples)
*   [Codebase Statistics](#codebase-statistics)
*   [馃帹 Design Patterns Detected](#馃帹-design-patterns-detected)
*   [鈿欙笍 Configuration Patterns](#鈿欙笍-configuration-patterns)
*   [馃摉 Project Documentation](#馃摉-project-documentation)
*   [馃摎 Available References](#馃摎-available-references)
*   [Practical Usage Guidance for Gemini](#practical-usage-guidance-for-gemini)

## Key Concepts

The `nanobot` codebase, a lightweight personal AI assistant, revolves around several core concepts that are critical for understanding its design and operation. For effective interaction, prioritize understanding the following components and their associated files/symbols:

### Core Agent Loop
The heart of `nanobot`'s intelligence, managing the interaction between the Language Model (LLM) and various tools.
-   `agent/loop.py`: Implements the main LLM 鈫?tool execution cycle.
-   `agent/context.py`: Responsible for building and managing the prompt context for the LLM.
-   `agent/memory.py`: Handles the persistent memory mechanisms.
-   `agent/tools/`: Contains definitions for built-in tools, including the `spawn` tool for subagent creation.

### Configuration
How `nanobot` is configured and customized for different environments and providers.
-   `config/schema.py`: Defines the data schemas for `ProvidersConfig` and `AgentsConfig`.
-   `~/.nanobot/config.json`: The primary runtime configuration file for nanobot instances.
-   `providers/registry.py`: Manages the registration and specifications (`ProviderSpec`) of various LLM providers.

### Subagent / Background Execution
Enables `nanobot` to delegate tasks or run processes in the background.
-   `spawn` tool: Allows the main agent to create and manage subagents.
-   Multiple instances: Supports running several `nanobot` instances, often identified by a `--name` flag.
-   Workspace sandboxing: Each instance operates within a sandboxed workspace for isolation.

### Task Scheduling
Manages periodic and one-time tasks within `nanobot`.
-   `cron` module: Provides functionality for scheduled tasks.
-   `nanobot cron add` / `list` / `remove`: CLI commands for managing cron jobs.
-   Natural language task scheduling: Agents can interpret and schedule tasks from user prompts.

### Memory
How `nanobot` stores and retrieves information across sessions.
-   `memory/MEMORY.md`: A markdown file used for storing long-term, persistent memory.
-   `memory/HISTORY.md`: Stores conversational history.
-   Memory consolidation patterns: Mechanisms for summarizing and archiving older conversation parts to manage context window limits.

### Channel Adapters (Chat Apps)
The modules that allow `nanobot` to communicate with various chat platforms.
-   `channels/`: Directory containing channel implementations (e.g., Telegram, Discord, WhatsApp, Feishu, Slack, DingTalk, QQ, Email, Matrix).
-   `ChannelAdapter`: The base pattern for integrating new chat platforms.
-   `Gateway`: The HTTP server that orchestrates communication with channels.

### Python SDK
Enables embedding `nanobot`'s functionalities within other Python applications.
-   `from nanobot import ...`: Allows importing and using `nanobot` components as a library, without relying on the CLI or gateway.

### Tool System
The framework for extending `nanobot`'s capabilities through external functions.
-   Built-in tools: Includes tools like `github`, `weather`, `web search`, `tmux`.
-   Compatible with OpenClaw skills: Designed to integrate with skills from the OpenClaw ecosystem.
-   MCP integration: Support for the Model Context Protocol.

## 鈿?Quick Reference - Code Examples

Here are 5 practical code examples extracted from the `nanobot` codebase, demonstrating common workflows and key functionalities.

### Provider Request Payload Preparation (Azure OpenAI)

This example shows how `nanobot` prepares a request payload for the Azure OpenAI provider, including handling messages, max tokens, temperature, and tools. It highlights compliance with specific API versions.

```python
'Test request payload preparation with Azure OpenAI 2024-10-21 compliance.'
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
messages = [{'role': 'user', 'content': 'Hello'}]
payload = provider._prepare_request_payload('gpt-4o', messages, max_tokens=1500, temperature=0.8)
assert payload['messages'] == messages
assert payload['max_completion_tokens'] == 1500
assert payload['temperature'] == 0.8
assert 'tools' not in payload
tools = [{'type': 'function', 'function': {'name': 'get_weather', 'parameters': {}}}]
payload_with_tools = provider._prepare_request_payload('gpt-4o', messages, tools=tools)
assert payload_with_tools['tools'] == tools
assert payload_with_tools['tool_choice'] == 'auto'
payload_with_reasoning = provider._prepare_request_payload('gpt-5-chat', messages, reasoning_effort='medium')
assert payload_with_reasoning['reasoning_effort'] == 'medium'
assert 'temperature' not in payload_with_reasoning
```

### Parsing Streaming Chunks (Gemini Compatibility)

This example demonstrates how `nanobot`'s OpenAI compatibility layer parses streaming chunks from an SDK response, specifically preserving `extra_content` for Gemini-like tool calls.

```python
fn_delta = SimpleNamespace(name='get_weather', arguments='{"city":"Tokyo"}')
tc_delta = SimpleNamespace(id='call_1', index=0, function=fn_delta, extra_content=GEMINI_EXTRA)
delta = SimpleNamespace(content=None, tool_calls=[tc_delta])
choice = SimpleNamespace(finish_reason='tool_calls', delta=delta)
chunk = SimpleNamespace(choices=[choice], usage=None)
result = OpenAICompatProvider._parse_chunks([chunk])
assert len(result.tool_calls) == 1
tc = result.tool_calls[0]
assert tc.extra_content == GEMINI_EXTRA
payload = tc.to_openai_tool_call()
assert payload['extra_content'] == GEMINI_EXTRA
```

### Onboarding with Explicit Configuration and Workspace Paths

This workflow illustrates how `nanobot`'s `onboard` command handles explicit configuration and workspace paths, ensuring proper initialization and template syncing.

```python
config_path = tmp_path / 'instance' / 'config.json'
workspace_path = tmp_path / 'workspace'
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
result = runner.invoke(app, ['onboard', '--config', str(config_path), '--workspace', str(workspace_path)])
assert result.exit_code == 0
saved = Config.model_validate(json.loads(config_path.read_text(encoding='utf-8')))
assert saved.workspace_path == workspace_path
assert (workspace_path / 'AGENTS.md').exists()
stripped_output = _strip_ansi(result.stdout)
compact_output = stripped_output.replace('\n', '')
resolved_config = str(config_path.resolve())
assert resolved_config in compact_output
assert f'--config {resolved_config}' in compact_output
```

### Gateway Using Workspace from Configuration by Default

This example demonstrates how the `nanobot gateway` command loads the workspace path from the configuration file if not explicitly overridden by a CLI flag.

```python
config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda path: seen.__setitem__('config_path', path))
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda path: seen.__setitem__('workspace', path))
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['config_path'] == config_file.resolve()
assert seen['workspace'] == Path(config.agents.defaults.workspace)
```

### Migrating Legacy Cron Store

This workflow shows how `nanobot` migrates a legacy global `jobs.json` file into the new workspace-specific cron store on its first run, ensuring backward compatibility and proper file organization.

```python
'Legacy global jobs.json is moved into the workspace on first run.'
from nanobot.cli.commands import _migrate_cron_store
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
legacy_file = legacy_dir / 'jobs.json'
legacy_file.write_text('{"jobs": []}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'workspace')
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
with patch('nanobot.config.paths.get_cron_dir', return_value=legacy_dir):
    _migrate_cron_store(config)
assert workspace_cron.exists()
assert workspace_cron.read_text() == '{"jobs": []}'
assert not legacy_file.exists()
```

## Codebase Statistics

**Languages:** Python (primary)
**Analysis Performed:**
-   鉁?API Reference (C2.5)
-   鉁?Dependency Graph (C2.6)
-   鉁?Design Patterns (C3.1)
-   鉁?Test Examples (C3.2)
-   鉁?Configuration Patterns (C3.4)
-   鉁?Architectural Analysis (C3.7)
-   鉁?Project Documentation (C3.9)

## 馃帹 Design Patterns Detected

*From C3.1 codebase analysis (confidence > 0.7)*

-   **Builder**: 4 instances
-   **Adapter**: 2 instances

*Total: 5 high-confidence patterns*

*See `references/patterns/` for complete pattern analysis*

## 鈿欙笍 Configuration Patterns

*From C3.4 configuration analysis*

This skill analyzed **6 configuration files** containing a total of **89 settings**. While no specific high-confidence patterns were detected, the analysis categorizes the types and purposes of these files:

**Configuration Files Analyzed:**
-   `docker-compose.yml`: yaml, docker_configuration (21 settings)
-   `Dockerfile`: dockerfile, docker_configuration (0 settings)
-   `pyproject.toml`: toml, package_configuration (34 settings)
-   `.github\workflows\ci.yml`: yaml, ci_cd_configuration (6 settings)
-   `bridge\package.json`: json, package_configuration (16 settings)
-   `bridge\tsconfig.json`: json, typescript_configuration (12 settings)

**Total Settings:** 89
**Patterns Detected:** 0 (specific formal patterns)
**Configuration Types:** yaml, dockerfile, toml, json, typescript_configuration

*See `references/config_patterns/` for detailed configuration analysis*

## 馃摉 Project Documentation

*Extracted from markdown files in the project (C3.9)*

The `nanobot` project includes **20 documentation files** categorized for various purposes:

### Overview
-   **COMMUNICATION.md** (`COMMUNICATION.md`)
-   **README.md** (`README.md`)

### Contributing
-   **CONTRIBUTING.md** (`CONTRIBUTING.md`)

### Other
-   **CHANNEL_PLUGIN_GUIDE.md** (`docs\CHANNEL_PLUGIN_GUIDE.md`)
-   **SKILL.md** (`nanobot\skills\clawhub\SKILL.md`)
-   **SKILL.md** (`nanobot\skills\cron\SKILL.md`)
-   **SKILL.md** (`nanobot\skills\github\SKILL.md`)
-   **SKILL.md** (`nanobot\skills\memory\SKILL.md`)
-   *...and 5 more files covering various skills.*

### Security
-   **SECURITY.md** (`SECURITY.md`)

### Templates
-   **AGENTS.md** (`nanobot\templates\AGENTS.md`)
-   **HEARTBEAT.md** (`nanobot\templates\HEARTBEAT.md`)
-   **MEMORY.md** (`nanobot\templates\memory\MEMORY.md`)
-   **SOUL.md** (`nanobot\templates\SOUL.md`)
-   **TOOLS.md** (`nanobot\templates\TOOLS.md`)
-   *...and 1 more template file.*

*See `references/documentation/` for all project documentation*

## 馃摎 Available References

This skill includes detailed reference documentation, organized into specific directories for targeted information retrieval:

-   **Dependencies**: `references/dependencies/` - Detailed dependency graph and analysis.
-   **Patterns**: `references/patterns/` - Explanations and instances of detected design patterns.
-   **Examples**: `references/test_examples/` - Comprehensive usage examples extracted from tests, including "How-To Guides".
-   **Configuration**: `references/config_patterns/` - In-depth analysis of configuration files and settings.
-   **Documentation**: `references/documentation/` - All project documentation files, including guides and overviews.

## Practical Usage Guidance for Gemini

When interacting with this documentation about the `nanobot` codebase, Gemini should prioritize the following areas, especially when operating in a context like ParrotCarriers:

1.  **Agent Loop Design (`agent/loop.py`)**: Focus on the core LLM 鈫?tool execution cycle. This is a primary reference for understanding how `nanobot` workers are designed and can inform the design of your own `nanobot`-based worker processes.

2.  **Subagent Creation (`spawn` tool)**: Pay close attention to patterns for creating background workers from the main agent. This is crucial for understanding how `nanobot` can manage concurrent or delegated tasks.

3.  **Task Scheduling (`cron` module)**: Use the `cron` module as a reference for implementing scheduled tasks, such as heartbeats or memory consolidation routines, within your own system.

4.  **Persistent Memory Management (`memory.py`)**: Analyze how `nanobot` manages its persistent memory. While you might use a different underlying technology (e.g., Graphiti), the lifecycle patterns for storing and retrieving information are highly relevant.

5.  **Python SDK Usage**: Remember that for integration purposes (like ParrotCarriers), `nanobot` is expected to be embedded as a library (`from nanobot import ...`), not primarily used via its CLI gateway. Focus on the SDK-level interactions.

6.  **Channel Adapters (Exclusion)**: **Crucially, for a context like ParrotCarriers, you should largely disregard `nanobot`'s built-in channel adapters (Telegram, Discord, etc.). Your primary communication channel is assumed to be LiveKit Room, and `nanobot`'s internal channel mechanisms are not directly applicable.**

Leverage the "How-To Guides" within `references/test_examples/` for step-by-step explanations of specific workflows, and consult `references/documentation/` for broader context and conceptual understanding.

Generated by Skill Seeker | Codebase Analyzer with C3.x Analysis
