# How To: Parse File Outside Base Dir

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test parse file outside base dir

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `vision_agents.core.instructions`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign file_path1 = value

```python
file_path1 = tmp_path / 'file1.md'
```

### Step 2: Assign base_dir = value

```python
base_dir = tmp_path / 'another-dir'
```

### Step 3: Call base_dir.mkdir()

```python
base_dir.mkdir()
```

### Step 4: Assign file_path2 = value

```python
file_path2 = base_dir / 'file1.md'
```

### Step 5: Assign input_text = value

```python
input_text = f'read @{file_path1}'
```

### Step 6: Call file_path1.write_text()

```python
file_path1.write_text('abcdef', encoding='utf-8')
```

### Step 7: Call file_path2.write_text()

```python
file_path2.write_text('abcdef', encoding='utf-8')
```

### Step 8: Call Instructions()

```python
Instructions(input_text=input_text, base_dir=base_dir)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
file_path1 = tmp_path / 'file1.md'
base_dir = tmp_path / 'another-dir'
base_dir.mkdir()
file_path2 = base_dir / 'file1.md'
input_text = f'read @{file_path1}'
file_path1.write_text('abcdef', encoding='utf-8')
file_path2.write_text('abcdef', encoding='utf-8')
with pytest.raises(InstructionsReadError, match='reason - path outside the base directory'):
    Instructions(input_text=input_text, base_dir=base_dir)
```

## Next Steps


---

*Source: test_instructions.py:55 | Complexity: Advanced | Last updated: 2026-04-12*