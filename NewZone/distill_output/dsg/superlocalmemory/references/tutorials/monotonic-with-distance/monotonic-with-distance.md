# How To: Monotonic With Distance

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Closer distributions should have higher similarity.

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`


## Step-by-Step Guide

### Step 1: 'Closer distributions should have higher similarity.'

```python
'Closer distributions should have higher similarity.'
```

**Verification:**
```python
assert s_near > s_far
```

### Step 2: Assign fm = FisherRaoMetric(...)

```python
fm = FisherRaoMetric()
```

### Step 3: Assign m = value

```python
m = [0.5, 0.5]
```

### Step 4: Assign v = value

```python
v = [1.0, 1.0]
```

### Step 5: Assign m_near = value

```python
m_near = [0.51, 0.51]
```

### Step 6: Assign m_far = value

```python
m_far = [5.0, 5.0]
```

### Step 7: Assign s_near = fm.similarity(...)

```python
s_near = fm.similarity(m, v, m_near, v)
```

### Step 8: Assign s_far = fm.similarity(...)

```python
s_far = fm.similarity(m, v, m_far, v)
```

**Verification:**
```python
assert s_near > s_far
```


## Complete Example

```python
# Workflow
'Closer distributions should have higher similarity.'
fm = FisherRaoMetric()
m = [0.5, 0.5]
v = [1.0, 1.0]
m_near = [0.51, 0.51]
m_far = [5.0, 5.0]
s_near = fm.similarity(m, v, m_near, v)
s_far = fm.similarity(m, v, m_far, v)
assert s_near > s_far
```

## Next Steps


---

*Source: test_fisher.py:188 | Complexity: Advanced | Last updated: 2026-05-05*