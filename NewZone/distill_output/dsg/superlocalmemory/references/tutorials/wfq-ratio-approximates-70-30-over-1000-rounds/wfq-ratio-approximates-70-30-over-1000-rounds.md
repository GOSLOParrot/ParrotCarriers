# How To: Wfq Ratio Approximates 70 30 Over 1000 Rounds

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test wfq ratio approximates 70 30 over 1000 rounds

## Prerequisites

**Required Modules:**
- `__future__`
- `superlocalmemory.core`


## Step-by-Step Guide

### Step 1: Assign pq = _imports(...)

```python
pq = _imports()
```

**Verification:**
```python
assert 67 <= high_pct <= 73, f'high lane got {high_pct}% (expected ~70)'
```

### Step 2: Assign sched = pq.WFQScheduler(...)

```python
sched = pq.WFQScheduler()
```

### Step 3: Assign counts = value

```python
counts = {'high': 0, 'low': 0}
```

### Step 4: Assign high_pct = value

```python
high_pct = counts['high'] / 1000 * 100
```

**Verification:**
```python
assert 67 <= high_pct <= 73, f'high lane got {high_pct}% (expected ~70)'
```

### Step 5: Assign lane = sched.pick_lane(...)

```python
lane = sched.pick_lane(has_high=True, has_low=True)
```

### Step 6: Call sched.record_served()

```python
sched.record_served(lane)
```


## Complete Example

```python
# Workflow
pq = _imports()
sched = pq.WFQScheduler()
counts = {'high': 0, 'low': 0}
for _ in range(1000):
    lane = sched.pick_lane(has_high=True, has_low=True)
    sched.record_served(lane)
    counts[lane] += 1
high_pct = counts['high'] / 1000 * 100
assert 67 <= high_pct <= 73, f'high lane got {high_pct}% (expected ~70)'
```

## Next Steps


---

*Source: test_priority_queue.py:40 | Complexity: Intermediate | Last updated: 2026-05-05*