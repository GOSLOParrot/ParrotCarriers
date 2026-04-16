# Test Example Extraction Report

**Total Examples**: 239  
**High Value Examples** (confidence > 0.7): 239  
**Average Complexity**: 0.35  

## Examples by Category

- **config**: 3
- **instantiation**: 172
- **method_call**: 18
- **workflow**: 46

## Examples by Language

- **Python**: 239

## Extracted Examples

### test_two_tables_split_into_two_groups

**Category**: workflow  
**Description**: Workflow: test two tables split into two groups  
**Expected**: assert t1 not in result[1]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
t1 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'A', 'width': 'auto'}], 'rows': [{'c0': 'table-one'}], 'page_size': 2}
t2 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'B', 'width': 'auto'}], 'rows': [{'c0': 'table-two'}], 'page_size': 2}
els = [_md('before'), t1, _md('between'), t2, _md('after')]
result = split(els)
assert len(result) == 2
assert t1 in result[0]
assert t2 not in result[0]
assert t2 in result[1]
assert t1 not in result[1]
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:56*

### test_list_shows_last_run_state

**Category**: workflow  
**Description**: Workflow: test list shows last run state  
**Expected**: assert '(UTC)' in result  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
job = tool._cron.add_job(name='Stateful job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
job.state.last_run_at_ms = 1773673200000
job.state.last_status = 'ok'
tool._cron._save_store()
result = tool._list_jobs()
assert 'Last run:' in result
assert 'ok' in result
assert '(UTC)' in result
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:218*

### test_list_shows_error_message

**Category**: workflow  
**Description**: Workflow: test list shows error message  
**Expected**: assert 'timeout' in result  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
job = tool._cron.add_job(name='Failed job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
job.state.last_run_at_ms = 1773673200000
job.state.last_status = 'error'
job.state.last_error = 'timeout'
tool._cron._save_store()
result = tool._list_jobs()
assert 'error' in result
assert 'timeout' in result
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:236*

### test_add_at_job_uses_default_timezone_for_naive_datetime

**Category**: workflow  
**Description**: Workflow: test add at job uses default timezone for naive datetime  
**Expected**: assert job.schedule.at_ms == expected  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool_with_tz(tmp_path, 'Asia/Shanghai')
tool.set_context('telegram', 'chat-1')
result = tool._add_job('Morning reminder', None, None, None, '2026-03-25T08:00:00')
assert result.startswith('Created job')
job = tool._cron.list_jobs()[0]
expected = int(datetime(2026, 3, 25, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
assert job.schedule.at_ms == expected
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:276*

### test_prepare_request_payload

**Category**: workflow  
**Description**: Workflow: Test request payload preparation with Azure OpenAI 2024-10-21 compliance.  
**Expected**: assert 'temperature' not in payload_with_reasoning  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:83*

### test_parse_sdk_object_preserves_extra_content

**Category**: workflow  
**Description**: Workflow: test parse sdk object preserves extra content  
**Expected**: assert payload['extra_content'] == GEMINI_EXTRA  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
with patch('nanobot.providers.openai_compat_provider.AsyncOpenAI'):
    provider = OpenAICompatProvider()
result = provider._parse(_make_sdk_response_with_extra_content())
assert len(result.tool_calls) == 1
tc = result.tool_calls[0]
assert tc.name == 'get_weather'
assert tc.extra_content == GEMINI_EXTRA
payload = tc.to_openai_tool_call()
assert payload['extra_content'] == GEMINI_EXTRA
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:80*

### test_parse_dict_preserves_extra_content

**Category**: workflow  
**Description**: Workflow: test parse dict preserves extra content  
**Expected**: assert payload['extra_content'] == GEMINI_EXTRA  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
with patch('nanobot.providers.openai_compat_provider.AsyncOpenAI'):
    provider = OpenAICompatProvider()
response_dict = {'choices': [{'message': {'content': None, 'tool_calls': [{'id': 'call_1', 'type': 'function', 'function': {'name': 'get_weather', 'arguments': '{"city":"Tokyo"}'}, 'extra_content': GEMINI_EXTRA}]}, 'finish_reason': 'tool_calls'}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
result = provider._parse(response_dict)
assert len(result.tool_calls) == 1
tc = result.tool_calls[0]
assert tc.name == 'get_weather'
assert tc.extra_content == GEMINI_EXTRA
payload = tc.to_openai_tool_call()
assert payload['extra_content'] == GEMINI_EXTRA
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:97*

### test_parse_chunks_sdk_preserves_extra_content

**Category**: workflow  
**Description**: Workflow: test parse chunks sdk preserves extra content  
**Expected**: assert payload['extra_content'] == GEMINI_EXTRA  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:130*

### test_parse_chunks_dict_preserves_extra_content

**Category**: workflow  
**Description**: Workflow: test parse chunks dict preserves extra content  
**Expected**: assert payload['extra_content'] == GEMINI_EXTRA  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
chunk = {'choices': [{'finish_reason': 'tool_calls', 'delta': {'content': None, 'tool_calls': [{'index': 0, 'id': 'call_1', 'function': {'name': 'get_weather', 'arguments': '{"city":"Tokyo"}'}, 'extra_content': GEMINI_EXTRA}]}}]}
result = OpenAICompatProvider._parse_chunks([chunk])
assert len(result.tool_calls) == 1
tc = result.tool_calls[0]
assert tc.extra_content == GEMINI_EXTRA
payload = tc.to_openai_tool_call()
assert payload['extra_content'] == GEMINI_EXTRA
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:152*

### test_register_optional_event_calls_supported_method

**Category**: workflow  
**Description**: Workflow: test register optional event calls supported method  
**Expected**: assert called == [handler]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
called = []

class Builder:

    def register_event(self, handler):
        called.append(handler)
        return self
builder = Builder()
handler = object()
same = FeishuChannel._register_optional_event(builder, 'register_event', handler)
assert same is builder
assert called == [handler]
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:63*

### test_onboard_uses_explicit_config_and_workspace_paths

**Category**: workflow  
**Description**: Workflow: test onboard uses explicit config and workspace paths  
**Expected**: assert f'--config {resolved_config}' in compact_output  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:155*

### test_onboard_wizard_preserves_explicit_config_in_next_steps

**Category**: workflow  
**Description**: Workflow: test onboard wizard preserves explicit config in next steps  
**Expected**: assert f'nanobot gateway --config {resolved_config}' in compact_output  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

config_path = tmp_path / 'instance' / 'config.json'
workspace_path = tmp_path / 'workspace'
from nanobot.cli.onboard import OnboardResult
monkeypatch.setattr('nanobot.cli.onboard.run_onboard', lambda initial_config: OnboardResult(config=initial_config, should_save=True))
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {})
result = runner.invoke(app, ['onboard', '--wizard', '--config', str(config_path), '--workspace', str(workspace_path)])
assert result.exit_code == 0
stripped_output = _strip_ansi(result.stdout)
compact_output = stripped_output.replace('\n', '')
resolved_config = str(config_path.resolve())
assert f'nanobot agent -m "Hello!" --config {resolved_config}' in compact_output
assert f'nanobot gateway --config {resolved_config}' in compact_output
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:177*

### test_gateway_uses_workspace_from_config_by_default

**Category**: workflow  
**Description**: Workflow: test gateway uses workspace from config by default  
**Expected**: assert seen['workspace'] == Path(config.agents.defaults.workspace)  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:645*

### test_gateway_workspace_option_overrides_config

**Category**: workflow  
**Description**: Workflow: test gateway workspace option overrides config  
**Expected**: assert config.workspace_path == override  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
override = tmp_path / 'override-workspace'
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda path: seen.__setitem__('workspace', path))
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
result = runner.invoke(app, ['gateway', '--config', str(config_file), '--workspace', str(override)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['workspace'] == override
assert config.workspace_path == override
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:675*

### test_gateway_uses_workspace_directory_for_cron_store

**Category**: workflow  
**Description**: Workflow: test gateway uses workspace directory for cron store  
**Expected**: assert seen['cron_store'] == config.workspace_path / 'cron' / 'jobs.json'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'config-workspace')
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())

class _StopCron:

    def __init__(self, store_path: Path) -> None:
        seen['cron_store'] = store_path
        raise _StopGatewayError('stop')
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['cron_store'] == config.workspace_path / 'cron' / 'jobs.json'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:706*

### test_gateway_workspace_override_does_not_migrate_legacy_cron

**Category**: workflow  
**Description**: Workflow: test gateway workspace override does not migrate legacy cron  
**Expected**: assert not (override / 'cron' / 'jobs.json').exists()  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
legacy_file = legacy_dir / 'jobs.json'
legacy_file.write_text('{"jobs": []}')
override = tmp_path / 'override-workspace'
config = Config()
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())
monkeypatch.setattr('nanobot.config.paths.get_cron_dir', lambda: legacy_dir)

class _StopCron:

    def __init__(self, store_path: Path) -> None:
        seen['cron_store'] = store_path
        raise _StopGatewayError('stop')
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
result = runner.invoke(app, ['gateway', '--config', str(config_file), '--workspace', str(override)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['cron_store'] == override / 'cron' / 'jobs.json'
assert legacy_file.exists()
assert not (override / 'cron' / 'jobs.json').exists()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:735*

### test_gateway_custom_config_workspace_does_not_migrate_legacy_cron

**Category**: workflow  
**Description**: Workflow: test gateway custom config workspace does not migrate legacy cron  
**Expected**: assert not (custom_workspace / 'cron' / 'jobs.json').exists()  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
legacy_file = legacy_dir / 'jobs.json'
legacy_file.write_text('{"jobs": []}')
custom_workspace = tmp_path / 'custom-workspace'
config = Config()
config.agents.defaults.workspace = str(custom_workspace)
seen: dict[str, Path] = {}
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: object())
monkeypatch.setattr('nanobot.bus.queue.MessageBus', lambda: object())
monkeypatch.setattr('nanobot.session.manager.SessionManager', lambda _workspace: object())
monkeypatch.setattr('nanobot.config.paths.get_cron_dir', lambda: legacy_dir)

class _StopCron:

    def __init__(self, store_path: Path) -> None:
        seen['cron_store'] = store_path
        raise _StopGatewayError('stop')
monkeypatch.setattr('nanobot.cron.service.CronService', _StopCron)
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert seen['cron_store'] == custom_workspace / 'cron' / 'jobs.json'
assert legacy_file.exists()
assert not (custom_workspace / 'cron' / 'jobs.json').exists()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:777*

### test_migrate_cron_store_moves_legacy_file

**Category**: workflow  
**Description**: Workflow: Legacy global jobs.json is moved into the workspace on first run.  
**Expected**: assert not legacy_file.exists()  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path

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

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:817*

### test_migrate_cron_store_skips_when_workspace_file_exists

**Category**: workflow  
**Description**: Workflow: Migration does not overwrite an existing workspace cron store.  
**Expected**: assert workspace_cron.read_text() == '{"new": true}'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Migration does not overwrite an existing workspace cron store.'
from nanobot.cli.commands import _migrate_cron_store
legacy_dir = tmp_path / 'global' / 'cron'
legacy_dir.mkdir(parents=True)
(legacy_dir / 'jobs.json').write_text('{"old": true}')
config = Config()
config.agents.defaults.workspace = str(tmp_path / 'workspace')
workspace_cron = config.workspace_path / 'cron' / 'jobs.json'
workspace_cron.parent.mkdir(parents=True)
workspace_cron.write_text('{"new": true}')
with patch('nanobot.config.paths.get_cron_dir', return_value=legacy_dir):
    _migrate_cron_store(config)
assert workspace_cron.read_text() == '{"new": true}'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:838*

### test_gateway_uses_configured_port_when_cli_flag_is_missing

**Category**: workflow  
**Description**: Workflow: test gateway uses configured port when cli flag is missing  
**Expected**: assert 'port 18791' in result.stdout  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

config_file = tmp_path / 'instance' / 'config.json'
config_file.parent.mkdir(parents=True)
config_file.write_text('{}')
config = Config()
config.gateway.port = 18791
monkeypatch.setattr('nanobot.config.loader.set_config_path', lambda _path: None)
monkeypatch.setattr('nanobot.config.loader.load_config', lambda _path=None: config)
monkeypatch.setattr('nanobot.cli.commands.sync_workspace_templates', lambda _path: None)
monkeypatch.setattr('nanobot.cli.commands._make_provider', lambda _config: (_ for _ in ()).throw(_StopGatewayError('stop')))
result = runner.invoke(app, ['gateway', '--config', str(config_file)])
assert isinstance(result.exception, _StopGatewayError)
assert 'port 18791' in result.stdout
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_commands.py:858*

### test_system_prompt_stays_stable_when_clock_changes

**Category**: workflow  
**Description**: Workflow: System prompt should not change just because wall clock minute changes.  
**Expected**: assert prompt1 == prompt2  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

'System prompt should not change just because wall clock minute changes.'
monkeypatch.setattr(datetime_module, 'datetime', _FakeDatetime)
workspace = _make_workspace(tmp_path)
builder = ContextBuilder(workspace)
_FakeDatetime.current = real_datetime(2026, 2, 24, 13, 59)
prompt1 = builder.build_system_prompt()
_FakeDatetime.current = real_datetime(2026, 2, 24, 14, 0)
prompt2 = builder.build_system_prompt()
assert prompt1 == prompt2
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:34*

### test_runtime_context_is_separate_untrusted_user_message

**Category**: workflow  
**Description**: Workflow: Runtime metadata should be merged with the user message.  
**Expected**: assert 'Return exactly: OK' in user_content  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Runtime metadata should be merged with the user message.'
workspace = _make_workspace(tmp_path)
builder = ContextBuilder(workspace)
messages = builder.build_messages(history=[], current_message='Return exactly: OK', channel='cli', chat_id='direct')
assert messages[0]['role'] == 'system'
assert '## Current Session' not in messages[0]['content']
assert messages[-1]['role'] == 'user'
user_content = messages[-1]['content']
assert isinstance(user_content, str)
assert ContextBuilder._RUNTIME_CONTEXT_TAG in user_content
assert 'Current Time:' in user_content
assert 'Channel: cli' in user_content
assert 'Chat ID: direct' in user_content
assert 'Return exactly: OK' in user_content
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:50*

### test_main_menu_interrupt_can_discard_unsaved_session_changes

**Category**: workflow  
**Description**: Workflow: test main menu interrupt can discard unsaved session changes  
**Expected**: assert result.config.model_dump(by_alias=True) == initial_config.model_dump(by_alias=True)  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

initial_config = Config()
responses = iter(['[A] Agent Settings', KeyboardInterrupt(), '[X] Exit Without Saving'])

class FakePrompt:

    def __init__(self, response):
        self.response = response

    def ask(self):
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response

def fake_select(*_args, **_kwargs):
    return FakePrompt(next(responses))

def fake_configure_general_settings(config, section):
    if section == 'Agent Settings':
        config.agents.defaults.model = 'test/provider-model'
monkeypatch.setattr(onboard_wizard, '_show_main_menu_header', lambda: None)
monkeypatch.setattr(onboard_wizard, 'questionary', SimpleNamespace(select=fake_select))
monkeypatch.setattr(onboard_wizard, '_configure_general_settings', fake_configure_general_settings)
result = run_onboard(initial_config=initial_config)
assert result.should_save is False
assert result.config.model_dump(by_alias=True) == initial_config.model_dump(by_alias=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:461*

### test_package_skill_creates_archive

**Category**: workflow  
**Description**: Workflow: test package skill creates archive  
**Expected**: assert 'package-me/scripts/helper.py' in names  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

skill_dir = tmp_path / 'package-me'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('---\nname: package-me\ndescription: Package this skill.\n---\n# Skill\n', encoding='utf-8')
scripts_dir = skill_dir / 'scripts'
scripts_dir.mkdir()
(scripts_dir / 'helper.py').write_text("print('ok')\n", encoding='utf-8')
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
assert archive_path == tmp_path / 'dist' / 'package-me.skill'
assert archive_path.exists()
with zipfile.ZipFile(archive_path, 'r') as archive:
    names = set(archive.namelist())
assert 'package-me/SKILL.md' in names
assert 'package-me/scripts/helper.py' in names
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:77*

### test_package_skill_rejects_symlink

**Category**: workflow  
**Description**: Workflow: test package skill rejects symlink  
**Expected**: assert not (tmp_path / 'dist' / 'symlink-skill.skill').exists()  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

skill_dir = tmp_path / 'symlink-skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('---\nname: symlink-skill\ndescription: Reject symlinks during packaging.\n---\n# Skill\n', encoding='utf-8')
scripts_dir = skill_dir / 'scripts'
scripts_dir.mkdir()
target = tmp_path / 'outside.txt'
target.write_text('secret\n', encoding='utf-8')
link = scripts_dir / 'outside.txt'
try:
    link.symlink_to(target)
except (OSError, NotImplementedError):
    return
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
assert archive_path is None
assert not (tmp_path / 'dist' / 'symlink-skill.skill').exists()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:102*

### test_extract_text_body_falls_back_to_html

**Category**: workflow  
**Description**: Workflow: test extract text body falls back to html  
**Expected**: assert 'world' in text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
msg = EmailMessage()
msg['From'] = 'alice@example.com'
msg['To'] = 'bot@example.com'
msg['Subject'] = 'HTML only'
msg.add_alternative('<p>Hello<br>world</p>', subtype='html')
text = EmailChannel._extract_text_body(msg)
assert 'Hello' in text
assert 'world' in text
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:208*

### test_spoofed_email_rejected_when_verify_enabled

**Category**: workflow  
**Description**: Workflow: An email without Authentication-Results should be rejected when verify_dkim=True.  
**Expected**: assert len(items) == 0, 'Spoofed email without auth headers should be rejected'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

'An email without Authentication-Results should be rejected when verify_dkim=True.'
raw = _make_raw_email(subject='Spoofed', body='Malicious payload')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=True, verify_spf=True)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 0, 'Spoofed email without auth headers should be rejected'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:526*

### test_backward_compat_verify_disabled

**Category**: workflow  
**Description**: Workflow: When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.  
**Expected**: assert len(items) == 1, 'With verification disabled, emails should be accepted as before'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

'When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.'
raw = _make_raw_email(subject='NoAuth', body='No auth headers present')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=False, verify_spf=False)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 1, 'With verification disabled, emails should be accepted as before'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:575*

### test_email_content_tagged_with_email_context

**Category**: workflow  
**Description**: Workflow: Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.  
**Expected**: assert items[0]['content'].startswith('[EMAIL-CONTEXT]'), 'Email content must be tagged with [EMAIL-CONTEXT]'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

'Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.'
raw = _make_raw_email(subject='Tagged', body='Check the tag')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=False, verify_spf=False)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 1
assert items[0]['content'].startswith('[EMAIL-CONTEXT]'), 'Email content must be tagged with [EMAIL-CONTEXT]'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:588*

### test_make_headers_includes_route_tag_when_configured

**Category**: workflow  
**Description**: Workflow: test make headers includes route tag when configured  
**Expected**: assert headers['SKRouteTag'] == '123'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
bus = MessageBus()
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], route_tag=123), bus)
channel._token = 'token'
headers = channel._make_headers()
assert headers['Authorization'] == 'Bearer token'
assert headers['SKRouteTag'] == '123'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:33*

