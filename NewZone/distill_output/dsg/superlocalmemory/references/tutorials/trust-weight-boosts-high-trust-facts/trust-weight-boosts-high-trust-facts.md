# How To: Trust Weight Boosts High Trust Facts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: trust=1.0 maps to weight=1.5, boosting the fact's score.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: "trust=1.0 maps to weight=1.5, boosting the fact's score."

```python
"trust=1.0 maps to weight=1.5, boosting the fact's score."
```

**Verification:**
```python
assert scores['f_high'] > scores['f_low']
```

### Step 2: Assign f_high = _make_fact(...)

```python
f_high = _make_fact('f_high', 'High-trust fact with comprehensive verified evidence')
```

### Step 3: Assign f_low = _make_fact(...)

```python
f_low = _make_fact('f_low', 'Low-trust fact with minimal unverified source information')
```

### Step 4: Assign engine = self._build_trust_engine(...)

```python
engine = self._build_trust_engine([f_high, f_low], trust_map={'f_high': 1.0, 'f_low': 0.0})
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

### Step 6: Assign scores = value

```python
scores = {r.fact.fact_id: r.score for r in response.results}
```

**Verification:**
```python
assert scores['f_high'] > scores['f_low']
```


## Complete Example

```python
# Workflow
"trust=1.0 maps to weight=1.5, boosting the fact's score."
f_high = _make_fact('f_high', 'High-trust fact with comprehensive verified evidence')
f_low = _make_fact('f_low', 'Low-trust fact with minimal unverified source information')
engine = self._build_trust_engine([f_high, f_low], trust_map={'f_high': 1.0, 'f_low': 0.0})
response = engine.recall('q', 'default')
scores = {r.fact.fact_id: r.score for r in response.results}
assert scores['f_high'] > scores['f_low']
```

## Next Steps


---

*Source: test_retrieval_integration.py:269 | Complexity: Intermediate | Last updated: 2026-05-05*