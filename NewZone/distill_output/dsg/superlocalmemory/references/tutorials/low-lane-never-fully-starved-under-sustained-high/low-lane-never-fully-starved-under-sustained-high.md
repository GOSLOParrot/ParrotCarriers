# How To: Low Lane Never Fully Starved Under Sustained High

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test low lane never fully starved under sustained high

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
assert counts['low'] > 20, f"Low lane starved: {counts['low']} in 100 rounds (expected ~30)"
```

### Step 2: Assign sched = pq.WFQScheduler(...)

```python
sched = pq.WFQScheduler()
```

### Step 3: Assign counts = value

```python
counts = {'high': 0, 'low': 0}
```

**Verification:**
```python
assert counts['low'] > 20, f"Low lane starved: {counts['low']} in 100 rounds (expected ~30)"
```

### Step 4: Assign lane = sched.pick_lane(...)

```python
lane = sched.pick_lane(has_high=True, has_low=True)
```

### Step 5: Call sched.record_served()

```python
sched.record_served(lane)
```


## Complete Example

```python
# Workflow
pq = _imports()
sched = pq.WFQScheduler()
counts = {'high': 0, 'low': 0}
for _ in range(100):
    lane = sched.pick_lane(has_high=True, has_low=True)
    sched.record_served(lane)
    counts[lane] += 1
assert counts['low'] > 20, f"Low lane starved: {counts['low']} in 100 rounds (expected ~30)"
```

## Next Steps


---

*Source: test_priority_queue.py:54 | Complexity: Intermediate | Last updated: 2026-05-05*