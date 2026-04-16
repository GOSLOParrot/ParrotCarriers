# How To: Add At Job Uses Default Timezone For Naive Datetime

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test add at job uses default timezone for naive datetime

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

### Step 1: Assign tool = _make_tool_with_tz(...)

```python
tool = _make_tool_with_tz(tmp_path, 'Asia/Shanghai')
```

**Verification:**
```python
assert result.startswith('Created job')
```

### Step 2: Call tool.set_context()

```python
tool.set_context('telegram', 'chat-1')
```

**Verification:**
```python
assert job.schedule.at_ms == expected
```

### Step 3: Assign result = tool._add_job(...)

```python
result = tool._add_job('Morning reminder', None, None, None, '2026-03-25T08:00:00')
```

**Verification:**
```python
assert result.startswith('Created job')
```

### Step 4: Assign job = value

```python
job = tool._cron.list_jobs()[0]
```

### Step 5: Assign expected = int(...)

```python
expected = int(datetime(2026, 3, 25, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
```

**Verification:**
```python
assert job.schedule.at_ms == expected
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
tool = _make_tool_with_tz(tmp_path, 'Asia/Shanghai')
tool.set_context('telegram', 'chat-1')
result = tool._add_job('Morning reminder', None, None, None, '2026-03-25T08:00:00')
assert result.startswith('Created job')
job = tool._cron.list_jobs()[0]
expected = int(datetime(2026, 3, 25, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
assert job.schedule.at_ms == expected
```

## Next Steps


---

*Source: test_cron_tool_list.py:276 | Complexity: Intermediate | Last updated: 2026-04-12*