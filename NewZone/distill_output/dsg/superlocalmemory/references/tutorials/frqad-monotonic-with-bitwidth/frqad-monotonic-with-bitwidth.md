# How To: Frqad Monotonic With Bitwidth

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Similarity: 32-bit > 8-bit > 4-bit > 2-bit.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`
- `superlocalmemory.math.fisher_quantized`

**Setup Required:**
```python
# Fixtures: frqad, embedding_pair
```

## Step-by-Step Guide

### Step 1: 'Similarity: 32-bit > 8-bit > 4-bit > 2-bit.'

```python
'Similarity: 32-bit > 8-bit > 4-bit > 2-bit.'
```

**Verification:**
```python
assert sim_32 > sim_2 - 0.01, f'32-bit must beat 2-bit: {sim_32} vs {sim_2}'
```

### Step 2: Assign unknown = embedding_pair

```python
mu_a, var_a, mu_b, var_b = embedding_pair
```

### Step 3: Assign sim_32 = frqad.similarity(...)

```python
sim_32 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 32)
```

### Step 4: Assign sim_8 = frqad.similarity(...)

```python
sim_8 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 8)
```

### Step 5: Assign sim_4 = frqad.similarity(...)

```python
sim_4 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 4)
```

### Step 6: Assign sim_2 = frqad.similarity(...)

```python
sim_2 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 2)
```

**Verification:**
```python
assert sim_32 > sim_2 - 0.01, f'32-bit must beat 2-bit: {sim_32} vs {sim_2}'
```


## Complete Example

```python
# Setup
# Fixtures: frqad, embedding_pair

# Workflow
'Similarity: 32-bit > 8-bit > 4-bit > 2-bit.'
mu_a, var_a, mu_b, var_b = embedding_pair
sim_32 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 32)
sim_8 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 8)
sim_4 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 4)
sim_2 = frqad.similarity(mu_a, var_a, 32, mu_b, var_b, 2)
assert sim_32 > sim_2 - 0.01, f'32-bit must beat 2-bit: {sim_32} vs {sim_2}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:210 | Complexity: Intermediate | Last updated: 2026-05-05*