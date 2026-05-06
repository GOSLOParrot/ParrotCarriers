# How To: Shadow Router Route Query Uses Install Token

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: route_query MUST hash install_token + query_id, not query_id alone.

Closes skeptic H-02 + H-03 — an attacker who controls query_id
cannot bias the A/B split without also reading the install_token.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `sqlite3`
- `datetime`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core.shadow_router`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core.shadow_router`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: learning_db, memory_db, tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'route_query MUST hash install_token + query_id, not query_id alone.\n\n    Closes skeptic H-02 + H-03 — an attacker who controls query_id\n    cannot bias the A/B split without also reading the install_token.\n    '

```python
'route_query MUST hash install_token + query_id, not query_id alone.\n\n    Closes skeptic H-02 + H-03 — an attacker who controls query_id\n    cannot bias the A/B split without also reading the install_token.\n    '
```

**Verification:**
```python
assert router_b.route_query('query-abc') == expected_arm
```

### Step 2: Assign router_a = sr_mod.ShadowRouter(...)

```python
router_a = sr_mod.ShadowRouter(memory_db=str(memory_db), learning_db=str(learning_db), profile_id='p')
```

**Verification:**
```python
assert router_b.route_query(q) != ('candidate' if int(naive_h, 16) % 2 == 1 else 'baseline')
```

### Step 3: Assign arm_a = router_a.route_query(...)

```python
arm_a = router_a.route_query('query-abc')
```

### Step 4: Assign new_token_file = value

```python
new_token_file = tmp_path / '.install_token_rotated'
```

### Step 5: Call new_token_file.write_text()

```python
new_token_file.write_text('c0ffee' * 16, encoding='utf-8')
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr(sp, '_install_token_path', lambda: new_token_file)
```

### Step 7: Assign router_b = sr_mod.ShadowRouter(...)

```python
router_b = sr_mod.ShadowRouter(memory_db=str(memory_db), learning_db=str(learning_db), profile_id='p')
```

### Step 8: Assign token_b = new_token_file.read_text.strip(...)

```python
token_b = new_token_file.read_text().strip()
```

### Step 9: Assign expected_h = value

```python
expected_h = hashlib.sha256((token_b + 'query-abc').encode('utf-8')).hexdigest()[:8]
```

### Step 10: Assign expected_arm = value

```python
expected_arm = 'candidate' if int(expected_h, 16) % 2 == 1 else 'baseline'
```

**Verification:**
```python
assert router_b.route_query('query-abc') == expected_arm
```

### Step 11: Assign query_only = value

```python
query_only = hashlib.sha256('query-abc'.encode('utf-8')).hexdigest()[:8]
```

### Step 12: Assign naive_arm = value

```python
naive_arm = 'candidate' if int(query_only, 16) % 2 == 1 else 'baseline'
```

### Step 13: Call pytest.fail()

```python
pytest.fail('route_query appears to ignore install_token')
```

### Step 14: Assign token_h = value

```python
token_h = hashlib.sha256((token_b + q).encode('utf-8')).hexdigest()[:8]
```

### Step 15: Assign naive_h = value

```python
naive_h = hashlib.sha256(q.encode('utf-8')).hexdigest()[:8]
```

**Verification:**
```python
assert router_b.route_query(q) != ('candidate' if int(naive_h, 16) % 2 == 1 else 'baseline')
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, memory_db, tmp_path, monkeypatch

# Workflow
'route_query MUST hash install_token + query_id, not query_id alone.\n\n    Closes skeptic H-02 + H-03 — an attacker who controls query_id\n    cannot bias the A/B split without also reading the install_token.\n    '
from superlocalmemory.core import shadow_router as sr_mod
from superlocalmemory.core import security_primitives as sp
router_a = sr_mod.ShadowRouter(memory_db=str(memory_db), learning_db=str(learning_db), profile_id='p')
arm_a = router_a.route_query('query-abc')
new_token_file = tmp_path / '.install_token_rotated'
new_token_file.write_text('c0ffee' * 16, encoding='utf-8')
monkeypatch.setattr(sp, '_install_token_path', lambda: new_token_file)
router_b = sr_mod.ShadowRouter(memory_db=str(memory_db), learning_db=str(learning_db), profile_id='p')
token_b = new_token_file.read_text().strip()
expected_h = hashlib.sha256((token_b + 'query-abc').encode('utf-8')).hexdigest()[:8]
expected_arm = 'candidate' if int(expected_h, 16) % 2 == 1 else 'baseline'
assert router_b.route_query('query-abc') == expected_arm
query_only = hashlib.sha256('query-abc'.encode('utf-8')).hexdigest()[:8]
naive_arm = 'candidate' if int(query_only, 16) % 2 == 1 else 'baseline'
if router_b.route_query('query-abc') == naive_arm:
    for q in (f'q-{i}' for i in range(1000)):
        token_h = hashlib.sha256((token_b + q).encode('utf-8')).hexdigest()[:8]
        naive_h = hashlib.sha256(q.encode('utf-8')).hexdigest()[:8]
        if int(token_h, 16) % 2 != int(naive_h, 16) % 2:
            assert router_b.route_query(q) != ('candidate' if int(naive_h, 16) % 2 == 1 else 'baseline')
            return
    pytest.fail('route_query appears to ignore install_token')
```

## Next Steps


---

*Source: test_shadow_router.py:111 | Complexity: Advanced | Last updated: 2026-05-05*