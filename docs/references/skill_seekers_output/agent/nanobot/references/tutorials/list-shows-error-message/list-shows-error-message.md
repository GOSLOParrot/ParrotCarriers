# How To: List Shows Error Message

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test list shows error message

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
assert 'error' in result
```

### Step 2: Assign job = tool._cron.add_job(...)

```python
job = tool._cron.add_job(name='Failed job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
```

**Verification:**
```python
assert 'timeout' in result
```

### Step 3: Assign job.state.last_run_at_ms = 1773673200000

```python
job.state.last_run_at_ms = 1773673200000
```

### Step 4: Assign job.state.last_status = 'error'

```python
job.state.last_status = 'error'
```

### Step 5: Assign job.state.last_error = 'timeout'

```python
job.state.last_error = 'timeout'
```

### Step 6: Call tool._cron._save_store()

```python
tool._cron._save_store()
```

### Step 7: Assign result = tool._list_jobs(...)

```python
result = tool._list_jobs()
```

**Verification:**
```python
assert 'error' in result
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
tool = _make_tool(tmp_path)
job = tool._cron.add_job(name='Failed job', schedule=CronSchedule(kind='cron', expr='0 9 * * *', tz='UTC'), message='test')
job.state.last_run_at_ms = 1773673200000
job.state.last_status = 'error'
job.state.last_error = 'timeout'
tool._cron._save_store()
result = tool._list_jobs()
assert 'error' in result
assert 'timeout' in result
```

## Next Steps


---

*Source: test_cron_tool_list.py:236 | Complexity: Intermediate | Last updated: 2026-04-12*