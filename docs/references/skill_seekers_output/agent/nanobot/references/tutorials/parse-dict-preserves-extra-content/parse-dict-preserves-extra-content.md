# How To: Parse Dict Preserves Extra Content

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test parse dict preserves extra content

## Prerequisites

**Required Modules:**
- `types`
- `unittest.mock`
- `nanobot.providers.base`
- `nanobot.providers.openai_compat_provider`


## Step-by-Step Guide

### Step 1: Assign response_dict = value

```python
response_dict = {'choices': [{'message': {'content': None, 'tool_calls': [{'id': 'call_1', 'type': 'function', 'function': {'name': 'get_weather', 'arguments': '{"city":"Tokyo"}'}, 'extra_content': GEMINI_EXTRA}]}, 'finish_reason': 'tool_calls'}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
```

**Verification:**
```python
assert len(result.tool_calls) == 1
```

### Step 2: Assign result = provider._parse(...)

```python
result = provider._parse(response_dict)
```

**Verification:**
```python
assert tc.name == 'get_weather'
```

### Step 3: Assign tc = value

```python
tc = result.tool_calls[0]
```

**Verification:**
```python
assert tc.extra_content == GEMINI_EXTRA
```

### Step 4: Assign payload = tc.to_openai_tool_call(...)

```python
payload = tc.to_openai_tool_call()
```

**Verification:**
```python
assert payload['extra_content'] == GEMINI_EXTRA
```

### Step 5: Assign provider = OpenAICompatProvider(...)

```python
provider = OpenAICompatProvider()
```


## Complete Example

```python
# Workflow
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

## Next Steps


---

*Source: test_gemini_thought_signature.py:97 | Complexity: Intermediate | Last updated: 2026-04-12*