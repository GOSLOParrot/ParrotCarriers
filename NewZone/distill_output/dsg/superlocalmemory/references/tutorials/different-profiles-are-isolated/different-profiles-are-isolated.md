# How To: Different Profiles Are Isolated

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test different profiles are isolated

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine
```

## Step-by-Step Guide

### Step 1: Call self._create_profile()

```python
self._create_profile(engine, 'work')
```

**Verification:**
```python
assert len(work_facts) == 0
```

### Step 2: Call self._create_profile()

```python
self._create_profile(engine, 'personal')
```

### Step 3: Assign engine.profile_id = 'work'

```python
engine.profile_id = 'work'
```

### Step 4: Call engine.store()

```python
engine.store('Work fact: Q1 revenue was $10M for the enterprise division', session_id='s1')
```

### Step 5: Assign engine.profile_id = 'personal'

```python
engine.profile_id = 'personal'
```

### Step 6: Call engine.store()

```python
engine.store('Personal fact: I love eating pepperoni pizza on weekends', session_id='s1')
```

### Step 7: Assign response = engine.recall(...)

```python
response = engine.recall('revenue', profile_id='personal')
```

### Step 8: Assign work_facts = value

```python
work_facts = [r for r in response.results if 'revenue' in r.fact.content.lower()]
```

**Verification:**
```python
assert len(work_facts) == 0
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
self._create_profile(engine, 'work')
self._create_profile(engine, 'personal')
engine.profile_id = 'work'
engine.store('Work fact: Q1 revenue was $10M for the enterprise division', session_id='s1')
engine.profile_id = 'personal'
engine.store('Personal fact: I love eating pepperoni pizza on weekends', session_id='s1')
response = engine.recall('revenue', profile_id='personal')
work_facts = [r for r in response.results if 'revenue' in r.fact.content.lower()]
assert len(work_facts) == 0
```

## Next Steps


---

*Source: test_e2e.py:288 | Complexity: Advanced | Last updated: 2026-05-05*