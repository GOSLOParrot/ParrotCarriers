# How To: Hook Cold Start Under Budget

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: test hook cold start under budget

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `os`
- `platform`
- `subprocess`
- `sys`
- `time`
- `pytest`

**Setup Required:**
```python
# Fixtures: module_name
```

## Step-by-Step Guide

### Step 1: Assign budget = _budget_ms(...)

```python
budget = _budget_ms()
```

**Verification:**
```python
assert p95 < budget, f'{module_name} cold-start p95={p95:.1f}ms exceeds budget={budget:.0f}ms. All runs: {durations}'
```

### Step 2: Assign durations = _measure_cold_start(...)

```python
durations = _measure_cold_start(module_name)
```

### Step 3: Assign p95 = _p95(...)

```python
p95 = _p95(durations)
```

### Step 4: Assign mean = value

```python
mean = sum(durations) / len(durations)
```

### Step 5: Call print()

```python
print(f'[hook-coldstart] {module_name}: mean={mean:.1f}ms p95={p95:.1f}ms runs={durations} budget={budget:.0f}ms')
```

**Verification:**
```python
assert p95 < budget, f'{module_name} cold-start p95={p95:.1f}ms exceeds budget={budget:.0f}ms. All runs: {durations}'
```


## Complete Example

```python
# Setup
# Fixtures: module_name

# Workflow
budget = _budget_ms()
durations = _measure_cold_start(module_name)
p95 = _p95(durations)
mean = sum(durations) / len(durations)
print(f'[hook-coldstart] {module_name}: mean={mean:.1f}ms p95={p95:.1f}ms runs={durations} budget={budget:.0f}ms')
assert p95 < budget, f'{module_name} cold-start p95={p95:.1f}ms exceeds budget={budget:.0f}ms. All runs: {durations}'
```

## Next Steps


---

*Source: test_hook_cold_start.py:112 | Complexity: Intermediate | Last updated: 2026-05-05*