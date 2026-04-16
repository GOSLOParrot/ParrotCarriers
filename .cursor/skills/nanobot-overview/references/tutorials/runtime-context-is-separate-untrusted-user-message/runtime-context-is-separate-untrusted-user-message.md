# How To: Runtime Context Is Separate Untrusted User Message

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Runtime metadata should be merged with the user message.

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Runtime metadata should be merged with the user message.'

```python
'Runtime metadata should be merged with the user message.'
```

**Verification:**
```python
assert messages[0]['role'] == 'system'
```

### Step 2: Assign workspace = _make_workspace(...)

```python
workspace = _make_workspace(tmp_path)
```

**Verification:**
```python
assert '## Current Session' not in messages[0]['content']
```

### Step 3: Assign builder = ContextBuilder(...)

```python
builder = ContextBuilder(workspace)
```

**Verification:**
```python
assert messages[-1]['role'] == 'user'
```

### Step 4: Assign messages = builder.build_messages(...)

```python
messages = builder.build_messages(history=[], current_message='Return exactly: OK', channel='cli', chat_id='direct')
```

**Verification:**
```python
assert isinstance(user_content, str)
```

### Step 5: Assign user_content = value

```python
user_content = messages[-1]['content']
```

**Verification:**
```python
assert ContextBuilder._RUNTIME_CONTEXT_TAG in user_content
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
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

## Next Steps


---

*Source: test_context_prompt_cache.py:50 | Complexity: Intermediate | Last updated: 2026-04-12*