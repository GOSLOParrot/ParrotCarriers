# How To: Llm Extraction

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test llm extraction

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.fact_extractor`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign response = json.dumps(...)

```python
response = json.dumps([{'text': 'Alice works at Google as a software engineer', 'fact_type': 'semantic', 'entities': ['Alice', 'Google'], 'importance': 7, 'confidence': 0.95}])
```

**Verification:**
```python
assert len(facts) == 1
```

### Step 2: Assign llm = self._mock_llm(...)

```python
llm = self._mock_llm(response)
```

**Verification:**
```python
assert facts[0].content == 'Alice works at Google as a software engineer'
```

### Step 3: Assign ext = FactExtractor(...)

```python
ext = FactExtractor(config=EncodingConfig(), llm=llm, mode=Mode.C)
```

**Verification:**
```python
assert facts[0].fact_type == FactType.SEMANTIC
```

### Step 4: Assign facts = ext.extract_facts(...)

```python
facts = ext.extract_facts(['Alice works at Google'], session_id='s1', session_date='2026-03-11')
```

**Verification:**
```python
assert 'Alice' in facts[0].entities
```


## Complete Example

```python
# Workflow
response = json.dumps([{'text': 'Alice works at Google as a software engineer', 'fact_type': 'semantic', 'entities': ['Alice', 'Google'], 'importance': 7, 'confidence': 0.95}])
llm = self._mock_llm(response)
ext = FactExtractor(config=EncodingConfig(), llm=llm, mode=Mode.C)
facts = ext.extract_facts(['Alice works at Google'], session_id='s1', session_date='2026-03-11')
assert len(facts) == 1
assert facts[0].content == 'Alice works at Google as a software engineer'
assert facts[0].fact_type == FactType.SEMANTIC
assert 'Alice' in facts[0].entities
```

## Next Steps


---

*Source: test_fact_extractor.py:269 | Complexity: Intermediate | Last updated: 2026-05-05*