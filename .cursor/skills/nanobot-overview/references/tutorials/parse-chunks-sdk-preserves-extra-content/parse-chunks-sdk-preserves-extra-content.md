# How To: Parse Chunks Sdk Preserves Extra Content

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test parse chunks sdk preserves extra content

## Prerequisites

**Required Modules:**
- `types`
- `unittest.mock`
- `nanobot.providers.base`
- `nanobot.providers.openai_compat_provider`


## Step-by-Step Guide

### Step 1: Assign fn_delta = SimpleNamespace(...)

```python
fn_delta = SimpleNamespace(name='get_weather', arguments='{"city":"Tokyo"}')
```

**Verification:**
```python
assert len(result.tool_calls) == 1
```

### Step 2: Assign tc_delta = SimpleNamespace(...)

```python
tc_delta = SimpleNamespace(id='call_1', index=0, function=fn_delta, extra_content=GEMINI_EXTRA)
```

**Verification:**
```python
assert tc.extra_content == GEMINI_EXTRA
```

### Step 3: Assign delta = SimpleNamespace(...)

```python
delta = SimpleNamespace(content=None, tool_calls=[tc_delta])
```

**Verification:**
```python
assert payload['extra_content'] == GEMINI_EXTRA
```

### Step 4: Assign choice = SimpleNamespace(...)

```python
choice = SimpleNamespace(finish_reason='tool_calls', delta=delta)
```

### Step 5: Assign chunk = SimpleNamespace(...)

```python
chunk = SimpleNamespace(choices=[choice], usage=None)
```

### Step 6: Assign result = OpenAICompatProvider._parse_chunks(...)

```python
result = OpenAICompatProvider._parse_chunks([chunk])
```

**Verification:**
```python
assert len(result.tool_calls) == 1
```

### Step 7: Assign tc = value

```python
tc = result.tool_calls[0]
```

**Verification:**
```python
assert tc.extra_content == GEMINI_EXTRA
```

### Step 8: Assign payload = tc.to_openai_tool_call(...)

```python
payload = tc.to_openai_tool_call()
```

**Verification:**
```python
assert payload['extra_content'] == GEMINI_EXTRA
```


## Complete Example

```python
# Workflow
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

## Next Steps


---

*Source: test_gemini_thought_signature.py:130 | Complexity: Advanced | Last updated: 2026-04-12*