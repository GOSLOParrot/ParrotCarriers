# How To: Preference Redaction Counts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test preference redaction counts

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `tempfile`
- `pathlib`
- `typing`
- `pytest`
- `fastapi`
- `fastapi.testclient`
- `superlocalmemory.core`
- `superlocalmemory.server.middleware.security_headers`
- `superlocalmemory.server.routes`
- `superlocalmemory.learning.database`
- `json`
- `superlocalmemory.learning.features`
- `time`
- `superlocalmemory.learning.database`
- `sqlite3`
- `importlib`
- `superlocalmemory.server.routes`
- `sys`
- `types`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `sqlite3`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes`
- `superlocalmemory.learning.database`
- `sys`
- `types`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `datetime`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `datetime`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `pathlib`
- `datetime`
- `superlocalmemory.learning.database`

**Setup Required:**
```python
# Fixtures: client, install_token, monkeypatch
```

## Step-by-Step Guide

### Step 1: Call monkeypatch.setattr()

```python
monkeypatch.setattr(brain_mod, '_load_raw_preferences', lambda pid: {'topics': [{'name': 'secret=AKIAABCDEFGHIJKLMNOP', 'strength': 0.9}], 'entities': [{'name': 'Qualixar', 'mention_count': 1}], 'tech': [{'name': 'Python', 'frequency': 0.6}]})
```

**Verification:**
```python
assert prefs['redacted_count'] >= 1
```

### Step 2: Assign r = client.get(...)

```python
r = client.get('/api/v3/brain', headers={'X-Install-Token': install_token})
```

**Verification:**
```python
assert 'AKIAABCDEFGHIJKLMNOP' not in dumped
```

### Step 3: Assign body = r.json(...)

```python
body = r.json()
```

**Verification:**
```python
assert '[REDACTED:AWS' in dumped
```

### Step 4: Assign prefs = value

```python
prefs = body['preferences']
```

**Verification:**
```python
assert prefs['redacted_count'] >= 1
```

### Step 5: Assign dumped = _json.dumps(...)

```python
dumped = _json.dumps(prefs)
```

**Verification:**
```python
assert 'AKIAABCDEFGHIJKLMNOP' not in dumped
```


## Complete Example

```python
# Setup
# Fixtures: client, install_token, monkeypatch

# Workflow
monkeypatch.setattr(brain_mod, '_load_raw_preferences', lambda pid: {'topics': [{'name': 'secret=AKIAABCDEFGHIJKLMNOP', 'strength': 0.9}], 'entities': [{'name': 'Qualixar', 'mention_count': 1}], 'tech': [{'name': 'Python', 'frequency': 0.6}]})
r = client.get('/api/v3/brain', headers={'X-Install-Token': install_token})
body = r.json()
prefs = body['preferences']
assert prefs['redacted_count'] >= 1
import json as _json
dumped = _json.dumps(prefs)
assert 'AKIAABCDEFGHIJKLMNOP' not in dumped
assert '[REDACTED:AWS' in dumped
```

## Next Steps


---

*Source: test_brain_endpoint.py:240 | Complexity: Intermediate | Last updated: 2026-05-05*