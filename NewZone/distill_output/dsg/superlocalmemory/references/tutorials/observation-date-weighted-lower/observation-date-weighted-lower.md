# How To: Observation Date Weighted Lower

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test observation date weighted lower

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `datetime`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.retrieval.temporal_channel`
- `datetime`


## Step-by-Step Guide

### Step 1: Assign events = value

```python
events = [{'fact_id': 'f1', 'observation_date': '2026-03-11', 'referenced_date': None, 'interval_start': None, 'interval_end': None}]
```

**Verification:**
```python
assert results[0][1] <= 0.85
```

### Step 2: Assign db = _mock_db_with_events(...)

```python
db = _mock_db_with_events(events)
```

### Step 3: Assign ch = TemporalChannel(...)

```python
ch = TemporalChannel(db)
```

### Step 4: Assign parser_inst = value

```python
parser_inst = MockParser.return_value
```

### Step 5: Assign parser_inst.extract_dates_from_text.return_value = value

```python
parser_inst.extract_dates_from_text.return_value = {'referenced_date': '2026-03-11', 'interval_start': None, 'interval_end': None}
```

### Step 6: Assign results = ch.search(...)

```python
results = ch.search('what happened on March 11?', 'default')
```

**Verification:**
```python
assert results[0][1] <= 0.85
```


## Complete Example

```python
# Workflow
events = [{'fact_id': 'f1', 'observation_date': '2026-03-11', 'referenced_date': None, 'interval_start': None, 'interval_end': None}]
db = _mock_db_with_events(events)
ch = TemporalChannel(db)
with patch('superlocalmemory.retrieval.temporal_channel.TemporalParser') as MockParser:
    parser_inst = MockParser.return_value
    parser_inst.extract_dates_from_text.return_value = {'referenced_date': '2026-03-11', 'interval_start': None, 'interval_end': None}
    results = ch.search('what happened on March 11?', 'default')
if results:
    assert results[0][1] <= 0.85
```

## Next Steps


---

*Source: test_temporal_channel.py:146 | Complexity: Intermediate | Last updated: 2026-05-05*