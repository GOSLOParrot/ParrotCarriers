# How To: Worker Disabled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Disabled config produces empty result with no DB operations.

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.learning.consolidation_quantization_worker`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.core.config`
- `superlocalmemory.core.consolidation_engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Disabled config produces empty result with no DB operations.'

```python
'Disabled config produces empty result with no DB operations.'
```

**Verification:**
```python
assert isinstance(result, CCQPipelineResult)
```

### Step 2: Assign config = CCQConfig(...)

```python
config = CCQConfig(enabled=False)
```

**Verification:**
```python
assert result.clusters_processed == 0
```

### Step 3: Assign mock_cons = MagicMock(...)

```python
mock_cons = MagicMock(spec=CognitiveConsolidator)
```

**Verification:**
```python
assert result.blocks_created == 0
```

### Step 4: Assign worker = CCQWorker(...)

```python
worker = CCQWorker(consolidator=mock_cons, config=config)
```

**Verification:**
```python
assert worker.should_run(store_count=100, is_session_end=True) is False
```

### Step 5: Assign result = worker.run(...)

```python
result = worker.run('some-profile')
```

**Verification:**
```python
assert isinstance(result, CCQPipelineResult)
```

### Step 6: Call mock_cons.run_pipeline.assert_not_called()

```python
mock_cons.run_pipeline.assert_not_called()
```

**Verification:**
```python
assert worker.should_run(store_count=100, is_session_end=True) is False
```


## Complete Example

```python
# Workflow
'Disabled config produces empty result with no DB operations.'
config = CCQConfig(enabled=False)
mock_cons = MagicMock(spec=CognitiveConsolidator)
worker = CCQWorker(consolidator=mock_cons, config=config)
result = worker.run('some-profile')
assert isinstance(result, CCQPipelineResult)
assert result.clusters_processed == 0
assert result.blocks_created == 0
mock_cons.run_pipeline.assert_not_called()
assert worker.should_run(store_count=100, is_session_end=True) is False
```

## Next Steps


---

*Source: test_consolidation_quantization_worker.py:216 | Complexity: Intermediate | Last updated: 2026-05-05*