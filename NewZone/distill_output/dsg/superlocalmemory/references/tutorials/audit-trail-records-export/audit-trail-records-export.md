# How To: Audit Trail Records Export

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test audit trail records export

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

### Step 1: Call engine._db.execute()

```python
engine._db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?,?)', ('auditee', 'Auditee'))
```

**Verification:**
```python
assert 'export' in actions
```

### Step 2: Assign engine.profile_id = 'auditee'

```python
engine.profile_id = 'auditee'
```

### Step 3: Call engine.store()

```python
engine.store('Data for audit trail test to verify compliance logging works correctly.', session_id='s1')
```

### Step 4: Assign gdpr = GDPRCompliance(...)

```python
gdpr = GDPRCompliance(engine._db)
```

### Step 5: Call gdpr.export_profile_data()

```python
gdpr.export_profile_data('auditee')
```

### Step 6: Assign trail = gdpr.get_audit_trail(...)

```python
trail = gdpr.get_audit_trail('auditee')
```

### Step 7: Assign actions = value

```python
actions = [t['action'] for t in trail]
```

**Verification:**
```python
assert 'export' in actions
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
engine._db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?,?)', ('auditee', 'Auditee'))
engine.profile_id = 'auditee'
engine.store('Data for audit trail test to verify compliance logging works correctly.', session_id='s1')
from superlocalmemory.compliance.gdpr import GDPRCompliance
gdpr = GDPRCompliance(engine._db)
gdpr.export_profile_data('auditee')
trail = gdpr.get_audit_trail('auditee')
actions = [t['action'] for t in trail]
assert 'export' in actions
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:335 | Complexity: Intermediate | Last updated: 2026-05-05*