# How To: Package Skill Creates Archive

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test package skill creates archive

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
skill_dir = tmp_path / 'package-me'
```

**Verification:**
```python
assert archive_path == tmp_path / 'dist' / 'package-me.skill'
```

### Step 2: Call skill_dir.mkdir()

```python
skill_dir.mkdir()
```

**Verification:**
```python
assert archive_path.exists()
```

### Step 3: Call unknown.write_text()

```python
(skill_dir / 'SKILL.md').write_text('---\nname: package-me\ndescription: Package this skill.\n---\n# Skill\n', encoding='utf-8')
```

**Verification:**
```python
assert 'package-me/SKILL.md' in names
```

### Step 4: Assign scripts_dir = value

```python
scripts_dir = skill_dir / 'scripts'
```

**Verification:**
```python
assert 'package-me/scripts/helper.py' in names
```

### Step 5: Call scripts_dir.mkdir()

```python
scripts_dir.mkdir()
```

### Step 6: Call unknown.write_text()

```python
(scripts_dir / 'helper.py').write_text("print('ok')\n", encoding='utf-8')
```

### Step 7: Assign archive_path = package_skill.package_skill(...)

```python
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
```

**Verification:**
```python
assert archive_path == tmp_path / 'dist' / 'package-me.skill'
```

### Step 8: Assign names = set(...)

```python
names = set(archive.namelist())
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
skill_dir = tmp_path / 'package-me'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('---\nname: package-me\ndescription: Package this skill.\n---\n# Skill\n', encoding='utf-8')
scripts_dir = skill_dir / 'scripts'
scripts_dir.mkdir()
(scripts_dir / 'helper.py').write_text("print('ok')\n", encoding='utf-8')
archive_path = package_skill.package_skill(skill_dir, tmp_path / 'dist')
assert archive_path == tmp_path / 'dist' / 'package-me.skill'
assert archive_path.exists()
with zipfile.ZipFile(archive_path, 'r') as archive:
    names = set(archive.namelist())
assert 'package-me/SKILL.md' in names
assert 'package-me/scripts/helper.py' in names
```

## Next Steps


---

*Source: test_skill_creator_scripts.py:77 | Complexity: Advanced | Last updated: 2026-04-12*