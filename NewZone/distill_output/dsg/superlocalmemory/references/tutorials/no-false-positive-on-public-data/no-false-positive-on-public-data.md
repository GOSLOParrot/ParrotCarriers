# How To: No False Positive On Public Data

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: test no false positive on public data

## Prerequisites

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.server.routes.brain`
- `json`
- `json`
- `json`
- `json`


## Step-by-Step Guide

### Step 1: Assign payload = value

```python
payload = {'topics': [{'name': 'ai_agents', 'strength': 0.87}], 'entities': [{'name': 'Qualixar', 'mention_count': 142}], 'tech': [{'name': 'Python', 'frequency': 0.62}], 'source': '_store_patterns'}
```


## Complete Example

```python
# Workflow
payload = {'topics': [{'name': 'ai_agents', 'strength': 0.87}], 'entities': [{'name': 'Qualixar', 'mention_count': 142}], 'tech': [{'name': 'Python', 'frequency': 0.62}], 'source': '_store_patterns'}
```

## Next Steps


---

*Source: test_preference_redaction.py:54 | Complexity: Beginner | Last updated: 2026-05-05*