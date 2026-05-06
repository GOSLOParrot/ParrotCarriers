# How To: Async Remember Persists To Memory Db

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: The bug that lost 18 memories: stored returns 'queued' but never
actually persists. This test catches that regression.

## Prerequisites

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `urllib.request`
- `urllib.error`
- `json`
- `pytest`


## Step-by-Step Guide

### Step 1: "The bug that lost 18 memories: stored returns 'queued' but never\n        actually persists. This test catches that regression.\n        "

```python
"The bug that lost 18 memories: stored returns 'queued' but never\n        actually persists. This test catches that regression.\n        "
```

**Verification:**
```python
assert resp['ok'] is True, f'remember failed: {resp}'
```

### Step 2: Assign marker = value

```python
marker = f'E2E_TEST_{int(time.time() * 1000)}'
```

**Verification:**
```python
assert resp['status'] == 'queued', f'unexpected status: {resp}'
```

### Step 3: Assign content = value

```python
content = f'{marker} — async-pipeline E2E persistence test'
```

**Verification:**
```python
assert materialized, f'Memory id={pending_id} stuck in pending after {MATERIALIZER_TIMEOUT_S}s — materializer is broken'
```

### Step 4: Assign req = urllib.request.Request(...)

```python
req = urllib.request.Request(f'{DAEMON_URL}/remember', data=json.dumps({'content': content}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
```

**Verification:**
```python
assert len(rows) >= 1, f"Memory id={pending_id} marked done but NOT in memory.db. This means the materializer's mark_done is firing but the actual engine.store() didn't complete — silent data loss."
```

### Step 5: Assign pending_id = value

```python
pending_id = resp['pending_id']
```

**Verification:**
```python
assert recall_resp['result_count'] >= 1, f'Memory persisted but recall returned 0 results — index broken'
```

### Step 6: Assign deadline = value

```python
deadline = time.time() + MATERIALIZER_TIMEOUT_S
```

**Verification:**
```python
assert marker in top_result['content'], f"Recall returned wrong memory: {top_result['content'][:100]}"
```

### Step 7: Assign materialized = False

```python
materialized = False
```

**Verification:**
```python
assert materialized, f'Memory id={pending_id} stuck in pending after {MATERIALIZER_TIMEOUT_S}s — materializer is broken'
```

### Step 8: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(MEMORY_DB, timeout=2)
```

### Step 9: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT memory_id FROM memories WHERE content LIKE ?', (f'%{marker}%',)).fetchall()
```

### Step 10: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert len(rows) >= 1, f"Memory id={pending_id} marked done but NOT in memory.db. This means the materializer's mark_done is firing but the actual engine.store() didn't complete — silent data loss."
```

### Step 11: Assign top_result = value

```python
top_result = recall_resp['results'][0]
```

**Verification:**
```python
assert marker in top_result['content'], f"Recall returned wrong memory: {top_result['content'][:100]}"
```

### Step 12: Assign resp = json.loads(...)

```python
resp = json.loads(r.read())
```

### Step 13: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(PENDING_DB, timeout=2)
```

### Step 14: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT status FROM pending_memories WHERE id = ?', (pending_id,)).fetchone()
```

### Step 15: Call conn.close()

```python
conn.close()
```

### Step 16: Call time.sleep()

```python
time.sleep(2)
```

### Step 17: Assign recall_resp = json.loads(...)

```python
recall_resp = json.loads(r.read())
```

### Step 18: Assign materialized = True

```python
materialized = True
```


## Complete Example

```python
# Workflow
"The bug that lost 18 memories: stored returns 'queued' but never\n        actually persists. This test catches that regression.\n        "
marker = f'E2E_TEST_{int(time.time() * 1000)}'
content = f'{marker} — async-pipeline E2E persistence test'
req = urllib.request.Request(f'{DAEMON_URL}/remember', data=json.dumps({'content': content}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    resp = json.loads(r.read())
assert resp['ok'] is True, f'remember failed: {resp}'
assert resp['status'] == 'queued', f'unexpected status: {resp}'
pending_id = resp['pending_id']
deadline = time.time() + MATERIALIZER_TIMEOUT_S
materialized = False
while time.time() < deadline:
    conn = sqlite3.connect(PENDING_DB, timeout=2)
    row = conn.execute('SELECT status FROM pending_memories WHERE id = ?', (pending_id,)).fetchone()
    conn.close()
    if row and row[0] == 'done':
        materialized = True
        break
    time.sleep(2)
assert materialized, f'Memory id={pending_id} stuck in pending after {MATERIALIZER_TIMEOUT_S}s — materializer is broken'
conn = sqlite3.connect(MEMORY_DB, timeout=2)
rows = conn.execute('SELECT memory_id FROM memories WHERE content LIKE ?', (f'%{marker}%',)).fetchall()
conn.close()
assert len(rows) >= 1, f"Memory id={pending_id} marked done but NOT in memory.db. This means the materializer's mark_done is firing but the actual engine.store() didn't complete — silent data loss."
with urllib.request.urlopen(f'{DAEMON_URL}/recall?q={marker}&limit=2', timeout=30) as r:
    recall_resp = json.loads(r.read())
assert recall_resp['result_count'] >= 1, f'Memory persisted but recall returned 0 results — index broken'
top_result = recall_resp['results'][0]
assert marker in top_result['content'], f"Recall returned wrong memory: {top_result['content'][:100]}"
```

## Next Steps


---

*Source: test_async_remember_e2e.py:62 | Complexity: Advanced | Last updated: 2026-05-05*