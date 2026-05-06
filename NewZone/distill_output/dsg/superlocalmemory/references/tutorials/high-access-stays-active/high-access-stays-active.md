# How To: High Access Stays Active

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test high access stays active

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

### Step 1: Assign old_date = unknown.isoformat(...)

```python
old_date = (datetime.now(UTC) - timedelta(days=60)).isoformat()
```

**Verification:**
```python
assert state == MemoryLifecycle.ACTIVE
```

### Step 2: Assign fact = AtomicFact(...)

```python
fact = AtomicFact(fact_id='lf4', content='Hot fact', created_at=old_date, access_count=20)
```

### Step 3: Assign mgr = LifecycleManager(...)

```python
mgr = LifecycleManager(db)
```

### Step 4: Assign state = mgr.get_lifecycle_state(...)

```python
state = mgr.get_lifecycle_state(fact)
```

**Verification:**
```python
assert state == MemoryLifecycle.ACTIVE
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
from superlocalmemory.compliance.lifecycle import LifecycleManager
old_date = (datetime.now(UTC) - timedelta(days=60)).isoformat()
fact = AtomicFact(fact_id='lf4', content='Hot fact', created_at=old_date, access_count=20)
mgr = LifecycleManager(db)
state = mgr.get_lifecycle_state(fact)
assert state == MemoryLifecycle.ACTIVE
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:459 | Complexity: Intermediate | Last updated: 2026-05-05*