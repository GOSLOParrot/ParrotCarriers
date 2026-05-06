# How To: Quantize Json Output

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: quantize with --json produces valid JSON envelope.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `argparse`
- `dataclasses`
- `unittest.mock`
- `pytest`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.commands`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`
- `superlocalmemory.cli.main`

**Setup Required:**
```python
# Fixtures: capsys
```

## Step-by-Step Guide

### Step 1: 'quantize with --json produces valid JSON envelope.'

```python
'quantize with --json produces valid JSON envelope.'
```

**Verification:**
```python
assert envelope['success'] is True
```

### Step 2: Assign config = _mock_config(...)

```python
config = _mock_config()
```

**Verification:**
```python
assert envelope['data']['downgrades'] == 10
```

### Step 3: Assign engine = _mock_engine(...)

```python
engine = _mock_engine()
```

### Step 4: Assign mock_result = value

```python
mock_result = {'total': 50, 'downgrades': 10, 'upgrades': 3, 'skipped': 35, 'deleted': 2, 'errors': 0}
```

### Step 5: Assign captured = capsys.readouterr(...)

```python
captured = capsys.readouterr()
```

### Step 6: Assign envelope = json.loads(...)

```python
envelope = json.loads(captured.out)
```

**Verification:**
```python
assert envelope['success'] is True
```

### Step 7: Assign MockEAP.return_value.run_eap_cycle.return_value = mock_result

```python
MockEAP.return_value.run_eap_cycle.return_value = mock_result
```

### Step 8: Call cmd_quantize()

```python
cmd_quantize(Namespace(dry_run=True, profile='', json=True))
```


## Complete Example

```python
# Setup
# Fixtures: capsys

# Workflow
'quantize with --json produces valid JSON envelope.'
config = _mock_config()
engine = _mock_engine()
mock_result = {'total': 50, 'downgrades': 10, 'upgrades': 3, 'skipped': 35, 'deleted': 2, 'errors': 0}
with patch('superlocalmemory.core.engine.MemoryEngine', return_value=engine), patch('superlocalmemory.core.config.SLMConfig.load', return_value=config), patch('superlocalmemory.dynamics.eap_scheduler.EAPScheduler') as MockEAP, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'), patch('superlocalmemory.storage.quantized_store.QuantizedEmbeddingStore'), patch('superlocalmemory.math.polar_quant.PolarQuantEncoder'), patch('superlocalmemory.math.qjl.QJLEncoder'):
    MockEAP.return_value.run_eap_cycle.return_value = mock_result
    from superlocalmemory.cli.commands import cmd_quantize
    cmd_quantize(Namespace(dry_run=True, profile='', json=True))
captured = capsys.readouterr()
envelope = json.loads(captured.out)
assert envelope['success'] is True
assert envelope['data']['downgrades'] == 10
```

## Next Steps


---

*Source: test_cli_v33.py:270 | Complexity: Advanced | Last updated: 2026-05-05*