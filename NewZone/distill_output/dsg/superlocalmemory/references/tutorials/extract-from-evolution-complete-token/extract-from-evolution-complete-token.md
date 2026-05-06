# How To: Extract From Evolution Complete Token

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test extract from evolution complete token

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `dataclasses`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.evolution.types`
- `superlocalmemory.evolution.evolution_store`
- `superlocalmemory.evolution.triggers`
- `superlocalmemory.evolution.mutation_generator`
- `superlocalmemory.evolution.blind_verifier`
- `superlocalmemory.evolution.skill_evolver`


## Step-by-Step Guide

### Step 1: Assign output = 'Analysis done.\n\n<EVOLUTION_COMPLETE>\n---\nname: evolved-skill\ndescription: Fixed version\n---\n\n# Content\nBetter instructions.'

```python
output = 'Analysis done.\n\n<EVOLUTION_COMPLETE>\n---\nname: evolved-skill\ndescription: Fixed version\n---\n\n# Content\nBetter instructions.'
```

**Verification:**
```python
assert result is not None
```

### Step 2: Assign result = parse_mutation_output(...)

```python
result = parse_mutation_output(output)
```

**Verification:**
```python
assert 'evolved-skill' in result
```


## Complete Example

```python
# Workflow
output = 'Analysis done.\n\n<EVOLUTION_COMPLETE>\n---\nname: evolved-skill\ndescription: Fixed version\n---\n\n# Content\nBetter instructions.'
result = parse_mutation_output(output)
assert result is not None
assert 'evolved-skill' in result
```

## Next Steps


---

*Source: test_evolution.py:944 | Complexity: Beginner | Last updated: 2026-05-05*