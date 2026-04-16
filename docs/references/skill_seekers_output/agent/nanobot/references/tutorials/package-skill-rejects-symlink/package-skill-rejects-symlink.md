# How To: Package Skill Rejects Symlink

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test package skill rejects symlink

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `importlib`
- `shutil`
- `sys`
- `zipfile`
- `pathlib`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign skill_dir = value

```python
skill_dir = tmp_path / 'symlink-skill'
```

**Verification:**
```python
assert archive_path is None
```

### Step 2: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert not (tmp_path / 'dist' / 'symlink-skill.skill').exists()
```

### Step 3: Call unknown.write_text()

```python
(skill_dir / 'SKILL.md').write_text('---\nname: symlink-skill\ndescription: Reject symlinks during packaging.\n---\n# Skill\n', encoding='utf-8')
```

### Step 4: Assign scripts_dir = value

```python
scripts_dir = skill_dir / 'scripts'
```

### Step 5: Call scripts_dir.mkdir()

```python
scripts_dir.mkdir()
```

### Step 6: Assign target = value

```python
target = tmp_path / 'outside.txt'
```

### Step 7: Call target.write_text()

```python
target.write_text('secret\n', encoding='utf-8')
```

### Step 8: Assign link = value

```python
link = scripts_dir / 'outside.txt'
```

### Step 9: Assign archive_path = package_skill.package_skill(...)

```python
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
```

**Verification:**
```python
assert archive_path is None
```

### Step 10: Call link.symlink_to()

```python
link.symlink_to(target)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
skill_dir = tmp_path / 'symlink-skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('---\nname: symlink-skill\ndescription: Reject symlinks during packaging.\n---\n# Skill\n', encoding='utf-8')
scripts_dir = skill_dir / 'scripts'
scripts_dir.mkdir()
target = tmp_path / 'outside.txt'
target.write_text('secret\n', encoding='utf-8')
link = scripts_dir / 'outside.txt'
try:
    link.symlink_to(target)
except (OSError, NotImplementedError):
    return
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
assert archive_path is None
assert not (tmp_path / 'dist' / 'symlink-skill.skill').exists()
```

## Next Steps


---

*Source: test_skill_creator_scripts.py:102 | Complexity: Advanced | Last updated: 2026-04-12*