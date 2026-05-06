# How To: Q1 Single Hop Relevance

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Q1: Top-5 results should mention engineer/Google/software.

Uses top-5 (not top-3) because mock hash embeddings have no real
semantic similarity — BM25 keyword overlap is the primary signal,
and "What is Alice's job?" may not keyword-match "software engineer"
in the top-3 when competing with other Alice-containing facts.

## Prerequisites

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `sys`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.math.langevin`
- `superlocalmemory.math.langevin`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Q1: Top-5 results should mention engineer/Google/software.\n\n        Uses top-5 (not top-3) because mock hash embeddings have no real\n        semantic similarity — BM25 keyword overlap is the primary signal,\n        and "What is Alice\'s job?" may not keyword-match "software engineer"\n        in the top-3 when competing with other Alice-containing facts.\n        '

```python
'Q1: Top-5 results should mention engineer/Google/software.\n\n        Uses top-5 (not top-3) because mock hash embeddings have no real\n        semantic similarity — BM25 keyword overlap is the primary signal,\n        and "What is Alice\'s job?" may not keyword-match "software engineer"\n        in the top-3 when competing with other Alice-containing facts.\n        '
```

**Verification:**
```python
assert found, f'DO NOT SHIP: Q1 top-5 results lack keywords {keywords}. Got: {[c[:60] for c in top_contents]}'
```

### Step 2: Assign resp = value

```python
resp = self.responses['q1_single_hop']
```

### Step 3: Assign keywords = value

```python
keywords = QUESTIONS['q1_single_hop']['expected_keywords']
```

### Step 4: Assign top_contents = value

```python
top_contents = [r.fact.content.lower() for r in resp.results[:5]]
```

### Step 5: Assign found = any(...)

```python
found = any((any((k in content for k in keywords)) for content in top_contents))
```

**Verification:**
```python
assert found, f'DO NOT SHIP: Q1 top-5 results lack keywords {keywords}. Got: {[c[:60] for c in top_contents]}'
```

### Step 6: Call pytest.skip()

```python
pytest.skip('No results')
```


## Complete Example

```python
# Workflow
'Q1: Top-5 results should mention engineer/Google/software.\n\n        Uses top-5 (not top-3) because mock hash embeddings have no real\n        semantic similarity — BM25 keyword overlap is the primary signal,\n        and "What is Alice\'s job?" may not keyword-match "software engineer"\n        in the top-3 when competing with other Alice-containing facts.\n        '
resp = self.responses['q1_single_hop']
if not resp.results:
    pytest.skip('No results')
keywords = QUESTIONS['q1_single_hop']['expected_keywords']
top_contents = [r.fact.content.lower() for r in resp.results[:5]]
found = any((any((k in content for k in keywords)) for content in top_contents))
assert found, f'DO NOT SHIP: Q1 top-5 results lack keywords {keywords}. Got: {[c[:60] for c in top_contents]}'
```

## Next Steps


---

*Source: test_final_locomo_mini.py:369 | Complexity: Intermediate | Last updated: 2026-05-05*