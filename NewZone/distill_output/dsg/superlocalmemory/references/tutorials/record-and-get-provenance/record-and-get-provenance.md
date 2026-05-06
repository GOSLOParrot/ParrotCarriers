# How To: Record And Get Provenance

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test record and get provenance

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
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign fid = _insert_stub_fact(...)

```python
fid = _insert_stub_fact(db, 'prov_f1')
```

**Verification:**
```python
assert got is not None
```

### Step 2: Assign tracker = ProvenanceTracker(...)

```python
tracker = ProvenanceTracker(db)
```

**Verification:**
```python
assert got.source_type == 'conversation'
```

### Step 3: Assign rec = tracker.record(...)

```python
rec = tracker.record(fact_id=fid, profile_id='default', source_type='conversation', source_id='session_1', created_by='agent_x')
```

**Verification:**
```python
assert got.source_id == 'session_1'
```

### Step 4: Assign got = tracker.get_provenance(...)

```python
got = tracker.get_provenance(fid, 'default')
```

**Verification:**
```python
assert got.created_by == 'agent_x'
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
from superlocalmemory.trust.provenance import ProvenanceTracker
fid = _insert_stub_fact(db, 'prov_f1')
tracker = ProvenanceTracker(db)
rec = tracker.record(fact_id=fid, profile_id='default', source_type='conversation', source_id='session_1', created_by='agent_x')
got = tracker.get_provenance(fid, 'default')
assert got is not None
assert got.source_type == 'conversation'
assert got.source_id == 'session_1'
assert got.created_by == 'agent_x'
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:181 | Complexity: Intermediate | Last updated: 2026-05-05*