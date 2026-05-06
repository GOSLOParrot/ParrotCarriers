# How To: Discover Files Ignores Large Files

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test discover files ignores large files

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.code_graph.config`
- `superlocalmemory.code_graph.models`
- `superlocalmemory.code_graph.parser`
- `tree_sitter`
- `tree_sitter_language_pack`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign config = CodeGraphConfig(...)

```python
config = CodeGraphConfig(enabled=True, repo_root=tmp_path, max_file_size_bytes=100)
```

**Verification:**
```python
assert 'small.py' in names
```

### Step 2: Assign parser = CodeParser(...)

```python
parser = CodeParser(config)
```

**Verification:**
```python
assert 'big.py' not in names
```

### Step 3: Call unknown.write_text()

```python
(tmp_path / 'big.py').write_text('x' * 200)
```

### Step 4: Call unknown.write_text()

```python
(tmp_path / 'small.py').write_text('# ok')
```

### Step 5: Assign files = parser.discover_files(...)

```python
files = parser.discover_files(tmp_path)
```

### Step 6: Assign names = value

```python
names = [f.name for f in files]
```

**Verification:**
```python
assert 'small.py' in names
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
config = CodeGraphConfig(enabled=True, repo_root=tmp_path, max_file_size_bytes=100)
parser = CodeParser(config)
(tmp_path / 'big.py').write_text('x' * 200)
(tmp_path / 'small.py').write_text('# ok')
files = parser.discover_files(tmp_path)
names = [f.name for f in files]
assert 'small.py' in names
assert 'big.py' not in names
```

## Next Steps


---

*Source: test_parser.py:63 | Complexity: Intermediate | Last updated: 2026-05-05*