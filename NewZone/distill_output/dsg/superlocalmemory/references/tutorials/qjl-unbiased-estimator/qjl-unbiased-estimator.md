# How To: Qjl Unbiased Estimator

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Over 200 trials with different seeds, mean estimate ~ true IP.

|E[estimate] - true_ip| < 0.15 for projection_dim=256.

## Prerequisites

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.qjl`
- `superlocalmemory.math.polar_quant`


## Step-by-Step Guide

### Step 1: 'Over 200 trials with different seeds, mean estimate ~ true IP.\n\n    |E[estimate] - true_ip| < 0.15 for projection_dim=256.\n    '

```python
'Over 200 trials with different seeds, mean estimate ~ true IP.\n\n    |E[estimate] - true_ip| < 0.15 for projection_dim=256.\n    '
```

**Verification:**
```python
assert abs(mean_est - true_ip) < 0.15, f'Mean estimate={mean_est:.4f}, true IP={true_ip:.4f}, diff={abs(mean_est - true_ip):.4f}'
```

### Step 2: Assign d = 768

```python
d = 768
```

### Step 3: Assign query = _random_vec(...)

```python
query = _random_vec(d, seed=100)
```

### Step 4: Assign target = _random_vec(...)

```python
target = _random_vec(d, seed=101)
```

### Step 5: Assign true_ip = float(...)

```python
true_ip = float(np.dot(query, target))
```

### Step 6: Assign mean_est = value

```python
mean_est = sum(estimates) / len(estimates)
```

**Verification:**
```python
assert abs(mean_est - true_ip) < 0.15, f'Mean estimate={mean_est:.4f}, true IP={true_ip:.4f}, diff={abs(mean_est - true_ip):.4f}'
```

### Step 7: Assign cfg = QJLConfig(...)

```python
cfg = QJLConfig(projection_dim=256, seed=trial_seed)
```

### Step 8: Assign enc = QJLEncoder(...)

```python
enc = QJLEncoder(cfg)
```

### Step 9: Assign bits = enc.encode_residual(...)

```python
bits = enc.encode_residual(target)
```

### Step 10: Assign est = enc.estimate_correction(...)

```python
est = enc.estimate_correction(query, bits)
```

### Step 11: Call estimates.append()

```python
estimates.append(est)
```


## Complete Example

```python
# Workflow
'Over 200 trials with different seeds, mean estimate ~ true IP.\n\n    |E[estimate] - true_ip| < 0.15 for projection_dim=256.\n    '
d = 768
query = _random_vec(d, seed=100)
target = _random_vec(d, seed=101)
true_ip = float(np.dot(query, target))
estimates: list[float] = []
for trial_seed in range(200):
    cfg = QJLConfig(projection_dim=256, seed=trial_seed)
    enc = QJLEncoder(cfg)
    bits = enc.encode_residual(target)
    est = enc.estimate_correction(query, bits)
    estimates.append(est)
mean_est = sum(estimates) / len(estimates)
assert abs(mean_est - true_ip) < 0.15, f'Mean estimate={mean_est:.4f}, true IP={true_ip:.4f}, diff={abs(mean_est - true_ip):.4f}'
```

## Next Steps


---

*Source: test_qjl.py:63 | Complexity: Advanced | Last updated: 2026-05-05*