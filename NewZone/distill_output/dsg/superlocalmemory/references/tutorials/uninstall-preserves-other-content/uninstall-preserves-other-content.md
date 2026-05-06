# How To: Uninstall Preserves Other Content

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Uninstall should only remove our section, keep the rest.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `stat`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.code_graph.git_hooks`

**Setup Required:**
```python
# Fixtures: git_repo
```

## Step-by-Step Guide

### Step 1: 'Uninstall should only remove our section, keep the rest.'

```python
'Uninstall should only remove our section, keep the rest.'
```

**Verification:**
```python
assert _HOOK_MARKER in content_before
```

### Step 2: Assign hook_path = value

```python
hook_path = git_repo / '.git' / 'hooks' / 'post-commit'
```

**Verification:**
```python
assert result['action'] == 'removed'
```

### Step 3: Call hook_path.write_text()

```python
hook_path.write_text("#!/bin/sh\necho 'keep this'\n")
```

**Verification:**
```python
assert 'keep this' in content_after
```

### Step 4: Call hook_path.chmod()

```python
hook_path.chmod(493)
```

**Verification:**
```python
assert _HOOK_MARKER not in content_after
```

### Step 5: Call install_post_commit_hook()

```python
install_post_commit_hook(git_repo)
```

### Step 6: Assign content_before = hook_path.read_text(...)

```python
content_before = hook_path.read_text()
```

**Verification:**
```python
assert _HOOK_MARKER in content_before
```

### Step 7: Assign result = uninstall_post_commit_hook(...)

```python
result = uninstall_post_commit_hook(git_repo)
```

**Verification:**
```python
assert result['action'] == 'removed'
```

### Step 8: Assign content_after = hook_path.read_text(...)

```python
content_after = hook_path.read_text()
```

**Verification:**
```python
assert 'keep this' in content_after
```


## Complete Example

```python
# Setup
# Fixtures: git_repo

# Workflow
'Uninstall should only remove our section, keep the rest.'
hook_path = git_repo / '.git' / 'hooks' / 'post-commit'
hook_path.write_text("#!/bin/sh\necho 'keep this'\n")
hook_path.chmod(493)
install_post_commit_hook(git_repo)
content_before = hook_path.read_text()
assert _HOOK_MARKER in content_before
result = uninstall_post_commit_hook(git_repo)
assert result['action'] == 'removed'
content_after = hook_path.read_text()
assert 'keep this' in content_after
assert _HOOK_MARKER not in content_after
```

## Next Steps


---

*Source: test_git_hooks.py:116 | Complexity: Advanced | Last updated: 2026-05-05*