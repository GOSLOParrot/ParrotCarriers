# How To: Survives Reload

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test survives reload

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.core.registry`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign path = value

```python
path = tmp_path / 'reg.json'
```

**Verification:**
```python
assert len(agents) == 1
```

### Step 2: Assign reg1 = AgentRegistry(...)

```python
reg1 = AgentRegistry(persist_path=path)
```

**Verification:**
```python
assert agents[0]['agent_id'] == 'persistent_agent'
```

### Step 3: Call reg1.register_agent()

```python
reg1.register_agent('persistent_agent', 'persistent_profile')
```

### Step 4: Assign reg2 = AgentRegistry(...)

```python
reg2 = AgentRegistry(persist_path=path)
```

### Step 5: Assign agents = reg2.list_agents(...)

```python
agents = reg2.list_agents()
```

**Verification:**
```python
assert len(agents) == 1
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
path = tmp_path / 'reg.json'
reg1 = AgentRegistry(persist_path=path)
reg1.register_agent('persistent_agent', 'persistent_profile')
reg2 = AgentRegistry(persist_path=path)
agents = reg2.list_agents()
assert len(agents) == 1
assert agents[0]['agent_id'] == 'persistent_agent'
```

## Next Steps


---

*Source: test_registry.py:141 | Complexity: Advanced | Last updated: 2026-05-05*