# How To: Legacy Migration Has Zero Ddl

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: LLD-06 H15: no ALTER/CREATE/DROP TABLE or CREATE INDEX.

## Prerequisites

**Required Modules:**
- `__future__`
- `ast`
- `hashlib`
- `json`
- `os`
- `random`
- `sqlite3`
- `string`
- `subprocess`
- `sys`
- `textwrap`
- `pathlib`
- `pytest`
- `build_entry`
- `superlocalmemory.core.topic_signature`
- `hmac`
- `time`
- `superlocalmemory.core.topic_signature`
- `re`
- `re`
- `re`
- `re`
- `emitted_entry`


## Step-by-Step Guide

### Step 1: 'LLD-06 H15: no ALTER/CREATE/DROP TABLE or CREATE INDEX.'

```python
'LLD-06 H15: no ALTER/CREATE/DROP TABLE or CREATE INDEX.'
```

**Verification:**
```python
assert target.exists()
```

### Step 2: Assign target = value

```python
target = REPO_ROOT / 'src' / 'superlocalmemory' / 'learning' / 'legacy_migration.py'
```

**Verification:**
```python
assert pattern.search(line) is None, f'DDL found in legacy_migration.py:{idx}: {line}'
```

### Step 3: Assign text = target.read_text(...)

```python
text = target.read_text(encoding='utf-8')
```

### Step 4: Assign tree = ast.parse(...)

```python
tree = ast.parse(text)
```

### Step 5: Assign pattern = _re.compile(...)

```python
pattern = _re.compile('(?i)(ALTER\\s+TABLE|CREATE\\s+TABLE|DROP\\s+TABLE|CREATE\\s+INDEX)')
```

### Step 6: Call code_lines.append()

```python
code_lines.append(line)
```

### Step 7: Assign in_doc = any(...)

```python
in_doc = any((s <= idx <= e for s, e in doc_spans))
```

**Verification:**
```python
assert pattern.search(line) is None, f'DDL found in legacy_migration.py:{idx}: {line}'
```

### Step 8: Assign body = getattr(...)

```python
body = getattr(node, 'body', None)
```

### Step 9: Call doc_spans.append()

```python
doc_spans.append((body[0].lineno, body[0].end_lineno or body[0].lineno))
```


## Complete Example

```python
# Workflow
'LLD-06 H15: no ALTER/CREATE/DROP TABLE or CREATE INDEX.'
import re as _re
target = REPO_ROOT / 'src' / 'superlocalmemory' / 'learning' / 'legacy_migration.py'
assert target.exists()
text = target.read_text(encoding='utf-8')
tree = ast.parse(text)
code_lines: list[str] = []
for line in text.splitlines():
    code_lines.append(line)
pattern = _re.compile('(?i)(ALTER\\s+TABLE|CREATE\\s+TABLE|DROP\\s+TABLE|CREATE\\s+INDEX)')
doc_spans: list[tuple[int, int]] = []
for node in ast.walk(tree):
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        body = getattr(node, 'body', None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            doc_spans.append((body[0].lineno, body[0].end_lineno or body[0].lineno))
for idx, line in enumerate(code_lines, start=1):
    in_doc = any((s <= idx <= e for s, e in doc_spans))
    if in_doc:
        continue
    assert pattern.search(line) is None, f'DDL found in legacy_migration.py:{idx}: {line}'
```

## Next Steps


---

*Source: test_entry_generator.py:516 | Complexity: Advanced | Last updated: 2026-05-05*