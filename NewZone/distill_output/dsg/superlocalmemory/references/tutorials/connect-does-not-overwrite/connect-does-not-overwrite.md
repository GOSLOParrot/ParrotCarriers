# How To: Connect Does Not Overwrite

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test connect does not overwrite

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pytest`
- `pathlib`
- `superlocalmemory.hooks.ide_connector`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign claude_dir = value

```python
claude_dir = tmp_path / '.claude'
```

**Verification:**
```python
assert 'My Custom Rules' in content
```

### Step 2: Call claude_dir.mkdir()

```python
claude_dir.mkdir()
```

**Verification:**
```python
assert SLM_MARKER in content
```

### Step 3: Assign claude_md = value

```python
claude_md = claude_dir / 'CLAUDE.md'
```

### Step 4: Call claude_md.write_text()

```python
claude_md.write_text('# My Custom Rules\nDo not touch this.\n')
```

### Step 5: Assign connector = IDEConnector(...)

```python
connector = IDEConnector(home=tmp_path)
```

### Step 6: Call connector.connect()

```python
connector.connect('claude_code')
```

### Step 7: Assign content = claude_md.read_text(...)

```python
content = claude_md.read_text()
```

**Verification:**
```python
assert 'My Custom Rules' in content
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
claude_dir = tmp_path / '.claude'
claude_dir.mkdir()
claude_md = claude_dir / 'CLAUDE.md'
claude_md.write_text('# My Custom Rules\nDo not touch this.\n')
connector = IDEConnector(home=tmp_path)
connector.connect('claude_code')
content = claude_md.read_text()
assert 'My Custom Rules' in content
assert SLM_MARKER in content
```

## Next Steps


---

*Source: test_ide_connector.py:58 | Complexity: Intermediate | Last updated: 2026-05-05*