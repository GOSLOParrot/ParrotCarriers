# How To: No Silent Debug Swallows In Shipped Paths

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Grep-style check — the five call sites elevated in v3.4.26 must
never regress back to ``logger.debug``. If you intentionally lower
one, update this test.

## Prerequisites

**Required Modules:**
- `__future__`
- `logging`
- `pathlib`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.core.engine_capabilities`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.schema_v3411`


## Step-by-Step Guide

### Step 1: 'Grep-style check — the five call sites elevated in v3.4.26 must\n    never regress back to ``logger.debug``. If you intentionally lower\n    one, update this test.'

```python
'Grep-style check — the five call sites elevated in v3.4.26 must\n    never regress back to ``logger.debug``. If you intentionally lower\n    one, update this test.'
```

**Verification:**
```python
assert not offences, '\n'.join(offences)
```

### Step 2: Assign root = value

```python
root = Path(__file__).resolve().parents[2] / 'src' / 'superlocalmemory'
```

### Step 3: Assign targets = value

```python
targets = [root / 'core' / 'engine.py', root / 'mcp' / 'server.py', root / 'hooks' / 'auto_recall.py', root / 'hooks' / 'auto_capture.py']
```

### Step 4: Assign forbidden_combos = value

```python
forbidden_combos = [('logger.debug', 'schema migration'), ('_logger.debug', 'pre-warmup failed'), ('_logger.debug', 'Daemon auto-start failed'), ('_logger.debug', 'Mesh auto-register failed'), ('logger.debug', 'Auto-recall failed'), ('logger.debug', 'Auto-recall query failed'), ('logger.debug', 'Auto-capture store failed')]
```

**Verification:**
```python
assert not offences, '\n'.join(offences)
```

### Step 5: Assign text = path.read_text(...)

```python
text = path.read_text()
```

### Step 6: Call offences.append()

```python
offences.append(f'{path.name}: {line.strip()}')
```


## Complete Example

```python
# Workflow
'Grep-style check — the five call sites elevated in v3.4.26 must\n    never regress back to ``logger.debug``. If you intentionally lower\n    one, update this test.'
root = Path(__file__).resolve().parents[2] / 'src' / 'superlocalmemory'
targets = [root / 'core' / 'engine.py', root / 'mcp' / 'server.py', root / 'hooks' / 'auto_recall.py', root / 'hooks' / 'auto_capture.py']
forbidden_combos = [('logger.debug', 'schema migration'), ('_logger.debug', 'pre-warmup failed'), ('_logger.debug', 'Daemon auto-start failed'), ('_logger.debug', 'Mesh auto-register failed'), ('logger.debug', 'Auto-recall failed'), ('logger.debug', 'Auto-recall query failed'), ('logger.debug', 'Auto-capture store failed')]
offences: list[str] = []
for path in targets:
    text = path.read_text()
    for needle_logger, needle_context in forbidden_combos:
        if needle_logger in text and needle_context in text:
            for line in text.splitlines():
                if needle_logger in line and needle_context in line:
                    offences.append(f'{path.name}: {line.strip()}')
assert not offences, '\n'.join(offences)
```

## Next Steps


---

*Source: test_silent_failure_elevation.py:46 | Complexity: Intermediate | Last updated: 2026-05-05*