# How To: Format Helpers Render

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test format helpers render

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks.context_payload`
- `tests.test_adapters.conftest`

**Setup Required:**
```python
# Fixtures: fake_recall
```

## Step-by-Step Guide

### Step 1: Assign payload = build_payload(...)

```python
payload = build_payload('default', 'project', Path('/tmp'), recall_fn=fake_recall)
```

**Verification:**
```python
assert 'ai_agents' in out_topics
```

### Step 2: Assign out_topics = format_topics(...)

```python
out_topics = format_topics(payload)
```

**Verification:**
```python
assert '(0.87)' in out_topics
```

### Step 3: Assign out_entities = format_entities(...)

```python
out_entities = format_entities(payload)
```

**Verification:**
```python
assert 'Qualixar' in out_entities
```

### Step 4: Assign out_decisions = format_decisions(...)

```python
out_decisions = format_decisions(payload)
```

**Verification:**
```python
assert '(142)' in out_entities
```

### Step 5: Assign out_mem = format_memories(...)

```python
out_mem = format_memories(payload)
```

**Verification:**
```python
assert 'AGPL' in out_decisions
```


## Complete Example

```python
# Setup
# Fixtures: fake_recall

# Workflow
payload = build_payload('default', 'project', Path('/tmp'), recall_fn=fake_recall)
out_topics = format_topics(payload)
assert 'ai_agents' in out_topics
assert '(0.87)' in out_topics
out_entities = format_entities(payload)
assert 'Qualixar' in out_entities
assert '(142)' in out_entities
out_decisions = format_decisions(payload)
assert 'AGPL' in out_decisions
out_mem = format_memories(payload)
assert 'memory one' in out_mem
```

## Next Steps


---

*Source: test_content_builder.py:91 | Complexity: Intermediate | Last updated: 2026-05-05*