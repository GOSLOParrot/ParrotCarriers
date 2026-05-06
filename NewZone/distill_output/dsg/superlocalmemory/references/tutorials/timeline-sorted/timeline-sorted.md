# How To: Timeline Sorted

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test timeline sorted

## Prerequisites

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.encoding.temporal_parser`
- `superlocalmemory.storage.models`
- `datetime`
- `datetime`
- `dateutil.relativedelta`
- `dateutil.relativedelta`
- `datetime`


## Step-by-Step Guide

### Step 1: Assign parser = TemporalParser(...)

```python
parser = TemporalParser(reference_date='2026-03-11')
```

**Verification:**
```python
assert len(events) >= 1
```

### Step 2: Assign facts = value

```python
facts = [AtomicFact(fact_id='f1', content='Alice started in 2025-06-01', profile_id='default'), AtomicFact(fact_id='f2', content='Alice promoted in 2026-01-15', profile_id='default')]
```

**Verification:**
```python
assert dates == sorted(dates)
```

### Step 3: Assign events = parser.build_entity_timeline(...)

```python
events = parser.build_entity_timeline('ent_alice', facts, '2026-03-11')
```

**Verification:**
```python
assert len(events) >= 1
```

### Step 4: Assign dates = value

```python
dates = [e.referenced_date or e.observation_date or '' for e in events]
```

**Verification:**
```python
assert dates == sorted(dates)
```


## Complete Example

```python
# Workflow
parser = TemporalParser(reference_date='2026-03-11')
facts = [AtomicFact(fact_id='f1', content='Alice started in 2025-06-01', profile_id='default'), AtomicFact(fact_id='f2', content='Alice promoted in 2026-01-15', profile_id='default')]
events = parser.build_entity_timeline('ent_alice', facts, '2026-03-11')
assert len(events) >= 1
dates = [e.referenced_date or e.observation_date or '' for e in events]
assert dates == sorted(dates)
```

## Next Steps


---

*Source: test_temporal_parser.py:219 | Complexity: Intermediate | Last updated: 2026-05-05*