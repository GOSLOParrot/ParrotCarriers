# How To: Convergence Proof

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Run 1000 decay+access cycles. Assert retention converges to stable equilibrium.

Validates that the Ebbinghaus curve admits a numerical steady state
when alternating between decay and spaced repetition updates.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `random`
- `datetime`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.ebbinghaus`
- `statistics`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: curve
```

## Step-by-Step Guide

### Step 1: 'Run 1000 decay+access cycles. Assert retention converges to stable equilibrium.\n\n    Validates that the Ebbinghaus curve admits a numerical steady state\n    when alternating between decay and spaced repetition updates.\n    '

```python
'Run 1000 decay+access cycles. Assert retention converges to stable equilibrium.\n\n    Validates that the Ebbinghaus curve admits a numerical steady state\n    when alternating between decay and spaced repetition updates.\n    '
```

**Verification:**
```python
assert std_dev < 0.01, f'Retention did not converge: std_dev of last 100 = {std_dev:.4f}'
```

### Step 2: Assign strength = 5.0

```python
strength = 5.0
```

### Step 3: Assign last_100 = value

```python
last_100 = retentions[-100:]
```

### Step 4: Assign std_dev = statistics.stdev(...)

```python
std_dev = statistics.stdev(last_100)
```

**Verification:**
```python
assert std_dev < 0.01, f'Retention did not converge: std_dev of last 100 = {std_dev:.4f}'
```

### Step 5: Assign r = curve.retention(...)

```python
r = curve.retention(24.0, strength)
```

### Step 6: Call retentions.append()

```python
retentions.append(r)
```

### Step 7: Assign strength = curve.spaced_repetition_update(...)

```python
strength = curve.spaced_repetition_update(strength, 24.0)
```


## Complete Example

```python
# Setup
# Fixtures: curve

# Workflow
'Run 1000 decay+access cycles. Assert retention converges to stable equilibrium.\n\n    Validates that the Ebbinghaus curve admits a numerical steady state\n    when alternating between decay and spaced repetition updates.\n    '
strength = 5.0
retentions: list[float] = []
for i in range(1000):
    r = curve.retention(24.0, strength)
    retentions.append(r)
    strength = curve.spaced_repetition_update(strength, 24.0)
last_100 = retentions[-100:]
import statistics
std_dev = statistics.stdev(last_100)
assert std_dev < 0.01, f'Retention did not converge: std_dev of last 100 = {std_dev:.4f}'
```

## Next Steps


---

*Source: test_ebbinghaus.py:135 | Complexity: Intermediate | Last updated: 2026-05-05*