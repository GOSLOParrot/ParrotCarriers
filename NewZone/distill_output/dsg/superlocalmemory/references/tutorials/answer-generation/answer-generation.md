# How To: Answer Generation

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: LLM generates an answer from retrieved context (not raw context dump).

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
# Fixtures: mode_b_engine, llm_backbone
```

## Step-by-Step Guide

### Step 1: 'LLM generates an answer from retrieved context (not raw context dump).'

```python
'LLM generates an answer from retrieved context (not raw context dump).'
```

**Verification:**
```python
assert len(answer.strip()) > 0, 'LLM returned empty answer'
```

### Step 2: Call self._ingest_conversation()

```python
self._ingest_conversation(mode_b_engine)
```

**Verification:**
```python
assert len(answer.strip()) > 10, f"LLM answer too short or empty: '{answer}'"
```

### Step 3: Assign response = mode_b_engine.recall(...)

```python
response = mode_b_engine.recall("What is Alice's job?")
```

### Step 4: Assign context = unknown.join(...)

```python
context = '\n'.join((f'- {r.fact.content}' for r in response.results[:5]))
```

### Step 5: Assign prompt = value

```python
prompt = f"Based ONLY on the following context, answer the question.\n\nContext:\n{context}\n\nQuestion: What is Alice's job?\nAnswer:"
```

### Step 6: Assign answer = llm_backbone.generate(...)

```python
answer = llm_backbone.generate(prompt=prompt, max_tokens=128)
```

**Verification:**
```python
assert len(answer.strip()) > 0, 'LLM returned empty answer'
```

### Step 7: Call pytest.skip()

```python
pytest.skip('No recall results — cannot test answer generation')
```


## Complete Example

```python
# Setup
# Fixtures: mode_b_engine, llm_backbone

# Workflow
'LLM generates an answer from retrieved context (not raw context dump).'
self._ingest_conversation(mode_b_engine)
response = mode_b_engine.recall("What is Alice's job?")
if not response.results:
    pytest.skip('No recall results — cannot test answer generation')
context = '\n'.join((f'- {r.fact.content}' for r in response.results[:5]))
prompt = f"Based ONLY on the following context, answer the question.\n\nContext:\n{context}\n\nQuestion: What is Alice's job?\nAnswer:"
answer = llm_backbone.generate(prompt=prompt, max_tokens=128)
assert len(answer.strip()) > 0, 'LLM returned empty answer'
assert len(answer.strip()) > 10, f"LLM answer too short or empty: '{answer}'"
```

## Next Steps


---

*Source: test_mode_b_ollama.py:510 | Complexity: Intermediate | Last updated: 2026-05-05*