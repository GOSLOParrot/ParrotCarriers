# How To: Concurrent Same Prompt

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test concurrent access to the same prompt name.

## Prerequisites

**Required Modules:**
- `concurrent.futures`
- `graphiti_core.llm_client.token_tracker`


## Step-by-Step Guide

### Step 1: 'Test concurrent access to the same prompt name.'

```python
'Test concurrent access to the same prompt name.'
```

**Verification:**
```python
assert usage['shared_prompt'].call_count == num_threads * calls_per_thread
```

### Step 2: Assign tracker = TokenUsageTracker(...)

```python
tracker = TokenUsageTracker()
```

**Verification:**
```python
assert usage['shared_prompt'].total_input_tokens == num_threads * calls_per_thread * 10
```

### Step 3: Assign num_threads = 10

```python
num_threads = 10
```

**Verification:**
```python
assert usage['shared_prompt'].total_output_tokens == num_threads * calls_per_thread * 5
```

### Step 4: Assign calls_per_thread = 100

```python
calls_per_thread = 100
```

### Step 5: Assign usage = tracker.get_usage(...)

```python
usage = tracker.get_usage()
```

**Verification:**
```python
assert usage['shared_prompt'].call_count == num_threads * calls_per_thread
```

### Step 6: Assign futures = value

```python
futures = [executor.submit(record_tokens) for _ in range(num_threads)]
```

### Step 7: Call tracker.record()

```python
tracker.record('shared_prompt', 10, 5)
```

### Step 8: Call f.result()

```python
f.result()
```


## Complete Example

```python
# Workflow
'Test concurrent access to the same prompt name.'
tracker = TokenUsageTracker()
num_threads = 10
calls_per_thread = 100

def record_tokens():
    for _ in range(calls_per_thread):
        tracker.record('shared_prompt', 10, 5)
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(record_tokens) for _ in range(num_threads)]
    for f in futures:
        f.result()
usage = tracker.get_usage()
assert usage['shared_prompt'].call_count == num_threads * calls_per_thread
assert usage['shared_prompt'].total_input_tokens == num_threads * calls_per_thread * 10
assert usage['shared_prompt'].total_output_tokens == num_threads * calls_per_thread * 5
```

## Next Steps


---

*Source: test_token_tracker.py:196 | Complexity: Advanced | Last updated: 2026-04-12*