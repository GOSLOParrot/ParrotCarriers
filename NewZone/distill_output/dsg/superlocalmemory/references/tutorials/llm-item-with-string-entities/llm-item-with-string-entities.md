# How To: Llm Item With String Entities

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test llm item with string entities

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
response = json.dumps([{'text': 'Alice is an engineer', 'entities': 'Alice', 'importance': 5, 'confidence': 0.8}])
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
assert facts[0].entities == ['Alice']
```

### Step 3: Assign ext = FactExtractor(...)

```python
ext = FactExtractor(config=EncodingConfig(), llm=llm, mode=Mode.C)
```

### Step 4: Assign facts = ext.extract_facts(...)

```python
facts = ext.extract_facts(['Alice is an engineer'], session_id='s1')
```

**Verification:**
```python
assert len(facts) == 1
```


## Complete Example

```python
# Workflow
response = json.dumps([{'text': 'Alice is an engineer', 'entities': 'Alice', 'importance': 5, 'confidence': 0.8}])
llm = self._mock_llm(response)
ext = FactExtractor(config=EncodingConfig(), llm=llm, mode=Mode.C)
facts = ext.extract_facts(['Alice is an engineer'], session_id='s1')
assert len(facts) == 1
assert facts[0].entities == ['Alice']
```

## Next Steps


---

*Source: test_fact_extractor.py:331 | Complexity: Intermediate | Last updated: 2026-05-05*