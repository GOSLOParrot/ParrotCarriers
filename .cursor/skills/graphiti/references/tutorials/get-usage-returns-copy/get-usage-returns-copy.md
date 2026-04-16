# How To: Get Usage Returns Copy

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that get_usage returns a copy, not the internal dict.

## Prerequisites

**Required Modules:**
- `concurrent.futures`
- `graphiti_core.llm_client.token_tracker`


## Step-by-Step Guide

### Step 1: 'Test that get_usage returns a copy, not the internal dict.'

```python
'Test that get_usage returns a copy, not the internal dict.'
```

**Verification:**
```python
assert usage2['test'].total_input_tokens == 100
```

### Step 2: Assign tracker = TokenUsageTracker(...)

```python
tracker = TokenUsageTracker()
```

### Step 3: Call tracker.record()

```python
tracker.record('test', 100, 50)
```

### Step 4: Assign usage1 = tracker.get_usage(...)

```python
usage1 = tracker.get_usage()
```

### Step 5: Assign unknown.total_input_tokens = 9999

```python
usage1['test'].total_input_tokens = 9999
```

### Step 6: Assign usage2 = tracker.get_usage(...)

```python
usage2 = tracker.get_usage()
```

**Verification:**
```python
assert usage2['test'].total_input_tokens == 100
```


## Complete Example

```python
# Workflow
'Test that get_usage returns a copy, not the internal dict.'
tracker = TokenUsageTracker()
tracker.record('test', 100, 50)
usage1 = tracker.get_usage()
usage1['test'].total_input_tokens = 9999
usage2 = tracker.get_usage()
assert usage2['test'].total_input_tokens == 100
```

## Next Steps


---

*Source: test_token_tracker.py:128 | Complexity: Intermediate | Last updated: 2026-04-12*