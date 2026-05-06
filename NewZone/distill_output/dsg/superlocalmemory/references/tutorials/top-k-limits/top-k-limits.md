# How To: Top K Limits

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test top k limits

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
events = [{'fact_id': f'f{i}', 'observation_date': None, 'referenced_date': f'2026-03-{10 + i:02d}', 'interval_start': None, 'interval_end': None} for i in range(15)]
```

**Verification:**
```python
assert len(results) <= 5
```

### Step 2: Assign db = _mock_db_with_events(...)

```python
db = _mock_db_with_events(events)
```

### Step 3: Assign ch = TemporalChannel(...)

```python
ch = TemporalChannel(db)
```

**Verification:**
```python
assert len(results) <= 5
```

### Step 4: Assign parser_inst = value

```python
parser_inst = MockParser.return_value
```

### Step 5: Assign parser_inst.extract_dates_from_text.return_value = value

```python
parser_inst.extract_dates_from_text.return_value = {'referenced_date': '2026-03-15', 'interval_start': None, 'interval_end': None}
```

### Step 6: Assign results = ch.search(...)

```python
results = ch.search('March 15 events', 'default', top_k=5)
```


## Complete Example

```python
# Workflow
events = [{'fact_id': f'f{i}', 'observation_date': None, 'referenced_date': f'2026-03-{10 + i:02d}', 'interval_start': None, 'interval_end': None} for i in range(15)]
db = _mock_db_with_events(events)
ch = TemporalChannel(db)
with patch('superlocalmemory.retrieval.temporal_channel.TemporalParser') as MockParser:
    parser_inst = MockParser.return_value
    parser_inst.extract_dates_from_text.return_value = {'referenced_date': '2026-03-15', 'interval_start': None, 'interval_end': None}
    results = ch.search('March 15 events', 'default', top_k=5)
assert len(results) <= 5
```

## Next Steps


---

*Source: test_temporal_channel.py:198 | Complexity: Intermediate | Last updated: 2026-05-05*