### test_save_and_load_state_persists_context_tokens

**Category**: workflow  
**Description**: Workflow: test save and load state persists context tokens  
**Expected**: assert restored._context_tokens == {'wx-user': 'ctx-1'}  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

bus = MessageBus()
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
channel._token = 'token'
channel._get_updates_buf = 'cursor'
channel._context_tokens = {'wx-user': 'ctx-1'}
channel._save_state()
saved = json.loads((tmp_path / 'account.json').read_text())
assert saved['context_tokens'] == {'wx-user': 'ctx-1'}
restored = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
assert restored._load_state() is True
assert restored._context_tokens == {'wx-user': 'ctx-1'}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:51*

### test_channels_login_uses_discovered_plugin_class

**Category**: workflow  
**Description**: Workflow: test channels login uses discovered plugin class  
**Expected**: assert seen['force'] is True  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

from nanobot.cli.commands import app
from nanobot.config.schema import Config
from typer.testing import CliRunner
runner = CliRunner()
seen: dict[str, object] = {}

class _LoginPlugin(_FakePlugin):
    display_name = 'Login Plugin'

    async def login(self, force: bool=False) -> bool:
        seen['force'] = force
        seen['config'] = self.config
        return True
monkeypatch.setattr('nanobot.config.loader.load_config', lambda: Config())
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'fakeplugin': _LoginPlugin})
result = runner.invoke(app, ['channels', 'login', 'fakeplugin', '--force'])
assert result.exit_code == 0
assert seen['force'] is True
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:195*

### test_exec_extract_absolute_paths_keeps_full_windows_path

**Category**: workflow  
**Description**: Workflow: test exec extract absolute paths keeps full windows path  
**Expected**: assert paths == ['C:\\user\\workspace\\txt']  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
cmd = 'type C:\\user\\workspace\\txt'
paths = ExecTool._extract_absolute_paths(cmd)
assert paths == ['C:\\user\\workspace\\txt']
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:92*

### test_last_consolidated_persistence

**Category**: workflow  
**Description**: Workflow: Test that last_consolidated persists across save/load.  
**Expected**: assert len(session2.messages) == 20  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that last_consolidated persists across save/load.'
manager = SessionManager(Path(tmp_path))
session1 = create_session_with_messages('test:persist', 20)
session1.last_consolidated = 15
manager.save(session1)
session2 = manager.get_or_create('test:persist')
assert session2.last_consolidated == 15
assert len(session2.messages) == 20
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:67*

### test_consolidation_skipped_when_no_new_messages

**Category**: workflow  
**Description**: Workflow: Test consolidation skipped when messages_to_process <= 0.  
**Expected**: assert len(old_messages) == 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test consolidation skipped when messages_to_process <= 0.'
session = create_session_with_messages('test:already_consolidated', 40)
session.last_consolidated = len(session.messages) - KEEP_COUNT
for i in range(40, 42):
    session.add_message('user', f'msg{i}')
total_messages = len(session.messages)
messages_to_process = total_messages - session.last_consolidated
assert messages_to_process > 0
session.last_consolidated = total_messages - KEEP_COUNT
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
assert len(old_messages) == 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:207*

### test_last_consolidated_exceeds_message_count

