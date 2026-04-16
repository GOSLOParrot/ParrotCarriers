# How To: List Shows Last Run State

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test list shows last run state

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `datetime`
- `nanobot.agent.tools.cron`
- `nanobot.cron.service`
- `nanobot.cron.types`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign tool = _make_tool(...)

```python
tool = _make_tool(tmp_path)
```

**Verification:**
```python
assert 'Last run:' in result
```

### Step 2: Assign job = tool._cron.add_job(...)

```python
job = tool._cron.add_job(name='Stateful job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
```

**Verification:**
```python
assert 'ok' in result
```

### Step 3: Assign job.state.last_run_at_ms = 1773673200000

```python
job.state.last_run_at_ms = 1773673200000
```

**Verification:**
```python
assert '(UTC)' in result
```

### Step 4: Assign job.state.last_status = 'ok'

```python
job.state.last_status = 'ok'
```

### Step 5: Call tool._cron._save_store()

```python
tool._cron._save_store()
```

### Step 6: Assign result = tool._list_jobs(...)

```python
result = tool._list_jobs()
```

**Verification:**
```python
assert 'Last run:' in result
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
tool = _make_tool(tmp_path)
job = tool._cron.add_job(name='Stateful job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
job.state.last_run_at_ms = 1773673200000
job.state.last_status = 'ok'
tool._cron._save_store()
result = tool._list_jobs()
assert 'Last run:' in result
assert 'ok' in result
assert '(UTC)' in result
```

## Next Steps


---

*Source: test_cron_tool_list.py:218 | Complexity: Intermediate | Last updated: 2026-04-12*