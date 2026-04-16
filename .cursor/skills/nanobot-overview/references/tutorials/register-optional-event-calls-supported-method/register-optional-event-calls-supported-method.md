# How To: Register Optional Event Calls Supported Method

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test register optional event calls supported method

## Prerequisites

**Required Modules:**
- `nanobot.channels.feishu`
- `nanobot.channels`
- `pytest`


## Step-by-Step Guide

### Step 1: Assign called = value

```python
called = []
```

**Verification:**
```python
assert same is builder
```

### Step 2: Assign builder = Builder(...)

```python
builder = Builder()
```

**Verification:**
```python
assert called == [handler]
```

### Step 3: Assign handler = object(...)

```python
handler = object()
```

### Step 4: Assign same = FeishuChannel._register_optional_event(...)

```python
same = FeishuChannel._register_optional_event(builder, 'register_event', handler)
```

**Verification:**
```python
assert same is builder
```

### Step 5: Call called.append()

```python
called.append(handler)
```


## Complete Example

```python
# Workflow
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

## Next Steps


---

*Source: test_feishu_post_content.py:63 | Complexity: Intermediate | Last updated: 2026-04-12*