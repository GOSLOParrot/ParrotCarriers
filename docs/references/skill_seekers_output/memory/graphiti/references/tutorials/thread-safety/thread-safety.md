# How To: Thread Safety

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that concurrent access from multiple threads is safe.

## Prerequisites

**Required Modules:**
- `concurrent.futures`
- `graphiti_core.llm_client.token_tracker`


## Step-by-Step Guide

### Step 1: 'Test that concurrent access from multiple threads is safe.'

```python
'Test that concurrent access from multiple threads is safe.'
```

**Verification:**
```python
assert len(usage) == num_threads
```

### Step 2: Assign tracker = TokenUsageTracker(...)

```python
tracker = TokenUsageTracker()
```

**Verification:**
```python
assert total.input_tokens == expected_input
```

### Step 3: Assign num_threads = 10

```python
num_threads = 10
```

**Verification:**
```python
assert total.output_tokens == expected_output
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
assert len(usage) == num_threads
```

### Step 6: Assign total = tracker.get_total_usage(...)

```python
total = tracker.get_total_usage()
```

### Step 7: Assign expected_input = value

```python
expected_input = num_threads * calls_per_thread * 10
```

### Step 8: Assign expected_output = value

```python
expected_output = num_threads * calls_per_thread * 5
```

**Verification:**
```python
assert total.input_tokens == expected_input
```

### Step 9: Assign futures = value

```python
futures = [executor.submit(record_tokens, i) for i in range(num_threads)]
```

### Step 10: Call tracker.record()

```python
tracker.record(f'prompt_{thread_id}', 10, 5)
```

### Step 11: Call f.result()

```python
f.result()
```


## Complete Example

```python
# Workflow
'Test that concurrent access from multiple threads is safe.'
tracker = TokenUsageTracker()
num_threads = 10
calls_per_thread = 100

def record_tokens(thread_id):
    for _ in range(calls_per_thread):
        tracker.record(f'prompt_{thread_id}', 10, 5)
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(record_tokens, i) for i in range(num_threads)]
    for f in futures:
        f.result()
usage = tracker.get_usage()
assert len(usage) == num_threads
total = tracker.get_total_usage()
expected_input = num_threads * calls_per_thread * 10
expected_output = num_threads * calls_per_thread * 5
assert total.input_tokens == expected_input
assert total.output_tokens == expected_output
```

## Next Steps


---

*Source: test_token_tracker.py:172 | Complexity: Advanced | Last updated: 2026-04-12*