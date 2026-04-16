# How To: Parse Chunks Dict Preserves Extra Content

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test parse chunks dict preserves extra content

## Prerequisites

**Required Modules:**
- `types`
- `unittest.mock`
- `nanobot.providers.base`
- `nanobot.providers.openai_compat_provider`


## Step-by-Step Guide

### Step 1: Assign chunk = value

```python
chunk = {'choices': [{'finish_reason': 'tool_calls', 'delta': {'content': None, 'tool_calls': [{'index': 0, 'id': 'call_1', 'function': {'name': 'get_weather', 'arguments': '{"city":"Tokyo"}'}, 'extra_content': GEMINI_EXTRA}]}}]}
```

**Verification:**
```python
assert len(result.tool_calls) == 1
```

### Step 2: Assign result = OpenAICompatProvider._parse_chunks(...)

```python
result = OpenAICompatProvider._parse_chunks([chunk])
```

**Verification:**
```python
assert tc.extra_content == GEMINI_EXTRA
```

### Step 3: Assign tc = value

```python
tc = result.tool_calls[0]
```

**Verification:**
```python
assert payload['extra_content'] == GEMINI_EXTRA
```

### Step 4: Assign payload = tc.to_openai_tool_call(...)

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
chunk = {'choices': [{'finish_reason': 'tool_calls', 'delta': {'content': None, 'tool_calls': [{'index': 0, 'id': 'call_1', 'function': {'name': 'get_weather', 'arguments': '{"city":"Tokyo"}'}, 'extra_content': GEMINI_EXTRA}]}}]}
result = OpenAICompatProvider._parse_chunks([chunk])
assert len(result.tool_calls) == 1
tc = result.tool_calls[0]
assert tc.extra_content == GEMINI_EXTRA
payload = tc.to_openai_tool_call()
assert payload['extra_content'] == GEMINI_EXTRA
```

## Next Steps


---

*Source: test_gemini_thought_signature.py:152 | Complexity: Intermediate | Last updated: 2026-04-12*