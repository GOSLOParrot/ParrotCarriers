# How To: Negation Marker

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test negation marker

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
fact_a = AtomicFact(content='Alice quit the company')
```

### Step 3: Assign fact_b = AtomicFact(...)

```python
fact_b = AtomicFact(content='Alice works at the company')
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
fact_a = AtomicFact(content='Alice quit the company')
fact_b = AtomicFact(content='Alice works at the company')
result = consolidator._keyword_contradiction_check(fact_a, fact_b)
assert result is True
```

## Next Steps


---

*Source: test_consolidator.py:228 | Complexity: Intermediate | Last updated: 2026-05-05*