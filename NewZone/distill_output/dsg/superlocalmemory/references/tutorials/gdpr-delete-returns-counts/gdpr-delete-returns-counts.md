# How To: Gdpr Delete Returns Counts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test gdpr delete returns counts

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
engine._db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?,?)', ('audit_del', 'AuditDel'))
```

**Verification:**
```python
assert isinstance(counts, dict)
```

### Step 2: Assign engine.profile_id = 'audit_del'

```python
engine.profile_id = 'audit_del'
```

**Verification:**
```python
assert 'profiles' in counts
```

### Step 3: Call engine.store()

```python
engine.store('Sensitive information about the quarterly financial report and projections.', session_id='s1')
```

**Verification:**
```python
assert counts['profiles'] == 1
```

### Step 4: Assign gdpr = GDPRCompliance(...)

```python
gdpr = GDPRCompliance(engine._db)
```

**Verification:**
```python
assert int(dict(remaining[0])['c']) == 0
```

### Step 5: Assign counts = gdpr.forget_profile(...)

```python
counts = gdpr.forget_profile('audit_del')
```

**Verification:**
```python
assert isinstance(counts, dict)
```

### Step 6: Assign remaining = engine._db.execute(...)

```python
remaining = engine._db.execute('SELECT COUNT(*) AS c FROM atomic_facts WHERE profile_id = ?', ('audit_del',))
```

**Verification:**
```python
assert int(dict(remaining[0])['c']) == 0
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
engine._db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?,?)', ('audit_del', 'AuditDel'))
engine.profile_id = 'audit_del'
engine.store('Sensitive information about the quarterly financial report and projections.', session_id='s1')
from superlocalmemory.compliance.gdpr import GDPRCompliance
gdpr = GDPRCompliance(engine._db)
counts = gdpr.forget_profile('audit_del')
assert isinstance(counts, dict)
assert 'profiles' in counts
assert counts['profiles'] == 1
remaining = engine._db.execute('SELECT COUNT(*) AS c FROM atomic_facts WHERE profile_id = ?', ('audit_del',))
assert int(dict(remaining[0])['c']) == 0
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:697 | Complexity: Intermediate | Last updated: 2026-05-05*