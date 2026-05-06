# How To: Forgetting Drift In Langevin

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Low-retention fact produces forgetting_drift > 0 and higher
effective_temperature. Verify lambda_forget = (1 - R) * drift_scale.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.dynamics.ebbinghaus_langevin_coupling`
- `superlocalmemory.dynamics.fisher_langevin_coupling`
- `superlocalmemory.math.ebbinghaus`
- `superlocalmemory.math.langevin`

**Setup Required:**
```python
# Fixtures: coupling
```

## Step-by-Step Guide

### Step 1: 'Low-retention fact produces forgetting_drift > 0 and higher\n    effective_temperature. Verify lambda_forget = (1 - R) * drift_scale.'

```python
'Low-retention fact produces forgetting_drift > 0 and higher\n    effective_temperature. Verify lambda_forget = (1 - R) * drift_scale.'
```

**Verification:**
```python
assert state_low.forgetting_drift > state_high.forgetting_drift, 'Low retention should produce higher forgetting drift'
```

### Step 2: Assign config = value

```python
config = coupling._config
```

**Verification:**
```python
assert state_low.forgetting_drift > 0.0, 'Forgetting drift should be positive'
```

### Step 3: Assign fisher_var = np.array(...)

```python
fisher_var = np.array([1.0] * 8)
```

**Verification:**
```python
assert state_low.forgetting_drift == pytest.approx(expected_drift, abs=1e-09), f'Expected drift {expected_drift}, got {state_low.forgetting_drift}'
```

### Step 4: Assign state_low = coupling.compute_coupled_state(...)

```python
state_low = coupling.compute_coupled_state(fact_id='fact_drift', fisher_variance=fisher_var, langevin_radius=0.5, access_count=0, importance=0.0, confirmation_count=0, emotional_salience=0.0, hours_since_last_access=500.0)
```

### Step 5: Assign state_high = coupling.compute_coupled_state(...)

```python
state_high = coupling.compute_coupled_state(fact_id='fact_no_drift', fisher_variance=fisher_var, langevin_radius=0.5, access_count=50, importance=0.9, confirmation_count=10, emotional_salience=0.5, hours_since_last_access=0.5)
```

**Verification:**
```python
assert state_low.forgetting_drift > state_high.forgetting_drift, 'Low retention should produce higher forgetting drift'
```

### Step 6: Assign expected_drift = value

```python
expected_drift = (1.0 - state_low.retention_score) * config.forgetting_drift_scale
```

**Verification:**
```python
assert state_low.forgetting_drift == pytest.approx(expected_drift, abs=1e-09), f'Expected drift {expected_drift}, got {state_low.forgetting_drift}'
```


## Complete Example

```python
# Setup
# Fixtures: coupling

# Workflow
'Low-retention fact produces forgetting_drift > 0 and higher\n    effective_temperature. Verify lambda_forget = (1 - R) * drift_scale.'
config = coupling._config
fisher_var = np.array([1.0] * 8)
state_low = coupling.compute_coupled_state(fact_id='fact_drift', fisher_variance=fisher_var, langevin_radius=0.5, access_count=0, importance=0.0, confirmation_count=0, emotional_salience=0.0, hours_since_last_access=500.0)
state_high = coupling.compute_coupled_state(fact_id='fact_no_drift', fisher_variance=fisher_var, langevin_radius=0.5, access_count=50, importance=0.9, confirmation_count=10, emotional_salience=0.5, hours_since_last_access=0.5)
assert state_low.forgetting_drift > state_high.forgetting_drift, 'Low retention should produce higher forgetting drift'
assert state_low.forgetting_drift > 0.0, 'Forgetting drift should be positive'
expected_drift = (1.0 - state_low.retention_score) * config.forgetting_drift_scale
assert state_low.forgetting_drift == pytest.approx(expected_drift, abs=1e-09), f'Expected drift {expected_drift}, got {state_low.forgetting_drift}'
```

## Next Steps


---

*Source: test_ebbinghaus_langevin.py:150 | Complexity: Intermediate | Last updated: 2026-05-05*