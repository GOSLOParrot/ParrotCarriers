# How To: Ranker Retrain Legacy Gated When Outcomes Present

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: Stage-8 H-07: once a profile has an active model (with outcomes),
the legacy cold-start path MUST be skipped. The online retrain path
owns the profile after that point.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `importlib`
- `json`
- `logging`
- `sqlite3`
- `sys`
- `warnings`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_cycle`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.dedup_hnsw`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning.ranker_retrain_legacy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign calls = value

```python
calls = {'online': 0, 'legacy': 0}
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
calls = {'online': 0, 'legacy': 0}
```

## Next Steps


---

*Source: test_f4a_refactor.py:183 | Complexity: Beginner | Last updated: 2026-05-05*