**Category**: workflow  
**Description**: Workflow: Test behavior when last_consolidated > len(messages) (data corruption).  
**Expected**: assert len(old_messages) == 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test behavior when last_consolidated > len(messages) (data corruption).'
session = create_session_with_messages('test:corruption', 10)
session.last_consolidated = 20
total_messages = len(session.messages)
messages_to_process = total_messages - session.last_consolidated
assert messages_to_process <= 0
old_messages = get_old_messages(session, session.last_consolidated, 5)
assert len(old_messages) == 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:229*

### test_last_consolidated_negative_value

**Category**: workflow  
**Description**: Workflow: Test behavior with negative last_consolidated (invalid state).  
**Expected**: assert old_messages[-1]['content'] == 'msg6'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test behavior with negative last_consolidated (invalid state).'
session = create_session_with_messages('test:negative', 10)
session.last_consolidated = -5
keep_count = 3
old_messages = get_old_messages(session, session.last_consolidated, keep_count)
assert len(old_messages) == 2
assert old_messages[0]['content'] == 'msg5'
assert old_messages[-1]['content'] == 'msg6'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:241*

### test_messages_added_after_consolidation

**Category**: workflow  
**Description**: Workflow: Test correct behavior when new messages arrive after consolidation.  
**Expected**: assert_messages_content(old_messages, 15, 24)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test correct behavior when new messages arrive after consolidation.'
session = create_session_with_messages('test:new_messages', 40)
session.last_consolidated = len(session.messages) - KEEP_COUNT
for i in range(40, 50):
    session.add_message('user', f'msg{i}')
total_messages = len(session.messages)
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
expected_consolidate_count = total_messages - KEEP_COUNT - session.last_consolidated
assert len(old_messages) == expected_consolidate_count
assert_messages_content(old_messages, 15, 24)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:254*

### test_archive_all_vs_normal_consolidation

**Category**: workflow  
**Description**: Workflow: Test difference between archive_all and normal consolidation.  
**Expected**: assert len(session2.messages) == 60  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test difference between archive_all and normal consolidation.'
session1 = create_session_with_messages('test:normal', 60)
session1.last_consolidated = len(session1.messages) - KEEP_COUNT
session2 = create_session_with_messages('test:all', 60)
session2.last_consolidated = 0
assert session1.last_consolidated == 35
assert len(session1.messages) == 60
assert session2.last_consolidated == 0
assert len(session2.messages) == 60
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:305*

### test_consolidation_does_not_modify_messages_list

**Category**: workflow  
**Description**: Workflow: Test that consolidation leaves messages list unchanged.  
**Expected**: assert session.messages == original_messages  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that consolidation leaves messages list unchanged.'
session = create_session_with_messages('test:immutable', 50)
original_messages = session.messages.copy()
original_len = len(session.messages)
session.last_consolidated = original_len - KEEP_COUNT
assert len(session.messages) == original_len
assert session.messages == original_messages
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:324*

### test_consolidation_only_updates_last_consolidated

**Category**: workflow  
**Description**: Workflow: Test that consolidation only updates last_consolidated field.  
**Expected**: assert session.last_consolidated == 35  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that consolidation only updates last_consolidated field.'
session = create_session_with_messages('test:field_only', 60)
original_messages = session.messages.copy()
original_key = session.key
original_metadata = session.metadata.copy()
session.last_consolidated = len(session.messages) - KEEP_COUNT
assert session.messages == original_messages
assert session.key == original_key
assert session.metadata == original_metadata
assert session.last_consolidated == 35
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:348*

### test_session_with_gaps_in_consolidation

**Category**: workflow  
**Description**: Workflow: Test session with potential gaps in consolidation history.  
**Expected**: assert_messages_content(old_messages, 10, 34)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test session with potential gaps in consolidation history.'
session = create_session_with_messages('test:gaps', 50)
session.last_consolidated = 10
for i in range(50, 60):
    session.add_message('user', f'msg{i}')
old_messages = get_old_messages(session, session.last_consolidated, KEEP_COUNT)
expected_count = 60 - KEEP_COUNT - 10
assert len(old_messages) == expected_count
assert_messages_content(old_messages, 10, 34)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:467*

### test_save_config_writes_context_window_tokens_but_not_memory_window

**Category**: workflow  
**Description**: Workflow: test save config writes context window tokens but not memory window  
**Expected**: assert 'memoryWindow' not in defaults  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

config_path = tmp_path / 'config.json'
config_path.write_text(json.dumps({'agents': {'defaults': {'maxTokens': 2222, 'memoryWindow': 30}}}), encoding='utf-8')
config = load_config(config_path)
save_config(config, config_path)
saved = json.loads(config_path.read_text(encoding='utf-8'))
defaults = saved['agents']['defaults']
assert defaults['maxTokens'] == 2222
assert defaults['contextWindowTokens'] == 65536
assert 'memoryWindow' not in defaults
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:29*

### test_onboard_does_not_crash_with_legacy_memory_window

**Category**: workflow  
**Description**: Workflow: test onboard does not crash with legacy memory window  
**Expected**: assert result.exit_code == 0  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

config_path = tmp_path / 'config.json'
workspace = tmp_path / 'workspace'
config_path.write_text(json.dumps({'agents': {'defaults': {'maxTokens': 3333, 'memoryWindow': 50}}}), encoding='utf-8')
monkeypatch.setattr('nanobot.config.loader.get_config_path', lambda: config_path)
monkeypatch.setattr('nanobot.cli.commands.get_workspace_path', lambda _workspace=None: workspace)
from typer.testing import CliRunner
from nanobot.cli.commands import app
runner = CliRunner()
result = runner.invoke(app, ['onboard'], input='n\n')
assert result.exit_code == 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:55*

### test_onboard_refresh_backfills_missing_channel_fields

**Category**: workflow  
**Description**: Workflow: test onboard refresh backfills missing channel fields  
**Expected**: assert saved['channels']['qq']['msgFormat'] == 'plain'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

