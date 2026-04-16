# How To: Email Content Tagged With Email Context

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `email.message`
- `datetime`
- `imaplib`
- `pytest`
- `nanobot.bus.events`
- `nanobot.bus.queue`
- `nanobot.channels.email`
- `nanobot.channels.email`
- `email.parser`
- `email`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.'

```python
'Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.'
```

**Verification:**
```python
assert len(items) == 1
```

### Step 2: Assign raw = _make_raw_email(...)

```python
raw = _make_raw_email(subject='Tagged', body='Check the tag')
```

**Verification:**
```python
assert items[0]['content'].startswith('[EMAIL-CONTEXT]'), 'Email content must be tagged with [EMAIL-CONTEXT]'
```

### Step 3: Assign fake = _make_fake_imap(...)

```python
fake = _make_fake_imap(raw)
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
```

### Step 5: Assign cfg = _make_config(...)

```python
cfg = _make_config(verify_dkim=False, verify_spf=False)
```

### Step 6: Assign channel = EmailChannel(...)

```python
channel = EmailChannel(cfg, MessageBus())
```

### Step 7: Assign items = channel._fetch_new_messages(...)

```python
items = channel._fetch_new_messages()
```

**Verification:**
```python
assert len(items) == 1
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'Email content should be prefixed with [EMAIL-CONTEXT] for LLM isolation.'
raw = _make_raw_email(subject='Tagged', body='Check the tag')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=False, verify_spf=False)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 1
assert items[0]['content'].startswith('[EMAIL-CONTEXT]'), 'Email content must be tagged with [EMAIL-CONTEXT]'
```

## Next Steps


---

*Source: test_email_channel.py:588 | Complexity: Intermediate | Last updated: 2026-04-12*