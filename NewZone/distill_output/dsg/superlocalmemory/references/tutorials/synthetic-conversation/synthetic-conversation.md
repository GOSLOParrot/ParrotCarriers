# How To: Synthetic Conversation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Ingest 10 turns, ask 4 questions. At least 2 should score > 0.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `pathlib`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.storage.models`
- `httpx`
- `httpx`
- `httpx`
- `warnings`

**Setup Required:**
```python
# Fixtures: mode_b_engine
```

## Step-by-Step Guide

### Step 1: 'Ingest 10 turns, ask 4 questions. At least 2 should score > 0.'

```python
'Ingest 10 turns, ask 4 questions. At least 2 should score > 0.'
```

**Verification:**
```python
assert hits >= 1, f'Only {hits}/4 questions found relevant top result. Expected >= 1 (mock embeddings rely on BM25 only).'
```

### Step 2: Call self._ingest_conversation()

```python
self._ingest_conversation(mode_b_engine)
```

### Step 3: Assign hits = 0

```python
hits = 0
```

**Verification:**
```python
assert hits >= 1, f'Only {hits}/4 questions found relevant top result. Expected >= 1 (mock embeddings rely on BM25 only).'
```

### Step 4: Assign response = mode_b_engine.recall(...)

```python
response = mode_b_engine.recall(qdata['q'])
```

### Step 5: Assign top_content = unknown.fact.content.lower(...)

```python
top_content = response.results[0].fact.content.lower()
```


## Complete Example

```python
# Setup
# Fixtures: mode_b_engine

# Workflow
'Ingest 10 turns, ask 4 questions. At least 2 should score > 0.'
self._ingest_conversation(mode_b_engine)
hits = 0
for qdata in self._QUESTIONS:
    response = mode_b_engine.recall(qdata['q'])
    if len(response.results) > 0:
        top_content = response.results[0].fact.content.lower()
        if any((kw in top_content for kw in qdata['keywords'])):
            hits += 1
assert hits >= 1, f'Only {hits}/4 questions found relevant top result. Expected >= 1 (mock embeddings rely on BM25 only).'
```

## Next Steps


---

*Source: test_mode_b_ollama.py:491 | Complexity: Intermediate | Last updated: 2026-05-05*