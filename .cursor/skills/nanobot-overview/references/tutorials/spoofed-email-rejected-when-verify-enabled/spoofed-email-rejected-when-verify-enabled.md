# How To: Spoofed Email Rejected When Verify Enabled

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: An email without Authentication-Results should be rejected when verify_dkim=True.

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

### Step 1: 'An email without Authentication-Results should be rejected when verify_dkim=True.'

```python
'An email without Authentication-Results should be rejected when verify_dkim=True.'
```

**Verification:**
```python
assert len(items) == 0, 'Spoofed email without auth headers should be rejected'
```

### Step 2: Assign raw = _make_raw_email(...)

```python
raw = _make_raw_email(subject='Spoofed', body='Malicious payload')
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
cfg = _make_config(verify_dkim=True, verify_spf=True)
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
assert len(items) == 0, 'Spoofed email without auth headers should be rejected'
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'An email without Authentication-Results should be rejected when verify_dkim=True.'
raw = _make_raw_email(subject='Spoofed', body='Malicious payload')
fake = _make_fake_imap(raw)
monkeypatch.setattr('nanobot.channels.email.imaplib.IMAP4_SSL', lambda _h, _p: fake)
cfg = _make_config(verify_dkim=True, verify_spf=True)
channel = EmailChannel(cfg, MessageBus())
items = channel._fetch_new_messages()
assert len(items) == 0, 'Spoofed email without auth headers should be rejected'
```

## Next Steps


---

*Source: test_email_channel.py:526 | Complexity: Intermediate | Last updated: 2026-04-12*