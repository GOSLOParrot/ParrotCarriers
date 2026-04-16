# How To: Backward Compat Verify Disabled

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.

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

### Step 1: 'When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.'

```python
'When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.'
```

**Verification:**
```python
assert len(items) == 1, 'With verification disabled, emails should be accepted as before'
```

### Step 2: Assign raw = _make_raw_email(...)

```python
raw = _make_raw_email(subject='NoAuth', body='No auth headers present')
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
assert len(items) == 1, 'With verification disabled, emails should be accepted as before'
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'When verify_dkim=False and verify_spf=False, emails without auth headers are accepted.'
raw = _make_raw_email(subject='NoAuth', body='No auth headers present')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=False, verify_spf=False)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 1, 'With verification disabled, emails should be accepted as before'
```

## Next Steps


---

*Source: test_email_channel.py:575 | Complexity: Intermediate | Last updated: 2026-04-12*