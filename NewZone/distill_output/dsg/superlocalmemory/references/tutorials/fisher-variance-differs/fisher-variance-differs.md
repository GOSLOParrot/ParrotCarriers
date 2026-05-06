# How To: Fisher Variance Differs

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts with different content should have different Fisher variance.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `pathlib`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.storage.models`
- `httpx`
- `httpx`
- `httpx`
- `warnings`

**Setup Required:**
```python
# Fixtures: mode_b_engine
```

## Step-by-Step Guide

### Step 1: 'Facts with different content should have different Fisher variance.'

```python
'Facts with different content should have different Fisher variance.'
```

**Verification:**
```python
assert diff > 1e-06, f'Fisher variance identical for different content: diff={diff}'
```

### Step 2: Call mode_b_engine.store()

```python
mode_b_engine.store('Python is a programming language.', session_id='s1')
```

### Step 3: Call mode_b_engine.store()

```python
mode_b_engine.store('The Eiffel Tower is in Paris, France.', session_id='s1')
```

### Step 4: Assign facts = mode_b_engine._db.get_all_facts(...)

```python
facts = mode_b_engine._db.get_all_facts('default')
```

### Step 5: Assign facts_with_fv = value

```python
facts_with_fv = [f for f in facts if f.fisher_variance is not None]
```

### Step 6: Assign v1 = np.asarray(...)

```python
v1 = np.asarray(facts_with_fv[0].fisher_variance)
```

### Step 7: Assign v2 = np.asarray(...)

```python
v2 = np.asarray(facts_with_fv[1].fisher_variance)
```

### Step 8: Assign diff = float(...)

```python
diff = float(np.linalg.norm(v1 - v2))
```

**Verification:**
```python
assert diff > 1e-06, f'Fisher variance identical for different content: diff={diff}'
```


## Complete Example

```python
# Setup
# Fixtures: mode_b_engine

# Workflow
'Facts with different content should have different Fisher variance.'
mode_b_engine.store('Python is a programming language.', session_id='s1')
mode_b_engine.store('The Eiffel Tower is in Paris, France.', session_id='s1')
facts = mode_b_engine._db.get_all_facts('default')
facts_with_fv = [f for f in facts if f.fisher_variance is not None]
if len(facts_with_fv) >= 2:
    v1 = np.asarray(facts_with_fv[0].fisher_variance)
    v2 = np.asarray(facts_with_fv[1].fisher_variance)
    diff = float(np.linalg.norm(v1 - v2))
    assert diff > 1e-06, f'Fisher variance identical for different content: diff={diff}'
```

## Next Steps


---

*Source: test_mode_b_ollama.py:399 | Complexity: Advanced | Last updated: 2026-05-05*