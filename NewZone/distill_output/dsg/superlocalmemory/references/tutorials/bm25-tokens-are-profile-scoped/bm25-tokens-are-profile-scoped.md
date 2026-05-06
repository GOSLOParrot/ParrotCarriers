# How To: Bm25 Tokens Are Profile Scoped

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test bm25 tokens are profile scoped

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `datetime`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.trust.provenance`
- `superlocalmemory.trust.provenance`
- `superlocalmemory.learning.adaptive`
- `superlocalmemory.learning.adaptive`
- `superlocalmemory.learning.adaptive`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning.outcomes`
- `superlocalmemory.learning.outcomes`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.eu_ai_act`
- `superlocalmemory.compliance.eu_ai_act`
- `superlocalmemory.compliance.eu_ai_act`
- `superlocalmemory.compliance.eu_ai_act`
- `superlocalmemory.compliance.eu_ai_act`
- `superlocalmemory.compliance.lifecycle`
- `superlocalmemory.compliance.lifecycle`
- `superlocalmemory.compliance.lifecycle`
- `superlocalmemory.compliance.lifecycle`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.trust.scorer`
- `superlocalmemory.attribution.mathematical_dna`
- `superlocalmemory.attribution.mathematical_dna`
- `superlocalmemory.attribution.mathematical_dna`
- `superlocalmemory.attribution.watermark`
- `superlocalmemory.attribution.signer`
- `superlocalmemory.attribution.signer`
- `superlocalmemory.storage.access_control`
- `superlocalmemory.storage.access_control`
- `superlocalmemory.storage.access_control`
- `superlocalmemory.storage.access_control`
- `superlocalmemory.compliance.gdpr`
- `superlocalmemory.compliance.gdpr`

**Setup Required:**
```python
# Fixtures: engine
```

## Step-by-Step Guide

### Step 1: Call self._create_profile()

```python
self._create_profile(engine, 'p1')
```

**Verification:**
```python
assert set(p1_tokens.keys()).isdisjoint(set(p2_tokens.keys()))
```

### Step 2: Call self._create_profile()

```python
self._create_profile(engine, 'p2')
```

### Step 3: Assign engine.profile_id = 'p1'

```python
engine.profile_id = 'p1'
```

### Step 4: Call engine.store()

```python
engine.store('Unique P1 keyword xylophone was mentioned during the music class session.', session_id='s1')
```

### Step 5: Assign engine.profile_id = 'p2'

```python
engine.profile_id = 'p2'
```

### Step 6: Call engine.store()

```python
engine.store('Unique P2 keyword harmonica was discussed in the band rehearsal meeting.', session_id='s2')
```

### Step 7: Assign p1_tokens = engine._db.get_all_bm25_tokens(...)

```python
p1_tokens = engine._db.get_all_bm25_tokens('p1')
```

### Step 8: Assign p2_tokens = engine._db.get_all_bm25_tokens(...)

```python
p2_tokens = engine._db.get_all_bm25_tokens('p2')
```

**Verification:**
```python
assert set(p1_tokens.keys()).isdisjoint(set(p2_tokens.keys()))
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
self._create_profile(engine, 'p1')
self._create_profile(engine, 'p2')
engine.profile_id = 'p1'
engine.store('Unique P1 keyword xylophone was mentioned during the music class session.', session_id='s1')
engine.profile_id = 'p2'
engine.store('Unique P2 keyword harmonica was discussed in the band rehearsal meeting.', session_id='s2')
p1_tokens = engine._db.get_all_bm25_tokens('p1')
p2_tokens = engine._db.get_all_bm25_tokens('p2')
assert set(p1_tokens.keys()).isdisjoint(set(p2_tokens.keys()))
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:542 | Complexity: Advanced | Last updated: 2026-05-05*