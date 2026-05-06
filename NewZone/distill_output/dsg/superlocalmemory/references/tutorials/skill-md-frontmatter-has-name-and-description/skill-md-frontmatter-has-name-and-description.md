# How To: Skill Md Frontmatter Has Name And Description

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test skill md frontmatter has name and description

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `re`
- `sqlite3`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks.adapter_base`
- `superlocalmemory.hooks.antigravity_adapter`
- `superlocalmemory.hooks`
- `ast`
- `superlocalmemory.hooks`
- `tests.test_adapters.conftest`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch, fake_recall
```

## Step-by-Step Guide

### Step 1: Assign adapter = _make_adapter(...)

```python
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
```

**Verification:**
```python
assert text.startswith('---\n')
```

### Step 2: Call adapter.sync()

```python
adapter.sync()
```

**Verification:**
```python
assert keys == {'name', 'description'}
```

### Step 3: Assign text = adapter.target_path.read_text(...)

```python
text = adapter.target_path.read_text()
```

**Verification:**
```python
assert text.startswith('---\n')
```

### Step 4: Assign end = text.index(...)

```python
end = text.index('\n---\n', 4)
```

### Step 5: Assign block = value

```python
block = text[4:end]
```

### Step 6: Assign keys = set(...)

```python
keys = set()
```

**Verification:**
```python
assert keys == {'name', 'description'}
```

### Step 7: Call keys.add()

```python
keys.add(line.split(':', 1)[0].strip())
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch, fake_recall

# Workflow
adapter = _make_adapter(tmp_path, recall=fake_recall, monkeypatch=monkeypatch)
adapter.sync()
text = adapter.target_path.read_text()
assert text.startswith('---\n')
end = text.index('\n---\n', 4)
block = text[4:end]
keys = set()
for line in block.splitlines():
    if ':' in line:
        keys.add(line.split(':', 1)[0].strip())
assert keys == {'name', 'description'}
```

## Next Steps


---

*Source: test_antigravity_adapter.py:56 | Complexity: Intermediate | Last updated: 2026-05-05*