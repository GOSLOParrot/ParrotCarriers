# How To: Graph Edges Are Profile Scoped

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test graph edges are profile scoped

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
self._create_profile(engine, 'alpha')
```

**Verification:**
```python
assert d['source_id'] not in beta_facts
```

### Step 2: Call self._create_profile()

```python
self._create_profile(engine, 'beta')
```

**Verification:**
```python
assert d['target_id'] not in beta_facts
```

### Step 3: Assign engine.profile_id = 'alpha'

```python
engine.profile_id = 'alpha'
```

### Step 4: Call engine.store()

```python
engine.store('Alice met Bob at the central park near downtown during the annual festival.', session_id='s1')
```

### Step 5: Assign engine.profile_id = 'beta'

```python
engine.profile_id = 'beta'
```

### Step 6: Call engine.store()

```python
engine.store('Charlie met Diana at the beach.', session_id='s2')
```

### Step 7: Assign alpha_edges = engine._db.execute(...)

```python
alpha_edges = engine._db.execute('SELECT COUNT(*) AS c FROM graph_edges WHERE profile_id = ?', ('alpha',))
```

### Step 8: Assign beta_edges = engine._db.execute(...)

```python
beta_edges = engine._db.execute('SELECT COUNT(*) AS c FROM graph_edges WHERE profile_id = ?', ('beta',))
```

### Step 9: Assign alpha_edge_rows = engine._db.execute(...)

```python
alpha_edge_rows = engine._db.execute('SELECT source_id, target_id FROM graph_edges WHERE profile_id = ?', ('alpha',))
```

### Step 10: Assign beta_facts = value

```python
beta_facts = {dict(r)['fact_id'] for r in engine._db.execute('SELECT fact_id FROM atomic_facts WHERE profile_id = ?', ('beta',))}
```

### Step 11: Assign d = dict(...)

```python
d = dict(row)
```

**Verification:**
```python
assert d['source_id'] not in beta_facts
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
self._create_profile(engine, 'alpha')
self._create_profile(engine, 'beta')
engine.profile_id = 'alpha'
engine.store('Alice met Bob at the central park near downtown during the annual festival.', session_id='s1')
engine.profile_id = 'beta'
engine.store('Charlie met Diana at the beach.', session_id='s2')
alpha_edges = engine._db.execute('SELECT COUNT(*) AS c FROM graph_edges WHERE profile_id = ?', ('alpha',))
beta_edges = engine._db.execute('SELECT COUNT(*) AS c FROM graph_edges WHERE profile_id = ?', ('beta',))
alpha_edge_rows = engine._db.execute('SELECT source_id, target_id FROM graph_edges WHERE profile_id = ?', ('alpha',))
beta_facts = {dict(r)['fact_id'] for r in engine._db.execute('SELECT fact_id FROM atomic_facts WHERE profile_id = ?', ('beta',))}
for row in alpha_edge_rows:
    d = dict(row)
    assert d['source_id'] not in beta_facts
    assert d['target_id'] not in beta_facts
```

## Next Steps


---

*Source: test_trust_compliance_wiring.py:495 | Complexity: Advanced | Last updated: 2026-05-05*