# How To: Emotional Valence Contradiction

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test emotional valence contradiction

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.consolidator`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign consolidator = MemoryConsolidator(...)

```python
consolidator = MemoryConsolidator(db=db)
```

**Verification:**
```python
assert result is True
```

### Step 2: Assign fact_a = AtomicFact(...)

```python
fact_a = AtomicFact(content='Alice loves the project', canonical_entities=['ent_alice'], emotional_valence=0.9)
```

### Step 3: Assign fact_b = AtomicFact(...)

```python
fact_b = AtomicFact(content='Alice hates the project', canonical_entities=['ent_alice'], emotional_valence=-0.9)
```

### Step 4: Assign result = consolidator._keyword_contradiction_check(...)

```python
result = consolidator._keyword_contradiction_check(fact_a, fact_b)
```

**Verification:**
```python
assert result is True
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
consolidator = MemoryConsolidator(db=db)
fact_a = AtomicFact(content='Alice loves the project', canonical_entities=['ent_alice'], emotional_valence=0.9)
fact_b = AtomicFact(content='Alice hates the project', canonical_entities=['ent_alice'], emotional_valence=-0.9)
result = consolidator._keyword_contradiction_check(fact_a, fact_b)
assert result is True
```

## Next Steps


---

*Source: test_consolidator.py:242 | Complexity: Intermediate | Last updated: 2026-05-05*