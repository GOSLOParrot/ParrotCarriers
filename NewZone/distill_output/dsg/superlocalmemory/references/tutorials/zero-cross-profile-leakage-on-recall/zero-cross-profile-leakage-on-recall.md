# How To: Zero Cross Profile Leakage On Recall

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test zero cross profile leakage on recall

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
self._create_profile(engine, 'work')
```

**Verification:**
```python
assert len(revenue_facts) == 0
```

### Step 2: Call self._create_profile()

```python
self._create_profile(engine, 'personal')
```

### Step 3: Assign engine.profile_id = 'work'

```python
engine.profile_id = 'work'
```

### Step 4: Call engine.store()

```python
engine.store('Q1 revenue target is $10M for the enterprise sales division this year.', session_id='s1')
```

### Step 5: Assign engine.profile_id = 'personal'

```python
engine.profile_id = 'personal'
```

### Step 6: Call engine.store()

```python
engine.store('I love eating pepperoni pizza at the Italian restaurant downtown on weekends.', session_id='s2')
```

### Step 7: Assign response = engine.recall(...)

```python
response = engine.recall('revenue', profile_id='personal')
```

### Step 8: Assign revenue_facts = value

```python
revenue_facts = [r for r in response.results if 'revenue' in r.fact.content.lower()]
```

**Verification:**
```python
assert len(revenue_facts) == 0
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
self._create_profile(engine, 'work')
self._create_profile(engine, 'personal')
engine.profile_id = 'work'
engine.store('Q1 revenue target is $10M for the enterprise sales division this year.', session_id='s1')
engine.profile_id = 'personal'
engine.store('I love eating pepperoni pizza at the Italian restaurant downtown on weekends.', session_id='s2')
response = engine.recall('revenue', profile_id='personal')
revenue_facts = [r for r in response.results if 'revenue' in r.fact.content.lower()]
assert len(revenue_facts) == 0
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:484 | Complexity: Advanced | Last updated: 2026-05-05*