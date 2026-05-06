# How To: User Prompt Hook Enriches Topic Signature

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: When trigram lookup yields hits for the prompt, the signature used
to probe the context cache must differ from the no-hits signature.

Strategy:
  - Capture `read_entry_fast(session_id, signature)` calls.
  - Case A: lookup stubbed to return ``[]``  → sig_A passed in.
  - Case B: lookup stubbed to return ``[("e001", 3)]`` → sig_B passed in.
  - Assert sig_A != sig_B  AND  both contain the base topic signature.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.learning`
- `superlocalmemory.core`
- `superlocalmemory.learning`
- `superlocalmemory.core`
- `superlocalmemory.hooks`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign payload = value

```python
payload = {'session_id': 'sess_test', 'prompt': 'what is SuperLocalMemory'}
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
payload = {'session_id': 'sess_test', 'prompt': 'what is SuperLocalMemory'}
```

## Next Steps


---

*Source: test_user_prompt_hook_entity_detection.py:83 | Complexity: Beginner | Last updated: 2026-05-05*