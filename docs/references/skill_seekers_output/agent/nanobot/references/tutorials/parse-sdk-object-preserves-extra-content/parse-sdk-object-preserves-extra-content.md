# How To: Parse Sdk Object Preserves Extra Content

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test parse sdk object preserves extra content

## Prerequisites

**Required Modules:**
- `types`
- `unittest.mock`
- `nanobot.providers.base`
- `nanobot.providers.openai_compat_provider`


## Step-by-Step Guide

### Step 1: Assign result = provider._parse(...)

```python
result = provider._parse(_make_sdk_response_with_extra_content())
```

**Verification:**
```python
assert len(result.tool_calls) == 1
```

### Step 2: Assign tc = value

```python
tc = result.tool_calls[0]
```

**Verification:**
```python
assert tc.name == 'get_weather'
```

### Step 3: Assign payload = tc.to_openai_tool_call(...)

```python
payload = tc.to_openai_tool_call()
```

**Verification:**
```python
assert tc.extra_content == GEMINI_EXTRA
```

### Step 4: Assign provider = OpenAICompatProvider(...)

```python
provider = OpenAICompatProvider()
```

**Verification:**
```python
assert payload['extra_content'] == GEMINI_EXTRA
```


## Complete Example

```python
# Workflow
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

## Next Steps


---

*Source: test_gemini_thought_signature.py:80 | Complexity: Intermediate | Last updated: 2026-04-12*