from types import SimpleNamespace
config_path = tmp_path / 'config.json'
workspace = tmp_path / 'workspace'
config_path.write_text(json.dumps({'channels': {'qq': {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': []}}}), encoding='utf-8')
monkeypatch.setattr('nanobot.config.loader.get_config_path', lambda: config_path)
monkeypatch.setattr('nanobot.cli.commands.get_workspace_path', lambda _workspace=None: workspace)
monkeypatch.setattr('nanobot.channels.registry.discover_all', lambda: {'qq': SimpleNamespace(default_config=lambda: {'enabled': False, 'appId': '', 'secret': '', 'allowFrom': [], 'msgFormat': 'plain'})})
from typer.testing import CliRunner
from nanobot.cli.commands import app
runner = CliRunner()
result = runner.invoke(app, ['onboard'], input='n\n')
assert result.exit_code == 0
saved = json.loads(config_path.read_text(encoding='utf-8'))
assert saved['channels']['qq']['msgFormat'] == 'plain'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:83*

### test_returns_card_id_on_success

**Category**: workflow  
**Description**: Workflow: test returns card id on success  
**Expected**: ch._client.im.v1.message.create.assert_called_once()  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
ch = _make_channel()
ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response('card_123')
ch._client.im.v1.message.create.return_value = _mock_send_response()
result = ch._create_streaming_card_sync('chat_id', 'oc_chat1')
assert result == 'card_123'
ch._client.cardkit.v1.card.create.assert_called_once()
ch._client.im.v1.message.create.assert_called_once()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:62*

### test_save_turn_skips_multimodal_user_when_only_runtime_context

**Category**: method_call  
**Description**: test save turn skips multimodal user when only runtime context  
**Expected**: assert session.messages == []  
**Confidence**: 0.85  

```python
loop._save_turn(session, [{'role': 'user', 'content': [{'type': 'text', 'text': runtime}]}], skip=0)
assert session.messages == []
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:17*

### test_save_turn_keeps_image_placeholder_with_path_after_runtime_strip

**Category**: method_call  
**Description**: test save turn keeps image placeholder with path after runtime strip  
**Expected**: assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image: /media/feishu/photo.jpg]'}]  
**Confidence**: 0.85  

```python
loop._save_turn(session, [{'role': 'user', 'content': [{'type': 'text', 'text': runtime}, {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,abc'}, '_meta': {'path': '/media/feishu/photo.jpg'}}]}], skip=0)
assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image: /media/feishu/photo.jpg]'}]
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:30*

### test_save_turn_keeps_image_placeholder_without_meta

**Category**: method_call  
**Description**: test save turn keeps image placeholder without meta  
**Expected**: assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image]'}]  
**Confidence**: 0.85  

```python
loop._save_turn(session, [{'role': 'user', 'content': [{'type': 'text', 'text': runtime}, {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,abc'}}]}], skip=0)
assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image]'}]
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:49*

### test_save_turn_keeps_tool_results_under_16k

**Category**: method_call  
**Description**: test save turn keeps tool results under 16k  
**Expected**: assert session.messages[0]['content'] == content  
**Confidence**: 0.85  

```python
loop._save_turn(session, [{'role': 'tool', 'tool_call_id': 'call_1', 'name': 'read_file', 'content': content}], skip=0)
assert session.messages[0]['content'] == content
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:68*

### test_explicit_provider_import_still_works

**Category**: method_call  
**Description**: test explicit provider import still works  
**Expected**: assert namespace['AnthropicProvider'].__name__ == 'AnthropicProvider'  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

exec('from nanobot.providers import AnthropicProvider', namespace)
assert namespace['AnthropicProvider'].__name__ == 'AnthropicProvider'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_providers_init.py:37*

### test_sent_in_turn_tracks_same_target

**Category**: method_call  
**Description**: test sent in turn tracks same target  
**Expected**: assert not tool._sent_in_turn  
**Confidence**: 0.85  

```python
tool.set_context('feishu', 'chat1')
assert not tool._sent_in_turn
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_message_tool_suppress.py:123*

### test_start_turn_resets

**Category**: method_call  
**Description**: test start turn resets  
**Expected**: assert not tool._sent_in_turn  
**Confidence**: 0.85  

```python
tool.start_turn()
assert not tool._sent_in_turn
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_message_tool_suppress.py:131*

### test_creates_memory_directory

**Category**: method_call  
**Description**: Should create memory directory structure.  
**Expected**: assert (workspace / 'memory').exists() or (workspace / 'skills').exists()  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: tmp_path

sync_workspace_templates(workspace, silent=True)
assert (workspace / 'memory').exists() or (workspace / 'skills').exists()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:335*

### test_runtime_dirs_follow_config_path

**Category**: method_call  
**Description**: test runtime dirs follow config path  
**Expected**: assert get_data_dir() == config_file.parent  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

monkeypatch.setattr('nanobot.config.paths.get_config_path', lambda: config_file)
assert get_data_dir() == config_file.parent
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_paths.py:19*

### test_media_dir_supports_channel_namespace

**Category**: method_call  
**Description**: test media dir supports channel namespace  
**Expected**: assert get_media_dir() == config_file.parent / 'media'  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch, tmp_path

monkeypatch.setattr('nanobot.config.paths.get_config_path', lambda: config_file)
assert get_media_dir() == config_file.parent / 'media'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_paths.py:29*

### test_clear_resets_last_consolidated

**Category**: method_call  
**Description**: Test that clear() resets last_consolidated to 0.  
**Expected**: assert len(session.messages) == 0  
**Confidence**: 0.85  

```python
session.clear()
assert len(session.messages) == 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_consolidate_offset.py:83*

### test_returns_card_id_on_success

**Category**: method_call  
**Description**: test returns card id on success  
**Expected**: ch._client.im.v1.message.create.assert_called_once()  
**Confidence**: 0.85  
**Tags**: mock  

```python
ch._client.cardkit.v1.card.create.assert_called_once()
ch._client.im.v1.message.create.assert_called_once()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:68*

### test_retain_recent_legal_suffix_keeps_recent_messages

**Category**: method_call  
**Description**: test retain recent legal suffix keeps recent messages  
**Expected**: assert len(session.messages) == 4  
**Confidence**: 0.85  

```python
session.retain_recent_legal_suffix(4)
assert len(session.messages) == 4
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:72*

### test_retain_recent_legal_suffix_adjusts_last_consolidated

**Category**: method_call  
**Description**: test retain recent legal suffix adjusts last consolidated  
**Expected**: assert len(session.messages) == 4  
**Confidence**: 0.85  

```python
session.retain_recent_legal_suffix(4)
assert len(session.messages) == 4
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:85*

### test_retain_recent_legal_suffix_zero_clears_session

**Category**: method_call  
**Description**: test retain recent legal suffix zero clears session  
**Expected**: assert session.messages == []  
**Confidence**: 0.85  

```python
session.retain_recent_legal_suffix(0)
assert session.messages == []
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:97*

### test_retain_recent_legal_suffix_keeps_legal_tool_boundary

**Category**: method_call  
**Description**: test retain recent legal suffix keeps legal tool boundary  
**Expected**: assert history[0]['role'] == 'user'  
**Confidence**: 0.85  

```python
_assert_no_orphans(history)
assert history[0]['role'] == 'user'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:114*

### test_orphan_trim_with_last_consolidated

**Category**: method_call  
**Description**: Orphan trimming works correctly when session is partially consolidated.  
**Expected**: assert all((m.get('role') != 'tool' or m['tool_call_id'].startswith('new_') for m in history))  
**Confidence**: 0.85  

```python
_assert_no_orphans(history)
assert all((m.get('role') != 'tool' or m['tool_call_id'].startswith('new_') for m in history))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:135*

### test_all_orphan_prefix_stripped

**Category**: method_call  
**Description**: If the window starts with orphan tool results and nothing else, they're all dropped.  
**Expected**: assert history[0]['role'] == 'user'  
**Confidence**: 0.85  

```python
_assert_no_orphans(history)
assert history[0]['role'] == 'user'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:163*

### test_save_turn_skips_multimodal_user_when_only_runtime_context

**Category**: instantiation  
**Description**: Instantiate Session: test save turn skips multimodal user when only runtime context  
**Expected**: assert session.messages == []  
**Confidence**: 0.80  

```python
session = Session(key='test:runtime-only')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:14*

### test_save_turn_keeps_image_placeholder_with_path_after_runtime_strip

**Category**: instantiation  
**Description**: Instantiate Session: test save turn keeps image placeholder with path after runtime strip  
**Expected**: assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image: /media/feishu/photo.jpg]'}]  
**Confidence**: 0.80  

```python
session = Session(key='test:image')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:27*

### test_save_turn_keeps_image_placeholder_without_meta

**Category**: instantiation  
**Description**: Instantiate Session: test save turn keeps image placeholder without meta  
**Expected**: assert session.messages[0]['content'] == [{'type': 'text', 'text': '[image]'}]  
**Confidence**: 0.80  

```python
session = Session(key='test:image-no-meta')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:46*

### test_save_turn_keeps_tool_results_under_16k

**Category**: instantiation  
**Description**: Instantiate Session: test save turn keeps tool results under 16k  
**Expected**: assert session.messages[0]['content'] == content  
**Confidence**: 0.80  

```python
session = Session(key='test:tool-result')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_save_turn.py:65*

### test_leading_markdown_stays_with_first_table

**Category**: instantiation  
**Description**: Instantiate _md: test leading markdown stays with first table  
**Expected**: assert len(result) == 1  
**Confidence**: 0.80  

```python
intro = _md('intro')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:94*

### test_leading_markdown_stays_with_first_table

**Category**: instantiation  
**Description**: Instantiate split: test leading markdown stays with first table  
**Expected**: assert len(result) == 1  
**Confidence**: 0.80  

```python
result = split([intro, t])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:96*

### test_trailing_markdown_after_second_table

**Category**: instantiation  
**Description**: Instantiate split: test trailing markdown after second table  
**Expected**: assert len(result) == 2  
**Confidence**: 0.80  

```python
result = split([t1, t2, tail])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:104*

### test_non_table_elements_before_first_table_kept_in_first_group

**Category**: instantiation  
**Description**: Instantiate split: test non table elements before first table kept in first group  
**Expected**: assert result[0] == [head, t1]  
**Confidence**: 0.80  

```python
result = split([head, t1, t2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:112*

### test_format_timing_cron_with_tz

**Category**: instantiation  
**Description**: Instantiate _make_tool: test format timing cron with tz  
**Expected**: assert tool._format_timing(s) == 'cron: 0 9 * * 1-5 (America/Denver)'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:24*

### test_format_timing_cron_with_tz

**Category**: instantiation  
**Description**: Instantiate CronSchedule: test format timing cron with tz  
**Expected**: assert tool._format_timing(s) == 'cron: 0 9 * * 1-5 (America/Denver)'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

s = CronSchedule(kind='cron', expr='0 9 * * 1-5', tz='America/Denver')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:25*

### test_format_timing_cron_without_tz

**Category**: instantiation  
**Description**: Instantiate _make_tool: test format timing cron without tz  
**Expected**: assert tool._format_timing(s) == 'cron: */5 * * * *'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:30*

### test_format_timing_cron_without_tz

**Category**: instantiation  
**Description**: Instantiate CronSchedule: test format timing cron without tz  
**Expected**: assert tool._format_timing(s) == 'cron: */5 * * * *'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

s = CronSchedule(kind='cron', expr='*/5 * * * *')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:31*

### test_format_timing_every_hours

**Category**: instantiation  
**Description**: Instantiate _make_tool: test format timing every hours  
**Expected**: assert tool._format_timing(s) == 'every 2h'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:36*

### test_format_timing_every_hours

**Category**: instantiation  
**Description**: Instantiate CronSchedule: test format timing every hours  
**Expected**: assert tool._format_timing(s) == 'every 2h'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

s = CronSchedule(kind='every', every_ms=7200000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:37*

### test_format_timing_every_minutes

**Category**: instantiation  
**Description**: Instantiate _make_tool: test format timing every minutes  
**Expected**: assert tool._format_timing(s) == 'every 30m'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

tool = _make_tool(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_tool_list.py:42*

### test_matrix_html_cleaner_strips_event_handlers_and_script_tags

**Category**: instantiation  
**Description**: Instantiate clean: test matrix html cleaner strips event handlers and script tags  
**Expected**: assert '<script' not in cleaned_html  
**Confidence**: 0.80  

```python
cleaned_html = matrix_module.MATRIX_HTML_CLEANER.clean(dirty_html)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_matrix_channel.py:1267*

### test_custom_provider_parse_handles_empty_choices

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test custom provider parse handles empty choices  
**Expected**: assert result.finish_reason == 'error'  
**Confidence**: 0.80  
**Tags**: mock  

```python
response = SimpleNamespace(choices=[])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_custom_provider.py:12*

### test_custom_provider_parse_handles_empty_choices

**Category**: instantiation  
**Description**: Instantiate _parse: test custom provider parse handles empty choices  
**Expected**: assert result.finish_reason == 'error'  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = provider._parse(response)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_custom_provider.py:14*

### test_custom_provider_parse_accepts_plain_string_response

**Category**: instantiation  
**Description**: Instantiate _parse: test custom provider parse accepts plain string response  
**Expected**: assert result.finish_reason == 'stop'  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = provider._parse('hello from backend')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_custom_provider.py:24*

### test_custom_provider_parse_accepts_dict_response

**Category**: instantiation  
**Description**: Instantiate _parse: test custom provider parse accepts dict response  
**Expected**: assert result.finish_reason == 'stop'  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = provider._parse({'choices': [{'message': {'content': 'hello from dict'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 1, 'completion_tokens': 2, 'total_tokens': 3}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_custom_provider.py:34*

### test_custom_provider_parse_chunks_accepts_plain_text_chunks

**Category**: instantiation  
**Description**: Instantiate _parse_chunks: test custom provider parse chunks accepts plain text chunks  
**Expected**: assert result.finish_reason == 'stop'  
**Confidence**: 0.80  

```python
result = OpenAICompatProvider._parse_chunks(['hello ', 'world'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_custom_provider.py:52*

### test_azure_openai_provider_init

**Category**: instantiation  
**Description**: Instantiate AzureOpenAIProvider: Test AzureOpenAIProvider initialization without deployment_name.  
**Expected**: assert provider.api_key == 'test-key'  
**Confidence**: 0.80  

```python
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o-deployment')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:13*

### test_build_chat_url

**Category**: instantiation  
**Description**: Instantiate AzureOpenAIProvider: Test Azure OpenAI URL building with different deployment names.  
**Confidence**: 0.80  

```python
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:38*

### test_build_chat_url

**Category**: instantiation  
**Description**: Instantiate _build_chat_url: Test Azure OpenAI URL building with different deployment names.  
**Confidence**: 0.80  

```python
url = provider._build_chat_url(deployment_name)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:52*

### test_build_chat_url_api_base_without_slash

**Category**: instantiation  
**Description**: Instantiate AzureOpenAIProvider: Test URL building when api_base doesn't end with slash.  
**Expected**: assert url == expected  
**Confidence**: 0.80  

```python
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:58*

### test_build_chat_url_api_base_without_slash

**Category**: instantiation  
**Description**: Instantiate _build_chat_url: Test URL building when api_base doesn't end with slash.  
**Expected**: assert url == expected  
**Confidence**: 0.80  

```python
url = provider._build_chat_url('test-deployment')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:64*

### test_build_headers

**Category**: instantiation  
**Description**: Instantiate AzureOpenAIProvider: Test Azure OpenAI header building with api-key authentication.  
**Expected**: assert headers['Content-Type'] == 'application/json'  
**Confidence**: 0.80  

```python
provider = AzureOpenAIProvider(api_key='test-api-key-123', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:71*

### test_prepare_request_payload

**Category**: instantiation  
**Description**: Instantiate AzureOpenAIProvider: Test request payload preparation with Azure OpenAI 2024-10-21 compliance.  
**Expected**: assert payload['messages'] == messages  
**Confidence**: 0.80  

```python
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:85*

### test_prepare_request_payload

**Category**: instantiation  
**Description**: Instantiate _prepare_request_payload: Test request payload preparation with Azure OpenAI 2024-10-21 compliance.  
**Expected**: assert payload['messages'] == messages  
**Confidence**: 0.80  

```python
payload = provider._prepare_request_payload('gpt-4o', messages, max_tokens=1500, temperature=0.8)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:92*

### test_prepare_request_payload

**Category**: instantiation  
**Description**: Instantiate _prepare_request_payload: Test request payload preparation with Azure OpenAI 2024-10-21 compliance.  
**Expected**: assert payload_with_tools['tools'] == tools  
**Confidence**: 0.80  

```python
payload_with_tools = provider._prepare_request_payload('gpt-4o', messages, tools=tools)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_azure_openai_provider.py:101*

### test_tool_call_request_serializes_extra_content

**Category**: instantiation  
**Description**: Instantiate ToolCallRequest: test tool call request serializes extra content  
**Expected**: assert payload['extra_content'] == GEMINI_EXTRA  
**Confidence**: 0.80  

```python
tc = ToolCallRequest(id='abc123xyz', name='read_file', arguments={'path': 'todo.md'}, extra_content=GEMINI_EXTRA)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:21*

### test_tool_call_request_serializes_provider_fields

**Category**: instantiation  
**Description**: Instantiate ToolCallRequest: test tool call request serializes provider fields  
**Expected**: assert payload['provider_specific_fields'] == {'custom_key': 'custom_val'}  
**Confidence**: 0.80  

```python
tc = ToolCallRequest(id='abc123xyz', name='read_file', arguments={'path': 'todo.md'}, provider_specific_fields={'custom_key': 'custom_val'}, function_provider_specific_fields={'inner': 'value'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:35*

### test_tool_call_request_omits_absent_extras

**Category**: instantiation  
**Description**: Instantiate ToolCallRequest: test tool call request omits absent extras  
**Expected**: assert 'extra_content' not in payload  
**Confidence**: 0.80  

```python
tc = ToolCallRequest(id='x', name='fn', arguments={})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:50*

### test_parse_sdk_object_preserves_extra_content

**Category**: instantiation  
**Description**: Instantiate _parse: test parse sdk object preserves extra content  
**Expected**: assert len(result.tool_calls) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = provider._parse(_make_sdk_response_with_extra_content())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:84*

### test_parse_dict_preserves_extra_content

**Category**: instantiation  
**Description**: Instantiate _parse: test parse dict preserves extra content  
**Expected**: assert len(result.tool_calls) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = provider._parse(response_dict)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:117*

### test_parse_chunks_sdk_preserves_extra_content

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test parse chunks sdk preserves extra content  
**Expected**: assert len(result.tool_calls) == 1  
**Confidence**: 0.80  

```python
fn_delta = SimpleNamespace(name='get_weather', arguments='{"city":"Tokyo"}')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_gemini_thought_signature.py:131*

### test_thinking_spinner_pause_stops_and_restarts

**Category**: instantiation  
**Description**: Instantiate ThinkingSpinner: Pause should stop the active spinner and restart it afterward.  
**Expected**: assert spinner.method_calls == [call.start(), call.stop(), call.start(), call.stop()]  
**Confidence**: 0.80  
**Tags**: mock  

```python
thinking = stream_mod.ThinkingSpinner(console=mock_console)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_cli_input.py:69*

### test_print_cli_progress_line_pauses_spinner_before_printing

**Category**: instantiation  
**Description**: Instantiate ThinkingSpinner: CLI progress output should pause spinner to avoid garbled lines.  
**Confidence**: 0.80  
**Tags**: mock  

```python
thinking = stream_mod.ThinkingSpinner(console=mock_console)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_cli_input.py:92*

### test_response_renderable_uses_text_for_explicit_plain_rendering

**Category**: instantiation  
**Description**: Instantiate _response_renderable: test response renderable uses text for explicit plain rendering  
**Expected**: assert renderable.__class__.__name__ == 'Text'  
**Confidence**: 0.80  

```python
renderable = commands._response_renderable(status, render_markdown=True, metadata={'render_as': 'text'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_cli_input.py:127*

### test_response_renderable_preserves_normal_markdown_rendering

**Category**: instantiation  
**Description**: Instantiate _response_renderable: test response renderable preserves normal markdown rendering  
**Expected**: assert renderable.__class__.__name__ == 'Markdown'  
**Confidence**: 0.80  

```python
renderable = commands._response_renderable('**bold**', render_markdown=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_cli_input.py:137*

### test_response_renderable_without_metadata_keeps_markdown_path

**Category**: instantiation  
**Description**: Instantiate _response_renderable: test response renderable without metadata keeps markdown path  
**Expected**: assert renderable.__class__.__name__ == 'Markdown'  
**Confidence**: 0.80  

```python
renderable = commands._response_renderable(help_text, render_markdown=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cli\test_cli_input.py:145*

### test_importing_providers_package_is_lazy

**Category**: instantiation  
**Description**: Instantiate import_module: test importing providers package is lazy  
**Expected**: assert 'nanobot.providers.anthropic_provider' not in sys.modules  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

providers = importlib.import_module('nanobot.providers')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_providers_init.py:16*

### test_agent_loop_registers_cron_tool_with_configured_timezone

**Category**: instantiation  
**Description**: Instantiate AgentLoop: test agent loop registers cron tool with configured timezone  
**Expected**: assert isinstance(cron_tool, CronTool)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path

loop = AgentLoop(bus=bus, provider=provider, workspace=tmp_path, model='test-model', cron_service=CronService(tmp_path / 'cron' / 'jobs.json'), timezone='Asia/Shanghai')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_cron_timezone.py:15*

### test_agent_loop_registers_cron_tool_with_configured_timezone

**Category**: instantiation  
**Description**: Instantiate get: test agent loop registers cron tool with configured timezone  
**Expected**: assert isinstance(cron_tool, CronTool)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path

cron_tool = loop.tools.get('cron')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_loop_cron_timezone.py:24*

### test_openrouter_spec_is_gateway

**Category**: instantiation  
**Description**: Instantiate find_by_name: test openrouter spec is gateway  
**Expected**: assert spec is not None  
**Confidence**: 0.80  

```python
spec = find_by_name('openrouter')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_litellm_kwargs.py:57*

### test_openrouter_sets_default_attribution_headers

**Category**: instantiation  
**Description**: Instantiate find_by_name: test openrouter sets default attribution headers  
**Expected**: assert headers['HTTP-Referer'] == 'https://github.com/HKUDS/nanobot'  
**Confidence**: 0.80  
**Tags**: mock  

```python
spec = find_by_name('openrouter')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_litellm_kwargs.py:64*

### test_openrouter_user_headers_override_default_attribution

**Category**: instantiation  
**Description**: Instantiate find_by_name: test openrouter user headers override default attribution  
**Expected**: assert headers['HTTP-Referer'] == 'https://nanobot.ai'  
**Confidence**: 0.80  
**Tags**: mock  

```python
spec = find_by_name('openrouter')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_litellm_kwargs.py:81*

### test_openai_model_passthrough

**Category**: instantiation  
**Description**: Instantiate find_by_name: OpenAI models pass through unchanged.  
**Expected**: assert provider.get_default_model() == 'gpt-4o'  
**Confidence**: 0.80  
**Tags**: mock  

```python
spec = find_by_name('openai')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_litellm_kwargs.py:209*

### test_openai_model_passthrough

**Category**: instantiation  
**Description**: Instantiate OpenAICompatProvider: OpenAI models pass through unchanged.  
**Confidence**: 0.80  
**Tags**: mock  

```python
provider = OpenAICompatProvider(api_key='sk-test-key', default_model='gpt-4o', spec=spec)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\providers\test_litellm_kwargs.py:211*

### test_extract_post_content_supports_post_wrapper_shape

**Category**: instantiation  
**Description**: Instantiate _extract_post_content: test extract post content supports post wrapper shape  
**Expected**: assert text == '日报 完成'  
**Confidence**: 0.80  

```python
text, image_keys = _extract_post_content(payload)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:30*

### test_extract_post_content_keeps_direct_shape_behavior

**Category**: instantiation  
**Description**: Instantiate _extract_post_content: test extract post content keeps direct shape behavior  
**Expected**: assert text == 'Daily report'  
**Confidence**: 0.80  

```python
text, image_keys = _extract_post_content(payload)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:48*

### test_register_optional_event_keeps_builder_when_method_missing

**Category**: instantiation  
**Description**: Instantiate _register_optional_event: test register optional event keeps builder when method missing  
**Expected**: assert same is builder  
**Confidence**: 0.80  

```python
same = FeishuChannel._register_optional_event(builder, 'missing', object())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:59*

### test_register_optional_event_calls_supported_method

**Category**: instantiation  
**Description**: Instantiate _register_optional_event: test register optional event calls supported method  
**Expected**: assert same is builder  
**Confidence**: 0.80  

```python
same = FeishuChannel._register_optional_event(builder, 'register_event', handler)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:73*

### test_wrapper_preserves_non_nullable_unions

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test wrapper preserves non nullable unions  
**Expected**: assert wrapper.parameters['properties']['value']['anyOf'] == [{'type': 'string'}, {'type': 'integer'}]  
**Confidence**: 0.80  

```python
tool_def = SimpleNamespace(name='demo', description='demo tool', inputSchema={'type': 'object', 'properties': {'value': {'anyOf': [{'type': 'string'}, {'type': 'integer'}]}}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:88*

### test_wrapper_preserves_non_nullable_unions

**Category**: instantiation  
**Description**: Instantiate MCPToolWrapper: test wrapper preserves non nullable unions  
**Expected**: assert wrapper.parameters['properties']['value']['anyOf'] == [{'type': 'string'}, {'type': 'integer'}]  
**Confidence**: 0.80  

```python
wrapper = MCPToolWrapper(SimpleNamespace(call_tool=None), 'test', tool_def)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:101*

### test_wrapper_normalizes_nullable_property_type_union

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test wrapper normalizes nullable property type union  
**Expected**: assert wrapper.parameters['properties']['name'] == {'type': 'string', 'nullable': True}  
**Confidence**: 0.80  

```python
tool_def = SimpleNamespace(name='demo', description='demo tool', inputSchema={'type': 'object', 'properties': {'name': {'type': ['string', 'null']}}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:110*

### test_wrapper_normalizes_nullable_property_type_union

**Category**: instantiation  
**Description**: Instantiate MCPToolWrapper: test wrapper normalizes nullable property type union  
**Expected**: assert wrapper.parameters['properties']['name'] == {'type': 'string', 'nullable': True}  
**Confidence**: 0.80  

```python
wrapper = MCPToolWrapper(SimpleNamespace(call_tool=None), 'test', tool_def)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:121*

### test_wrapper_normalizes_nullable_property_anyof

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test wrapper normalizes nullable property anyof  
**Expected**: assert wrapper.parameters['properties']['name'] == {'type': 'string', 'description': 'optional name', 'nullable': True}  
**Confidence**: 0.80  

```python
tool_def = SimpleNamespace(name='demo', description='demo tool', inputSchema={'type': 'object', 'properties': {'name': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'description': 'optional name'}}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:127*

### test_wrapper_normalizes_nullable_property_anyof

**Category**: instantiation  
**Description**: Instantiate MCPToolWrapper: test wrapper normalizes nullable property anyof  
**Expected**: assert wrapper.parameters['properties']['name'] == {'type': 'string', 'description': 'optional name', 'nullable': True}  
**Confidence**: 0.80  

```python
wrapper = MCPToolWrapper(SimpleNamespace(call_tool=None), 'test', tool_def)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_mcp_tool.py:141*

### manager

**Category**: instantiation  
**Description**: Instantiate ChannelManager: Create a channel manager with a mock channel.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: config, bus

manager = ChannelManager(config, bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_manager_delta_coalescing.py:55*

### manager

**Category**: instantiation  
**Description**: Instantiate MockChannel: Create a channel manager with a mock channel.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: config, bus

manager.channels['mock'] = MockChannel({}, bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_manager_delta_coalescing.py:56*

### test_system_prompt_stays_stable_when_clock_changes

**Category**: instantiation  
**Description**: Instantiate _make_workspace: System prompt should not change just because wall clock minute changes.  
**Expected**: assert prompt1 == prompt2  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

workspace = _make_workspace(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:38*

### test_system_prompt_stays_stable_when_clock_changes

**Category**: instantiation  
**Description**: Instantiate ContextBuilder: System prompt should not change just because wall clock minute changes.  
**Expected**: assert prompt1 == prompt2  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

builder = ContextBuilder(workspace)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:39*

### test_system_prompt_stays_stable_when_clock_changes

**Category**: instantiation  
**Description**: Instantiate real_datetime: System prompt should not change just because wall clock minute changes.  
**Expected**: assert prompt1 == prompt2  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

_FakeDatetime.current = real_datetime(2026, 2, 24, 13, 59)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:41*

### test_system_prompt_stays_stable_when_clock_changes

**Category**: instantiation  
**Description**: Instantiate real_datetime: System prompt should not change just because wall clock minute changes.  
**Expected**: assert prompt1 == prompt2  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

_FakeDatetime.current = real_datetime(2026, 2, 24, 14, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:44*

### test_runtime_context_is_separate_untrusted_user_message

**Category**: instantiation  
**Description**: Instantiate _make_workspace: Runtime metadata should be merged with the user message.  
**Expected**: assert messages[0]['role'] == 'system'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

workspace = _make_workspace(tmp_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:52*

### test_runtime_context_is_separate_untrusted_user_message

**Category**: instantiation  
**Description**: Instantiate ContextBuilder: Runtime metadata should be merged with the user message.  
**Expected**: assert messages[0]['role'] == 'system'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

builder = ContextBuilder(workspace)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:53*

### test_runtime_context_is_separate_untrusted_user_message

**Category**: instantiation  
**Description**: Instantiate build_messages: Runtime metadata should be merged with the user message.  
**Expected**: assert messages[0]['role'] == 'system'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

messages = builder.build_messages(history=[], current_message='Return exactly: OK', channel='cli', chat_id='direct')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_context_prompt_cache.py:55*

### test_adds_missing_top_level_keys

**Category**: instantiation  
**Description**: Instantiate _merge_missing_defaults: test adds missing top level keys  
**Expected**: assert result == {'a': 1, 'b': 2, 'c': 3}  
**Confidence**: 0.80  

```python
result = _merge_missing_defaults(existing, defaults)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:38*

### test_preserves_existing_values

**Category**: instantiation  
**Description**: Instantiate _merge_missing_defaults: test preserves existing values  
**Expected**: assert result == {'a': 'custom_value'}  
**Confidence**: 0.80  

```python
result = _merge_missing_defaults(existing, defaults)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:46*

### test_merges_nested_dicts_recursively

**Category**: instantiation  
**Description**: Instantiate _merge_missing_defaults: test merges nested dicts recursively  
**Expected**: assert result == {'level1': {'level2': {'existing': 'kept', 'added': 'new'}, 'level2b': 'also_new'}}  
**Confidence**: 0.80  

```python
result = _merge_missing_defaults(existing, defaults)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:68*

### test_backfills_channel_config

**Category**: instantiation  
**Description**: Instantiate _merge_missing_defaults: Real-world scenario: backfill missing channel fields.  
**Expected**: assert result['msgFormat'] == 'plain'  
**Confidence**: 0.80  

```python
result = _merge_missing_defaults(existing_channel, default_channel)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:110*

### test_extracts_str_type

**Category**: instantiation  
**Description**: Instantiate _get_field_type_info: test extracts str type  
**Expected**: assert type_name == 'str'  
**Confidence**: 0.80  

```python
type_name, inner = _get_field_type_info(Model.model_fields['field'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:123*

### test_extracts_int_type

**Category**: instantiation  
**Description**: Instantiate _get_field_type_info: test extracts int type  
**Expected**: assert type_name == 'int'  
**Confidence**: 0.80  

```python
type_name, inner = _get_field_type_info(Model.model_fields['count'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:131*

### test_extracts_bool_type

**Category**: instantiation  
**Description**: Instantiate _get_field_type_info: test extracts bool type  
**Expected**: assert type_name == 'bool'  
**Confidence**: 0.80  

```python
type_name, inner = _get_field_type_info(Model.model_fields['enabled'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:139*

### test_extracts_float_type

**Category**: instantiation  
**Description**: Instantiate _get_field_type_info: test extracts float type  
**Expected**: assert type_name == 'float'  
**Confidence**: 0.80  

```python
type_name, inner = _get_field_type_info(Model.model_fields['ratio'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_onboard_logic.py:147*

### test_init_skill_creates_expected_files

**Category**: instantiation  
**Description**: Instantiate init_skill: test init skill creates expected files  
**Expected**: assert skill_dir == tmp_path / 'demo-skill'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

skill_dir = init_skill.init_skill('demo-skill', tmp_path, ['scripts', 'references', 'assets'], include_examples=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:18*

### test_validate_skill_accepts_existing_skill_creator

**Category**: instantiation  
**Description**: Instantiate validate_skill: test validate skill accepts existing skill creator  
**Expected**: assert valid, message  
**Confidence**: 0.80  

```python
valid, message = quick_validate.validate_skill(Path('nanobot/skills/skill-creator').resolve())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:33*

### test_validate_skill_rejects_placeholder_description

**Category**: instantiation  
**Description**: Instantiate validate_skill: test validate skill rejects placeholder description  
**Expected**: assert not valid  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

valid, message = quick_validate.validate_skill(skill_dir)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:52*

### test_validate_skill_rejects_root_files_outside_allowed_dirs

**Category**: instantiation  
**Description**: Instantiate validate_skill: test validate skill rejects root files outside allowed dirs  
**Expected**: assert not valid  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

valid, message = quick_validate.validate_skill(skill_dir)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:71*

### test_package_skill_creates_archive

**Category**: instantiation  
**Description**: Instantiate package_skill: test package skill creates archive  
**Expected**: assert archive_path == tmp_path / 'dist' / 'package-me.skill'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:92*

### test_package_skill_creates_archive

**Category**: instantiation  
**Description**: Instantiate set: test package skill creates archive  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

names = set(archive.namelist())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:97*

### test_package_skill_rejects_symlink

**Category**: instantiation  
**Description**: Instantiate package_skill: test package skill rejects symlink  
**Expected**: assert archive_path is None  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_skill_creator_scripts.py:124*

### test_fetch_new_messages_parses_unseen_and_marks_seen

**Category**: instantiation  
**Description**: Instantiate _make_raw_email: test fetch new messages parses unseen and marks seen  
**Expected**: assert len(items) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

raw = _make_raw_email(subject='Invoice', body='Please pay')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:52*

### test_fetch_new_messages_parses_unseen_and_marks_seen

**Category**: instantiation  
**Description**: Instantiate EmailChannel: test fetch new messages parses unseen and marks seen  
**Expected**: assert len(items) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

channel = EmailChannel(_make_config(), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:80*

### test_fetch_new_messages_retries_once_when_imap_connection_goes_stale

**Category**: instantiation  
**Description**: Instantiate _make_raw_email: test fetch new messages retries once when imap connection goes stale  
**Expected**: assert len(items) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

raw = _make_raw_email(subject='Invoice', body='Please pay')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:95*

### test_fetch_new_messages_retries_once_when_imap_connection_goes_stale

**Category**: instantiation  
**Description**: Instantiate EmailChannel: test fetch new messages retries once when imap connection goes stale  
**Expected**: assert len(items) == 1  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

channel = EmailChannel(_make_config(), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:135*

### test_fetch_new_messages_keeps_messages_collected_before_stale_retry

**Category**: instantiation  
**Description**: Instantiate _make_raw_email: test fetch new messages keeps messages collected before stale retry  
**Expected**: assert [item['subject'] for item in items] == ['First', 'Second']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

raw_first = _make_raw_email(subject='First', body='First body')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:145*

### test_fetch_new_messages_keeps_messages_collected_before_stale_retry

**Category**: instantiation  
**Description**: Instantiate _make_raw_email: test fetch new messages keeps messages collected before stale retry  
**Expected**: assert [item['subject'] for item in items] == ['First', 'Second']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

raw_second = _make_raw_email(subject='Second', body='Second body')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_email_channel.py:146*

### test_feishu_config_reply_to_message_can_be_enabled

**Category**: instantiation  
**Description**: Instantiate FeishuConfig: test feishu config reply to message can be enabled  
**Expected**: assert config.reply_to_message is True  
**Confidence**: 0.80  

```python
config = FeishuConfig(reply_to_message=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:94*

### test_get_message_content_sync_returns_reply_prefix

**Category**: instantiation  
**Description**: Instantiate _make_get_message_response: test get message content sync returns reply prefix  
**Expected**: assert result == '[Reply to: what time is it?]'  
**Confidence**: 0.80  

```python
channel._client.im.v1.message.get.return_value = _make_get_message_response('what time is it?')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:104*

### test_get_message_content_sync_returns_reply_prefix

**Category**: instantiation  
**Description**: Instantiate _get_message_content_sync: test get message content sync returns reply prefix  
**Expected**: assert result == '[Reply to: what time is it?]'  
**Confidence**: 0.80  

```python
result = channel._get_message_content_sync('om_parent')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:106*

### test_get_message_content_sync_truncates_long_text

**Category**: instantiation  
**Description**: Instantiate _make_get_message_response: test get message content sync truncates long text  
**Expected**: assert result is not None  
**Confidence**: 0.80  

```python
channel._client.im.v1.message.get.return_value = _make_get_message_response(long_text)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:114*

### test_get_message_content_sync_truncates_long_text

**Category**: instantiation  
**Description**: Instantiate _get_message_content_sync: test get message content sync truncates long text  
**Expected**: assert result is not None  
**Confidence**: 0.80  

```python
result = channel._get_message_content_sync('om_parent')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:116*

### test_get_message_content_sync_returns_none_on_api_failure

**Category**: instantiation  
**Description**: Instantiate _get_message_content_sync: test get message content sync returns none on api failure  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = channel._get_message_content_sync('om_parent')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:132*

### test_get_message_content_sync_returns_none_for_non_text_type

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test get message content sync returns none for non text type  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
body = SimpleNamespace(content=json.dumps({'image_key': 'img_1'}))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:139*

### test_get_message_content_sync_returns_none_for_non_text_type

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test get message content sync returns none for non text type  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
item = SimpleNamespace(msg_type='image', body=body)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:140*

### test_get_message_content_sync_returns_none_for_non_text_type

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test get message content sync returns none for non text type  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
data = SimpleNamespace(items=[item])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:141*

### test_get_message_content_sync_returns_none_for_non_text_type

**Category**: instantiation  
**Description**: Instantiate _get_message_content_sync: test get message content sync returns none for non text type  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = channel._get_message_content_sync('om_parent')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_reply.py:147*

### test_exact_match

**Category**: instantiation  
**Description**: Instantiate _find_match: test exact match  
**Expected**: assert match == 'world'  
**Confidence**: 0.80  

```python
match, count = _find_match('hello world', 'world')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:103*

### test_exact_no_match

**Category**: instantiation  
**Description**: Instantiate _find_match: test exact no match  
**Expected**: assert match is None  
**Confidence**: 0.80  

```python
match, count = _find_match('hello world', 'xyz')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:108*

### test_crlf_normalisation

**Category**: instantiation  
**Description**: Instantiate _find_match: test crlf normalisation  
**Expected**: assert match is not None  
**Confidence**: 0.80  

```python
match, count = _find_match(content, old_text)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:117*

### test_line_trim_fallback

**Category**: instantiation  
**Description**: Instantiate _find_match: test line trim fallback  
**Expected**: assert match is not None  
**Confidence**: 0.80  

```python
match, count = _find_match(content, old_text)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:124*

### test_line_trim_multiple_candidates

**Category**: instantiation  
**Description**: Instantiate _find_match: test line trim multiple candidates  
**Expected**: assert count == 2  
**Confidence**: 0.80  

```python
match, count = _find_match(content, old_text)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:133*

### test_empty_old_text

**Category**: instantiation  
**Description**: Instantiate _find_match: test empty old text  
**Expected**: assert match == ''  
**Confidence**: 0.80  

```python
match, count = _find_match('hello', '')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_filesystem_tools.py:137*

### test_add_job_rejects_unknown_timezone

**Category**: instantiation  
**Description**: Instantiate CronService: test add job rejects unknown timezone  
**Expected**: assert service.list_jobs(include_disabled=True) == []  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

service = CronService(tmp_path / 'cron' / 'jobs.json')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_service.py:11*

### test_add_job_accepts_valid_timezone

**Category**: instantiation  
**Description**: Instantiate CronService: test add job accepts valid timezone  
**Expected**: assert job.schedule.tz == 'America/Vancouver'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

service = CronService(tmp_path / 'cron' / 'jobs.json')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_service.py:24*

### test_add_job_accepts_valid_timezone

**Category**: instantiation  
**Description**: Instantiate add_job: test add job accepts valid timezone  
**Expected**: assert job.schedule.tz == 'America/Vancouver'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

job = service.add_job(name='tz ok', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='America/Vancouver'), message='hello')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\cron\test_cron_service.py:26*

### test_exec_tool_not_registered_when_disabled

**Category**: instantiation  
**Description**: Instantiate _make_loop: test exec tool not registered when disabled  
**Expected**: assert loop.tools.get('exec') is None  
**Confidence**: 0.80  

```python
loop, _bus = _make_loop(exec_config=ExecToolConfig(enable=False))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_task_cancel.py:102*

### test_make_headers_includes_route_tag_when_configured

**Category**: instantiation  
**Description**: Instantiate WeixinChannel: test make headers includes route tag when configured  
**Expected**: assert headers['Authorization'] == 'Bearer token'  
**Confidence**: 0.80  

```python
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], route_tag=123), bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:35*

### test_save_and_load_state_persists_context_tokens

**Category**: instantiation  
**Description**: Instantiate WeixinChannel: test save and load state persists context tokens  
**Expected**: assert saved['context_tokens'] == {'wx-user': 'ctx-1'}  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:53*

### test_save_and_load_state_persists_context_tokens

**Category**: instantiation  
**Description**: Instantiate loads: test save and load state persists context tokens  
**Expected**: assert saved['context_tokens'] == {'wx-user': 'ctx-1'}  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

saved = json.loads((tmp_path / 'account.json').read_text())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:63*

### test_save_and_load_state_persists_context_tokens

**Category**: instantiation  
**Description**: Instantiate WeixinChannel: test save and load state persists context tokens  
**Expected**: assert restored._load_state() is True  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

restored = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_weixin_channel.py:66*

### mock_feishu_channel

**Category**: instantiation  
**Description**: Instantiate FeishuChannel: Create a FeishuChannel with mocked client.  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
channel = FeishuChannel(config, bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_tool_hint_code_block.py:32*

### test_channels_config_accepts_unknown_keys

**Category**: instantiation  
**Description**: Instantiate model_validate: test channels config accepts unknown keys  
**Expected**: assert extra is not None  
**Confidence**: 0.80  

```python
cfg = ChannelsConfig.model_validate({'myplugin': {'enabled': True, 'token': 'abc'}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:70*

### test_channels_config_getattr_returns_extra

**Category**: instantiation  
**Description**: Instantiate model_validate: test channels config getattr returns extra  
**Expected**: assert isinstance(section, dict)  
**Confidence**: 0.80  

```python
cfg = ChannelsConfig.model_validate({'myplugin': {'enabled': True}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:80*

### test_channels_config_getattr_returns_extra

**Category**: instantiation  
**Description**: Instantiate getattr: test channels config getattr returns extra  
**Expected**: assert isinstance(section, dict)  
**Confidence**: 0.80  

```python
section = getattr(cfg, 'myplugin', None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:81*

### test_discover_plugins_loads_entry_points

**Category**: instantiation  
**Description**: Instantiate _make_entry_point: test discover plugins loads entry points  
**Expected**: assert 'line' in result  
**Confidence**: 0.80  
**Tags**: mock  

```python
ep = _make_entry_point('line', _FakePlugin)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:104*

### test_discover_plugins_handles_load_error

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test discover plugins handles load error  
**Expected**: assert 'broken' not in result  
**Confidence**: 0.80  
**Tags**: mock  

```python
ep = SimpleNamespace(name='broken', load=_boom)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:118*

### test_discover_all_includes_external_plugin

**Category**: instantiation  
**Description**: Instantiate _make_entry_point: test discover all includes external plugin  
**Expected**: assert 'line' in result  
**Confidence**: 0.80  
**Tags**: mock  

```python
ep = _make_entry_point('line', _FakePlugin)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:145*

### test_discover_all_builtin_shadows_plugin

**Category**: instantiation  
**Description**: Instantiate _make_entry_point: test discover all builtin shadows plugin  
**Expected**: assert 'telegram' in result  
**Confidence**: 0.80  
**Tags**: mock  

```python
ep = _make_entry_point('telegram', _FakeTelegram)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:156*

### test_channels_login_uses_discovered_plugin_class

**Category**: instantiation  
**Description**: Instantiate invoke: test channels login uses discovered plugin class  
**Expected**: assert result.exit_code == 0  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: monkeypatch

result = runner.invoke(app, ['channels', 'login', 'fakeplugin', '--force'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:217*

### test_builtin_channel_init_from_dict

**Category**: instantiation  
**Description**: Instantiate TelegramChannel: Built-in channels accept a raw dict and convert to Pydantic internally.  
**Expected**: assert ch.config.token == 'test-tok'  
**Confidence**: 0.80  

```python
ch = TelegramChannel({'enabled': False, 'token': 'test-tok', 'allowFrom': ['*']}, bus)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_channel_plugins.py:263*

### test_validate_params_missing_required

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params missing required  
**Expected**: assert 'missing required count' in '; '.join(errors)  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'hi'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:46*

### test_validate_params_type_and_range

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params type and range  
**Expected**: assert any(('count must be >= 1' in e for e in errors))  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'hi', 'count': 0})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:52*

### test_validate_params_type_and_range

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params type and range  
**Expected**: assert any(('count should be integer' in e for e in errors))  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'hi', 'count': '2'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:55*

### test_validate_params_enum_and_min_length

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params enum and min length  
**Expected**: assert any(('query must be at least 2 chars' in e for e in errors))  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'h', 'count': 2, 'mode': 'slow'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:61*

### test_validate_params_nested_object_and_array

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params nested object and array  
**Expected**: assert any(('missing required meta.tag' in e for e in errors))  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'hi', 'count': 2, 'meta': {'flags': [1, 'ok']}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:68*

### test_validate_params_ignores_unknown_fields

**Category**: instantiation  
**Description**: Instantiate validate_params: test validate params ignores unknown fields  
**Expected**: assert errors == []  
**Confidence**: 0.80  

```python
errors = tool.validate_params({'query': 'hi', 'count': 2, 'extra': 'x'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:81*

### test_exec_extract_absolute_paths_keeps_full_windows_path

**Category**: instantiation  
**Description**: Instantiate _extract_absolute_paths: test exec extract absolute paths keeps full windows path  
**Expected**: assert paths == ['C:\\user\\workspace\\txt']  
**Confidence**: 0.80  

```python
paths = ExecTool._extract_absolute_paths(cmd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:94*

### test_exec_extract_absolute_paths_ignores_relative_posix_segments

**Category**: instantiation  
**Description**: Instantiate _extract_absolute_paths: test exec extract absolute paths ignores relative posix segments  
**Expected**: assert '/bin/python' not in paths  
**Confidence**: 0.80  

```python
paths = ExecTool._extract_absolute_paths(cmd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:100*

### test_exec_extract_absolute_paths_captures_posix_absolute_paths

**Category**: instantiation  
**Description**: Instantiate _extract_absolute_paths: test exec extract absolute paths captures posix absolute paths  
**Expected**: assert '/tmp/data.txt' in paths  
**Confidence**: 0.80  

```python
paths = ExecTool._extract_absolute_paths(cmd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\tools\test_tool_validation.py:106*

### test_load_config_keeps_max_tokens_and_ignores_legacy_memory_window

**Category**: instantiation  
**Description**: Instantiate load_config: test load config keeps max tokens and ignores legacy memory window  
**Expected**: assert config.agents.defaults.max_tokens == 1234  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

config = load_config(config_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:22*

### test_save_config_writes_context_window_tokens_but_not_memory_window

**Category**: instantiation  
**Description**: Instantiate load_config: test save config writes context window tokens but not memory window  
**Expected**: assert defaults['maxTokens'] == 2222  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

config = load_config(config_path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:45*

### test_save_config_writes_context_window_tokens_but_not_memory_window

**Category**: instantiation  
**Description**: Instantiate loads: test save config writes context window tokens but not memory window  
**Expected**: assert defaults['maxTokens'] == 2222  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

saved = json.loads(config_path.read_text(encoding='utf-8'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:47*

### test_onboard_does_not_crash_with_legacy_memory_window

**Category**: instantiation  
**Description**: Instantiate invoke: test onboard does not crash with legacy memory window  
**Expected**: assert result.exit_code == 0  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

result = runner.invoke(app, ['onboard'], input='n\n')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:78*

### test_onboard_refresh_backfills_missing_channel_fields

**Category**: instantiation  
**Description**: Instantiate invoke: test onboard refresh backfills missing channel fields  
**Expected**: assert result.exit_code == 0  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

result = runner.invoke(app, ['onboard'], input='n\n')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:124*

### test_onboard_refresh_backfills_missing_channel_fields

**Category**: instantiation  
**Description**: Instantiate loads: test onboard refresh backfills missing channel fields  
**Expected**: assert saved['channels']['qq']['msgFormat'] == 'plain'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

saved = json.loads(config_path.read_text(encoding='utf-8'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\config\test_config_migration.py:127*

### test_is_allowed_requires_exact_match

**Category**: instantiation  
**Description**: Instantiate _DummyChannel: test is allowed requires exact match  
**Expected**: assert channel.is_allowed('allow@email.com') is True  
**Confidence**: 0.80  

```python
channel = _DummyChannel(SimpleNamespace(allow_from=['allow@email.com']), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_base_channel.py:22*

### test_rejects_non_http_scheme

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test rejects non http scheme  
**Expected**: assert not ok  
**Confidence**: 0.80  

```python
ok, err = validate_url_target('ftp://example.com/file')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:27*

### test_rejects_missing_domain

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test rejects missing domain  
**Expected**: assert not ok  
**Confidence**: 0.80  

```python
ok, err = validate_url_target('http://')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:33*

### test_blocks_private_ipv4

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test blocks private ipv4  
**Confidence**: 0.80  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: ip, label

ok, err = validate_url_target(f'http://evil.com/path')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:52*

### test_blocks_ipv6_loopback

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test blocks ipv6 loopback  
**Confidence**: 0.80  
**Tags**: mock  

```python
ok, err = validate_url_target('http://evil.com/')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:61*

### test_allows_public_ip

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test allows public ip  
**Confidence**: 0.80  
**Tags**: mock  

```python
ok, err = validate_url_target('http://example.com/page')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:71*

### test_allows_normal_https

**Category**: instantiation  
**Description**: Instantiate validate_url_target: test allows normal https  
**Confidence**: 0.80  
**Tags**: mock  

```python
ok, err = validate_url_target('https://github.com/HKUDS/nanobot')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\security\test_security_network.py:77*

### test_derive_topic_session_key_uses_thread_id

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test derive topic session key uses thread id  
**Expected**: assert TelegramChannel._derive_topic_session_key(message) == 'telegram:-100123:topic:42'  
**Confidence**: 0.80  

```python
message = SimpleNamespace(chat=SimpleNamespace(type='supergroup'), chat_id=-100123, message_thread_id=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:402*

### test_get_extension_falls_back_to_original_filename

**Category**: instantiation  
**Description**: Instantiate TelegramChannel: test get extension falls back to original filename  
**Expected**: assert channel._get_extension('file', None, 'report.pdf') == '.pdf'  
**Confidence**: 0.80  

```python
channel = TelegramChannel(TelegramConfig(), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:412*

### test_is_allowed_accepts_legacy_telegram_id_username_formats

**Category**: instantiation  
**Description**: Instantiate TelegramChannel: test is allowed accepts legacy telegram id username formats  
**Expected**: assert channel.is_allowed('12345|carol') is True  
**Confidence**: 0.80  

```python
channel = TelegramChannel(TelegramConfig(allow_from=['12345', 'alice', '67890|bob']), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:423*

### test_is_allowed_rejects_invalid_legacy_telegram_sender_shapes

**Category**: instantiation  
**Description**: Instantiate TelegramChannel: test is allowed rejects invalid legacy telegram sender shapes  
**Expected**: assert channel.is_allowed('attacker|alice|extra') is False  
**Confidence**: 0.80  

```python
channel = TelegramChannel(TelegramConfig(allow_from=['alice']), MessageBus())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:431*

### test_extract_reply_context_no_reply

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: When there is no reply_to_message, _extract_reply_context returns None.  
**Expected**: assert TelegramChannel._extract_reply_context(message) is None  
**Confidence**: 0.80  

```python
message = SimpleNamespace(reply_to_message=None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:652*

### test_extract_reply_context_with_text

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: When reply has text, return prefixed string.  
**Expected**: assert TelegramChannel._extract_reply_context(message) == '[Reply to: Hello world]'  
**Confidence**: 0.80  

```python
reply = SimpleNamespace(text='Hello world', caption=None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:658*

### test_extract_reply_context_with_text

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: When reply has text, return prefixed string.  
**Expected**: assert TelegramChannel._extract_reply_context(message) == '[Reply to: Hello world]'  
**Confidence**: 0.80  

```python
message = SimpleNamespace(reply_to_message=reply)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:659*

### test_extract_reply_context_with_caption_only

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: When reply has only caption (no text), caption is used.  
**Expected**: assert TelegramChannel._extract_reply_context(message) == '[Reply to: Photo caption]'  
**Confidence**: 0.80  

```python
reply = SimpleNamespace(text=None, caption='Photo caption')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:665*

### test_extract_reply_context_with_caption_only

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: When reply has only caption (no text), caption is used.  
**Expected**: assert TelegramChannel._extract_reply_context(message) == '[Reply to: Photo caption]'  
**Confidence**: 0.80  

```python
message = SimpleNamespace(reply_to_message=reply)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:666*

### test_extract_reply_context_truncation

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: Reply text is truncated at TELEGRAM_REPLY_CONTEXT_MAX_LEN.  
**Expected**: assert result is not None  
**Confidence**: 0.80  

```python
reply = SimpleNamespace(text=long_text, caption=None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_telegram_channel.py:673*

### test_parse_md_table_strips_markdown_formatting_in_headers_and_cells

**Category**: instantiation  
**Description**: Instantiate _parse_md_table: test parse md table strips markdown formatting in headers and cells  
**Expected**: assert table is not None  
**Confidence**: 0.80  

```python
table = FeishuChannel._parse_md_table('\n| **Name** | __Status__ | *Notes* | ~~State~~ |\n| --- | --- | --- | --- |\n| **Alice** | __Ready__ | *Fast* | ~~Old~~ |\n')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_markdown_rendering.py:16*

### test_split_headings_strips_embedded_markdown_before_bolding

**Category**: instantiation  
**Description**: Instantiate __new__: test split headings strips embedded markdown before bolding  
**Expected**: assert elements == [{'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**Important status update**'}}]  
**Confidence**: 0.80  

```python
channel = FeishuChannel.__new__(FeishuChannel)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_markdown_rendering.py:37*

### test_split_headings_strips_embedded_markdown_before_bolding

**Category**: instantiation  
**Description**: Instantiate _split_headings: test split headings strips embedded markdown before bolding  
**Expected**: assert elements == [{'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**Important status update**'}}]  
**Confidence**: 0.80  

```python
elements = channel._split_headings('# **Important** *status* ~~update~~')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_markdown_rendering.py:39*

### test_split_headings_keeps_markdown_body_and_code_blocks_intact

**Category**: instantiation  
**Description**: Instantiate __new__: test split headings keeps markdown body and code blocks intact  
**Expected**: assert elements[0] == {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**Heading**'}}  
**Confidence**: 0.80  

```python
channel = FeishuChannel.__new__(FeishuChannel)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_markdown_rendering.py:53*

### test_split_headings_keeps_markdown_body_and_code_blocks_intact

**Category**: instantiation  
**Description**: Instantiate _split_headings: test split headings keeps markdown body and code blocks intact  
**Expected**: assert elements[0] == {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**Heading**'}}  
**Confidence**: 0.80  

```python
elements = channel._split_headings("# **Heading**\n\nBody with **bold** text.\n\n```python\nprint('hi')\n```")
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_markdown_rendering.py:55*

### test_supports_streaming_when_enabled

**Category**: instantiation  
**Description**: Instantiate _make_channel: test supports streaming when enabled  
**Expected**: assert ch.supports_streaming is True  
**Confidence**: 0.80  

```python
ch = _make_channel(streaming=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:53*

### test_supports_streaming_disabled

**Category**: instantiation  
**Description**: Instantiate _make_channel: test supports streaming disabled  
**Expected**: assert ch.supports_streaming is False  
**Confidence**: 0.80  

```python
ch = _make_channel(streaming=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:57*

### test_returns_card_id_on_success

**Category**: instantiation  
**Description**: Instantiate _mock_create_card_response: test returns card id on success  
**Expected**: assert result == 'card_123'  
**Confidence**: 0.80  
**Tags**: mock  

```python
ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response('card_123')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:64*

### test_returns_card_id_on_success

**Category**: instantiation  
**Description**: Instantiate _create_streaming_card_sync: test returns card id on success  
**Expected**: assert result == 'card_123'  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = ch._create_streaming_card_sync('chat_id', 'oc_chat1')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:66*

### test_returns_none_on_exception

**Category**: instantiation  
**Description**: Instantiate RuntimeError: test returns none on exception  
**Expected**: assert ch._create_streaming_card_sync('chat_id', 'oc_chat1') is None  
**Confidence**: 0.80  

```python
ch._client.cardkit.v1.card.create.side_effect = RuntimeError('network')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:82*

### test_returns_none_when_card_send_fails

**Category**: instantiation  
**Description**: Instantiate _mock_create_card_response: test returns none when card send fails  
**Expected**: assert ch._create_streaming_card_sync('chat_id', 'oc_chat1') is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response('card_123')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:87*

### test_returns_true_on_success

**Category**: instantiation  
**Description**: Instantiate _mock_content_response: test returns true on success  
**Expected**: assert ch._close_streaming_mode_sync('card_1', 10) is True  
**Confidence**: 0.80  
**Tags**: mock  

```python
ch._client.cardkit.v1.card.settings.return_value = _mock_content_response(True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:100*

### test_returns_false_on_failure

**Category**: instantiation  
**Description**: Instantiate _mock_content_response: test returns false on failure  
**Expected**: assert ch._close_streaming_mode_sync('card_1', 10) is False  
**Confidence**: 0.80  
**Tags**: mock  

```python
ch._client.cardkit.v1.card.settings.return_value = _mock_content_response(False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_streaming.py:105*

### test_get_history_drops_orphan_tool_results_when_window_cuts_tool_calls

**Category**: instantiation  
**Description**: Instantiate Session: test get history drops orphan tool results when window cuts tool calls  
**Expected**: _assert_no_orphans(history)  
**Confidence**: 0.80  

```python
session = Session(key='telegram:test')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:37*

### test_get_history_drops_orphan_tool_results_when_window_cuts_tool_calls

**Category**: instantiation  
**Description**: Instantiate get_history: test get history drops orphan tool results when window cuts tool calls  
**Expected**: _assert_no_orphans(history)  
**Confidence**: 0.80  

```python
history = session.get_history(max_messages=100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:46*

### test_legitimate_tool_pairs_preserved_after_trim

**Category**: instantiation  
**Description**: Instantiate Session: Complete tool-call groups within the window must not be dropped.  
**Expected**: _assert_no_orphans(history)  
**Confidence**: 0.80  

```python
session = Session(key='test:positive')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:54*

### test_legitimate_tool_pairs_preserved_after_trim

**Category**: instantiation  
**Description**: Instantiate get_history: Complete tool-call groups within the window must not be dropped.  
**Expected**: _assert_no_orphans(history)  
**Confidence**: 0.80  

```python
history = session.get_history(max_messages=500)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\agent\test_session_manager_history.py:60*

### test_two_tables_split_into_two_groups

**Category**: config  
**Description**: Configuration example: test two tables split into two groups  
**Expected**: assert len(result) == 2  
**Confidence**: 0.75  

```python
t1 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'A', 'width': 'auto'}], 'rows': [{'c0': 'table-one'}], 'page_size': 2}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:58*

### test_two_tables_split_into_two_groups

**Category**: config  
**Description**: Configuration example: test two tables split into two groups  
**Expected**: assert len(result) == 2  
**Confidence**: 0.75  

```python
t2 = {'tag': 'table', 'columns': [{'tag': 'column', 'name': 'c0', 'display_name': 'B', 'width': 'auto'}], 'rows': [{'c0': 'table-two'}], 'page_size': 2}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_table_split.py:64*

### test_extract_post_content_keeps_direct_shape_behavior

**Category**: config  
**Description**: Configuration example: test extract post content keeps direct shape behavior  
**Expected**: assert text == 'Daily report'  
**Confidence**: 0.75  

```python
payload = {'title': 'Daily', 'content': [[{'tag': 'text', 'text': 'report'}, {'tag': 'img', 'image_key': 'img_a'}, {'tag': 'img', 'image_key': 'img_b'}]]}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-nanobot-c9d7c228\tests\channels\test_feishu_post_content.py:37*

