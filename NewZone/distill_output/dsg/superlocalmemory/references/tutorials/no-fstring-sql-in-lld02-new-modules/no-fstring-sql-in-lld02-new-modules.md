# How To: No Fstring Sql In Lld02 New Modules

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: f-string SQL is forbidden in the NEW modules introduced by LLD-02.

Pre-existing f-string SQL with hard-coded values (e.g. iterating a tuple
of known table names in ``database.reset()`` or ``IN``-clause
placeholders in ``_generate_patterns``) is out of scope for LLD-02
Wave 2 Stream B; the rule in §7 targets user-data interpolation.

## Prerequisites

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `sqlite3`
- `threading`
- `pathlib`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.database`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `re`
- `re`
- `re`
- `re`


## Step-by-Step Guide

### Step 1: 'f-string SQL is forbidden in the NEW modules introduced by LLD-02.\n\n    Pre-existing f-string SQL with hard-coded values (e.g. iterating a tuple\n    of known table names in ``database.reset()`` or ``IN``-clause\n    placeholders in ``_generate_patterns``) is out of scope for LLD-02\n    Wave 2 Stream B; the rule in §7 targets user-data interpolation.\n    '

```python
'f-string SQL is forbidden in the NEW modules introduced by LLD-02.\n\n    Pre-existing f-string SQL with hard-coded values (e.g. iterating a tuple\n    of known table names in ``database.reset()`` or ``IN``-clause\n    placeholders in ``_generate_patterns``) is out of scope for LLD-02\n    Wave 2 Stream B; the rule in §7 targets user-data interpolation.\n    '
```

**Verification:**
```python
assert not hits, f'f-string SQL detected in {name}: {hits}'
```

### Step 2: Assign new_modules = value

```python
new_modules = ['signals.py', 'signal_worker.py', 'model_cache.py', 'labeler.py', 'ranker.py']
```

### Step 3: Assign pattern = re.compile(...)

```python
pattern = re.compile('f["\'][^"\']*\\b(SELECT|INSERT|UPDATE|DELETE)\\b')
```

### Step 4: Assign base = _learning_dir(...)

```python
base = _learning_dir()
```

### Step 5: Assign text = unknown.read_text(...)

```python
text = (base / name).read_text(encoding='utf-8')
```

### Step 6: Assign hits = pattern.findall(...)

```python
hits = pattern.findall(text)
```

**Verification:**
```python
assert not hits, f'f-string SQL detected in {name}: {hits}'
```


## Complete Example

```python
# Workflow
'f-string SQL is forbidden in the NEW modules introduced by LLD-02.\n\n    Pre-existing f-string SQL with hard-coded values (e.g. iterating a tuple\n    of known table names in ``database.reset()`` or ``IN``-clause\n    placeholders in ``_generate_patterns``) is out of scope for LLD-02\n    Wave 2 Stream B; the rule in §7 targets user-data interpolation.\n    '
import re
new_modules = ['signals.py', 'signal_worker.py', 'model_cache.py', 'labeler.py', 'ranker.py']
pattern = re.compile('f["\'][^"\']*\\b(SELECT|INSERT|UPDATE|DELETE)\\b')
base = _learning_dir()
for name in new_modules:
    text = (base / name).read_text(encoding='utf-8')
    hits = pattern.findall(text)
    assert not hits, f'f-string SQL detected in {name}: {hits}'
```

## Next Steps


---

*Source: test_lightgbm_training.py:325 | Complexity: Intermediate | Last updated: 2026-05-05*