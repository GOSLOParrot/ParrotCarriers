# How To: Make Headers Includes Route Tag When Configured

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test make headers includes route tag when configured

## Prerequisites

**Required Modules:**
- `asyncio`
- `json`
- `tempfile`
- `types`
- `unittest.mock`
- `pytest`
- `nanobot.bus.queue`
- `nanobot.channels.weixin`


## Step-by-Step Guide

### Step 1: Assign bus = MessageBus(...)

```python
bus = MessageBus()
```

**Verification:**
```python
assert headers['Authorization'] == 'Bearer token'
```

### Step 2: Assign channel = WeixinChannel(...)

```python
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], route_tag=123), bus)
```

**Verification:**
```python
assert headers['SKRouteTag'] == '123'
```

### Step 3: Assign channel._token = 'token'

```python
channel._token = 'token'
```

### Step 4: Assign headers = channel._make_headers(...)

```python
headers = channel._make_headers()
```

**Verification:**
```python
assert headers['Authorization'] == 'Bearer token'
```


## Complete Example

```python
# Workflow
bus = MessageBus()
channel = WeixinChannel(WeixinConfig(enabled=True, allow_from=['*'], route_tag=123), bus)
channel._token = 'token'
headers = channel._make_headers()
assert headers['Authorization'] == 'Bearer token'
assert headers['SKRouteTag'] == '123'
```

## Next Steps


---

*Source: test_weixin_channel.py:33 | Complexity: Intermediate | Last updated: 2026-04-12*