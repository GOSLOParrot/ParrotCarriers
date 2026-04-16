# How To: Save And Load State Persists Context Tokens

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test save and load state persists context tokens

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `asyncio`
- `json`
- `tempfile`
- `types`
- `unittest.mock`
- `pytest`
- `nanobot.bus.queue`
- `nanobot.channels.weixin`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign bus = MessageBus(...)

```python
bus = MessageBus()
```

**Verification:**
```python
assert saved['context_tokens'] == {'wx-user': 'ctx-1'}
```

### Step 2: Assign channel = WeixinChannel(...)

```python
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
```

**Verification:**
```python
assert restored._load_state() is True
```

### Step 3: Assign channel._token = 'token'

```python
channel._token = 'token'
```

**Verification:**
```python
assert restored._context_tokens == {'wx-user': 'ctx-1'}
```

### Step 4: Assign channel._get_updates_buf = 'cursor'

```python
channel._get_updates_buf = 'cursor'
```

### Step 5: Assign channel._context_tokens = value

```python
channel._context_tokens = {'wx-user': 'ctx-1'}
```

### Step 6: Call channel._save_state()

```python
channel._save_state()
```

### Step 7: Assign saved = json.loads(...)

```python
saved = json.loads((tmp_path / 'account.json').read_text())
```

**Verification:**
```python
assert saved['context_tokens'] == {'wx-user': 'ctx-1'}
```

### Step 8: Assign restored = WeixinChannel(...)

```python
restored = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], state_dir=str(tmp_path)), bus)
```

**Verification:**
```python
assert restored._load_state() is True
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
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

## Next Steps


---

*Source: test_weixin_channel.py:51 | Complexity: Advanced | Last updated: 2026-04-12*