# How To: Dispatch Dlq Surfaces Dead Letter

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test dispatch dlq surfaces dead letter

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign qd = _imports(...)

```python
qd = _imports()
```

### Step 2: Assign disp = _make_dispatcher(...)

```python
disp = _make_dispatcher(tmp_path)
```

### Step 3: Assign t = threading.Thread(...)

```python
t = threading.Thread(target=poisoner, daemon=True)
```

### Step 4: Call t.start()

```python
t.start()
```

### Step 5: Call t.join()

```python
t.join(timeout=2.0)
```

### Step 6: Call disp.close()

```python
disp.close()
```

### Step 7: Call disp.dispatch()

```python
disp.dispatch(query='x', limit_n=10, mode='B', agent_id='a', session_id='s', timeout_s=3.0)
```

### Step 8: Assign claim = disp.queue.claim_pending(...)

```python
claim = disp.queue.claim_pending(priority='high', stall_timeout_s=5.0)
```

### Step 9: Call disp.queue.mark_dead_letter()

```python
disp.queue.mark_dead_letter(claim['request_id'], reason='max_receives_exceeded')
```

### Step 10: Call time.sleep()

```python
time.sleep(0.01)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
qd = _imports()
disp = _make_dispatcher(tmp_path)

def poisoner() -> None:
    for _ in range(50):
        claim = disp.queue.claim_pending(priority='high', stall_timeout_s=5.0)
        if claim is None:
            time.sleep(0.01)
            continue
        disp.queue.mark_dead_letter(claim['request_id'], reason='max_receives_exceeded')
        return
t = threading.Thread(target=poisoner, daemon=True)
t.start()
with pytest.raises(qd.rq.DeadLetterError):
    disp.dispatch(query='x', limit_n=10, mode='B', agent_id='a', session_id='s', timeout_s=3.0)
t.join(timeout=2.0)
disp.close()
```

## Next Steps


---

*Source: test_queue_dispatcher.py:80 | Complexity: Advanced | Last updated: 2026-05-05*