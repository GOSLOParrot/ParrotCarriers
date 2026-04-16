# How To: Prepare Request Payload

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test request payload preparation with Azure OpenAI 2024-10-21 compliance.

## Prerequisites

**Required Modules:**
- `unittest.mock`
- `pytest`
- `nanobot.providers.azure_openai_provider`
- `nanobot.providers.base`


## Step-by-Step Guide

### Step 1: 'Test request payload preparation with Azure OpenAI 2024-10-21 compliance.'

```python
'Test request payload preparation with Azure OpenAI 2024-10-21 compliance.'
```

**Verification:**
```python
assert payload['messages'] == messages
```

### Step 2: Assign provider = AzureOpenAIProvider(...)

```python
provider = AzureOpenAIProvider(api_key='test-key', api_base='https://test-resource.openai.azure.com', default_model='gpt-4o')
```

**Verification:**
```python
assert payload['max_completion_tokens'] == 1500
```

### Step 3: Assign messages = value

```python
messages = [{'role': 'user', 'content': 'Hello'}]
```

**Verification:**
```python
assert payload['temperature'] == 0.8
```

### Step 4: Assign payload = provider._prepare_request_payload(...)

```python
payload = provider._prepare_request_payload('gpt-4o', messages, max_tokens=1500, temperature=0.8)
```

**Verification:**
```python
assert 'tools' not in payload
```

### Step 5: Assign tools = value

```python
tools = [{'type': 'function', 'function': {'name': 'get_weather', 'parameters': {}}}]
```

**Verification:**
```python
assert payload_with_tools['tools'] == tools
```

### Step 6: Assign payload_with_tools = provider._prepare_request_payload(...)

```python
payload_with_tools = provider._prepare_request_payload('gpt-4o', messages, tools=tools)
```

**Verification:**
```python
assert payload_with_tools['tool_choice'] == 'auto'
```

### Step 7: Assign payload_with_reasoning = provider._prepare_request_payload(...)

```python
payload_with_reasoning = provider._prepare_request_payload('gpt-5-chat', messages, reasoning_effort='medium')
```

**Verification:**
```python
assert payload_with_reasoning['reasoning_effort'] == 'medium'
```


## Complete Example

```python
# Workflow
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

## Next Steps


---

*Source: test_azure_openai_provider.py:83 | Complexity: Intermediate | Last updated: 2026-04-12*