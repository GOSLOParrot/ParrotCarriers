# How To: Evolution Timeseries Counts Signals

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Signals written today should show up in the last point.

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
# Fixtures: client, install_token, tmp_learning_db
```

## Step-by-Step Guide

### Step 1: 'Signals written today should show up in the last point.'

```python
'Signals written today should show up in the last point.'
```

**Verification:**
```python
assert body['total_signals'] >= 1
```

### Step 2: Assign iso_now = datetime.now.isoformat(...)

```python
iso_now = datetime.now(timezone.utc).isoformat()
```

**Verification:**
```python
assert last['date'] == today
```

### Step 3: Assign body = client.get.json(...)

```python
body = client.get('/api/v3/brain/evolution-timeseries?days=7', headers={'X-Install-Token': install_token}).json()
```

**Verification:**
```python
assert last['signals'] >= 1
```

### Step 4: Assign today = datetime.now.date.isoformat(...)

```python
today = datetime.now(timezone.utc).date().isoformat()
```

### Step 5: Assign last = value

```python
last = body['points'][-1]
```

**Verification:**
```python
assert last['date'] == today
```

### Step 6: Call conn.execute()

```python
conn.execute('INSERT INTO learning_signals (profile_id, query, fact_id, signal_type, created_at) VALUES (?, ?, ?, ?, ?)', ('default', 'q', 'f1', 'shown', iso_now))
```

### Step 7: Call conn.commit()

```python
conn.commit()
```


## Complete Example

```python
# Setup
# Fixtures: client, install_token, tmp_learning_db

# Workflow
'Signals written today should show up in the last point.'
from datetime import datetime, timezone
iso_now = datetime.now(timezone.utc).isoformat()
with sqlite3.connect(tmp_learning_db) as conn:
    conn.execute('INSERT INTO learning_signals (profile_id, query, fact_id, signal_type, created_at) VALUES (?, ?, ?, ?, ?)', ('default', 'q', 'f1', 'shown', iso_now))
    conn.commit()
body = client.get('/api/v3/brain/evolution-timeseries?days=7', headers={'X-Install-Token': install_token}).json()
assert body['total_signals'] >= 1
today = datetime.now(timezone.utc).date().isoformat()
last = body['points'][-1]
assert last['date'] == today
assert last['signals'] >= 1
```

## Next Steps


---

*Source: test_brain_endpoint.py:848 | Complexity: Intermediate | Last updated: 2026-05-05*