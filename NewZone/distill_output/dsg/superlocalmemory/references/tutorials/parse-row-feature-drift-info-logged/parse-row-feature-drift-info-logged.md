# How To: Parse Row Feature Drift Info Logged

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test parse row feature drift info logged

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `json`

**Setup Required:**
```python
# Fixtures: tmp_path, caplog
```

## Step-by-Step Guide

### Step 1: Assign unknown = _trained_model(...)

```python
_, model = _trained_model(tmp_path)
```

**Verification:**
```python
assert parsed is not None
```

### Step 2: Assign state = model.booster.model_to_string.encode(...)

```python
state = model.booster.model_to_string().encode('utf-8')
```

**Verification:**
```python
assert any(('feature-drift' in rec.message for rec in caplog.records))
```

### Step 3: Assign sha = _h.sha256.hexdigest(...)

```python
sha = _h.sha256(state).hexdigest()
```

**Verification:**
```python
assert parsed is not None
```

### Step 4: Assign parsed = _parse_row(...)

```python
parsed = _parse_row('p1', {'state_bytes': state, 'bytes_sha256': sha, 'feature_names': _json.dumps(['only_one_name']), 'trained_at': ''})
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, caplog

# Workflow
_, model = _trained_model(tmp_path)
from superlocalmemory.learning.model_cache import _parse_row
state = model.booster.model_to_string().encode('utf-8')
import hashlib as _h
sha = _h.sha256(state).hexdigest()
import json as _json
with caplog.at_level('INFO'):
    parsed = _parse_row('p1', {'state_bytes': state, 'bytes_sha256': sha, 'feature_names': _json.dumps(['only_one_name']), 'trained_at': ''})
assert parsed is not None
assert any(('feature-drift' in rec.message for rec in caplog.records))
```

## Next Steps


---

*Source: test_ranker_v2.py:552 | Complexity: Intermediate | Last updated: 2026-05-05*