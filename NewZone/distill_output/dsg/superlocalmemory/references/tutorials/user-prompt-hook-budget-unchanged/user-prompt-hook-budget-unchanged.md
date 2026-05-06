# How To: User Prompt Hook Budget Unchanged

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: 1000 hook invocations with entity detection in the critical path
must still finish under the I1 50 ms p95 budget (we assert 50 ms hard,
far larger than the expected <10 ms on a dev box).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.learning`
- `superlocalmemory.core`
- `superlocalmemory.learning`
- `superlocalmemory.core`
- `superlocalmemory.hooks`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: '1000 hook invocations with entity detection in the critical path\n    must still finish under the I1 50 ms p95 budget (we assert 50 ms hard,\n    far larger than the expected <10 ms on a dev box).\n    '

```python
'1000 hook invocations with entity detection in the critical path\n    must still finish under the I1 50 ms p95 budget (we assert 50 ms hard,\n    far larger than the expected <10 ms on a dev box).\n    '
```

**Verification:**
```python
assert p95 < 50.0, f'hook p95 {p95:.2f} ms exceeds 50 ms I1 budget'
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(ti, 'get_or_none', lambda: _FakeIdx(), raising=False)
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(cc, 'read_entry_fast', lambda s, t: None)
```

### Step 4: Assign payload = value

```python
payload = {'session_id': 'sess_bench', 'prompt': 'budget check for SuperLocalMemory hook path'}
```

### Step 5: Assign N = 1000

```python
N = 1000
```

### Step 6: Call timings.sort()

```python
timings.sort()
```

### Step 7: Assign p95 = value

```python
p95 = timings[int(N * 0.95)]
```

**Verification:**
```python
assert p95 < 50.0, f'hook p95 {p95:.2f} ms exceeds 50 ms I1 budget'
```

### Step 8: Assign t0 = time.perf_counter_ns(...)

```python
t0 = time.perf_counter_ns()
```

### Step 9: Call _invoke_hook()

```python
_invoke_hook(monkeypatch, payload)
```

### Step 10: Call timings.append()

```python
timings.append((time.perf_counter_ns() - t0) / 1000000.0)
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'1000 hook invocations with entity detection in the critical path\n    must still finish under the I1 50 ms p95 budget (we assert 50 ms hard,\n    far larger than the expected <10 ms on a dev box).\n    '
from superlocalmemory.learning import trigram_index as ti
from superlocalmemory.core import context_cache as cc

class _FakeIdx:

    def lookup(self, text: str):
        return [('e001', 2)]
monkeypatch.setattr(ti, 'get_or_none', lambda: _FakeIdx(), raising=False)
monkeypatch.setattr(cc, 'read_entry_fast', lambda s, t: None)
payload = {'session_id': 'sess_bench', 'prompt': 'budget check for SuperLocalMemory hook path'}
N = 1000
timings: list[float] = []
for _ in range(N):
    t0 = time.perf_counter_ns()
    _invoke_hook(monkeypatch, payload)
    timings.append((time.perf_counter_ns() - t0) / 1000000.0)
timings.sort()
p95 = timings[int(N * 0.95)]
assert p95 < 50.0, f'hook p95 {p95:.2f} ms exceeds 50 ms I1 budget'
```

## Next Steps


---

*Source: test_user_prompt_hook_entity_detection.py:113 | Complexity: Advanced | Last updated: 2026-05-05*