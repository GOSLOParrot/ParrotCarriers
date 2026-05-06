# How To: Hex Id Pattern Keys Are Filtered On Read

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Historic ``_store_patterns`` rows whose pattern_key is a bare
hex id are invisible to the dashboard.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `tempfile`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning`
- `superlocalmemory.learning.behavioral`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Historic ``_store_patterns`` rows whose pattern_key is a bare\n    hex id are invisible to the dashboard.'

```python
'Historic ``_store_patterns`` rows whose pattern_key is a bare\n    hex id are invisible to the dashboard.'
```

**Verification:**
```python
assert 'Qualixar' in keys, f'legitimate pattern missing: {keys!r}'
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'learning.db'
```

**Verification:**
```python
assert 'ea701bf01f1ff4df8' not in keys, f'orphan hex id leaked into pattern_key: {keys!r}'
```

### Step 3: Assign store = BehavioralPatternStore(...)

```python
store = BehavioralPatternStore(str(db_path))
```

**Verification:**
```python
assert 'ea701bf01f1ff4df8' not in values, f'orphan hex id leaked into metadata.value: {values!r}'
```

### Step 4: Call store.record_pattern()

```python
store.record_pattern(profile_id='p', pattern_type='entity_preferences', data={'topic': 'Qualixar', 'pattern_key': 'entity:Qualixar', 'value': 'Qualixar', 'evidence': 10, 'source': 't'}, success_rate=0.9, confidence=0.9)
```

### Step 5: Call store.record_pattern()

```python
store.record_pattern(profile_id='p', pattern_type='entity_preferences', data={'topic': 'ea701bf01f1ff4df8', 'pattern_key': 'entity:ea701bf01f1ff4df8', 'value': 'ea701bf01f1ff4df8', 'evidence': 191, 'source': 't'}, success_rate=1.0, confidence=1.0)
```

### Step 6: Assign out = store.get_patterns(...)

```python
out = store.get_patterns(profile_id='p')
```

### Step 7: Assign keys = value

```python
keys = [p.get('pattern_key') for p in out]
```

### Step 8: Assign values = value

```python
values = [(p.get('metadata') or {}).get('value') for p in out]
```

**Verification:**
```python
assert 'Qualixar' in keys, f'legitimate pattern missing: {keys!r}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Historic ``_store_patterns`` rows whose pattern_key is a bare\n    hex id are invisible to the dashboard.'
from superlocalmemory.learning.behavioral import BehavioralPatternStore
db_path = tmp_path / 'learning.db'
store = BehavioralPatternStore(str(db_path))
store.record_pattern(profile_id='p', pattern_type='entity_preferences', data={'topic': 'Qualixar', 'pattern_key': 'entity:Qualixar', 'value': 'Qualixar', 'evidence': 10, 'source': 't'}, success_rate=0.9, confidence=0.9)
store.record_pattern(profile_id='p', pattern_type='entity_preferences', data={'topic': 'ea701bf01f1ff4df8', 'pattern_key': 'entity:ea701bf01f1ff4df8', 'value': 'ea701bf01f1ff4df8', 'evidence': 191, 'source': 't'}, success_rate=1.0, confidence=1.0)
out = store.get_patterns(profile_id='p')
keys = [p.get('pattern_key') for p in out]
values = [(p.get('metadata') or {}).get('value') for p in out]
assert 'Qualixar' in keys, f'legitimate pattern missing: {keys!r}'
assert 'ea701bf01f1ff4df8' not in keys, f'orphan hex id leaked into pattern_key: {keys!r}'
assert 'ea701bf01f1ff4df8' not in values, f'orphan hex id leaked into metadata.value: {values!r}'
```

## Next Steps


---

*Source: test_s9_dash_orphan_entity.py:35 | Complexity: Advanced | Last updated: 2026-05-05*