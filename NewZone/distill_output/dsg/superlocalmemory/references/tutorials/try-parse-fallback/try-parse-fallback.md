# How To: Try Parse Fallback

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When TemporalParser returns None, _try_parse is used as fallback.

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

### Step 1: 'When TemporalParser returns None, _try_parse is used as fallback.'

```python
'When TemporalParser returns None, _try_parse is used as fallback.'
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign events = value

```python
events = [{'fact_id': 'f1', 'observation_date': None, 'referenced_date': '2026-03-11', 'interval_start': None, 'interval_end': None}]
```

### Step 3: Assign db = _mock_db_with_events(...)

```python
db = _mock_db_with_events(events)
```

### Step 4: Assign ch = TemporalChannel(...)

```python
ch = TemporalChannel(db)
```

**Verification:**
```python
assert len(results) > 0
```

### Step 5: Assign parser_inst = value

```python
parser_inst = MockParser.return_value
```

### Step 6: Assign parser_inst.extract_dates_from_text.return_value = value

```python
parser_inst.extract_dates_from_text.return_value = {'referenced_date': None, 'interval_start': None, 'interval_end': None}
```

### Step 7: Assign results = ch.search(...)

```python
results = ch.search('March 11 2026', 'default')
```


## Complete Example

```python
# Workflow
'When TemporalParser returns None, _try_parse is used as fallback.'
events = [{'fact_id': 'f1', 'observation_date': None, 'referenced_date': '2026-03-11', 'interval_start': None, 'interval_end': None}]
db = _mock_db_with_events(events)
ch = TemporalChannel(db)
with patch('superlocalmemory.retrieval.temporal_channel.TemporalParser') as MockParser:
    parser_inst = MockParser.return_value
    parser_inst.extract_dates_from_text.return_value = {'referenced_date': None, 'interval_start': None, 'interval_end': None}
    results = ch.search('March 11 2026', 'default')
assert len(results) > 0
```

## Next Steps


---

*Source: test_temporal_channel.py:225 | Complexity: Advanced | Last updated: 2026-05-05*