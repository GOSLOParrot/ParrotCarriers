# How To: System Prompt Stays Stable When Clock Changes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: System prompt should not change just because wall clock minute changes.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `datetime`
- `importlib.resources`
- `pathlib`
- `datetime`
- `nanobot.agent.context`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'System prompt should not change just because wall clock minute changes.'

```python
'System prompt should not change just because wall clock minute changes.'
```

**Verification:**
```python
assert prompt1 == prompt2
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(datetime_module, 'datetime', _FakeDatetime)
```

### Step 3: Assign workspace = _make_workspace(...)

```python
workspace = _make_workspace(tmp_path)
```

### Step 4: Assign builder = ContextBuilder(...)

```python
builder = ContextBuilder(workspace)
```

### Step 5: Assign _FakeDatetime.current = real_datetime(...)

```python
_FakeDatetime.current = real_datetime(2026, 2, 24, 13, 59)
```

### Step 6: Assign prompt1 = builder.build_system_prompt(...)

```python
prompt1 = builder.build_system_prompt()
```

### Step 7: Assign _FakeDatetime.current = real_datetime(...)

```python
_FakeDatetime.current = real_datetime(2026, 2, 24, 14, 0)
```

### Step 8: Assign prompt2 = builder.build_system_prompt(...)

```python
prompt2 = builder.build_system_prompt()
```

**Verification:**
```python
assert prompt1 == prompt2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
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

## Next Steps


---

*Source: test_context_prompt_cache.py:34 | Complexity: Advanced | Last updated: 2026-04-12*