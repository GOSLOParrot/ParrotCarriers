# How To: Extract Text Body Falls Back To Html

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test extract text body falls back to html

## Prerequisites

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


## Step-by-Step Guide

### Step 1: Assign msg = EmailMessage(...)

```python
msg = EmailMessage()
```

**Verification:**
```python
assert 'Hello' in text
```

### Step 2: Assign unknown = 'alice@example.com'

```python
msg['From'] = 'alice@example.com'
```

**Verification:**
```python
assert 'world' in text
```

### Step 3: Assign unknown = 'bot@example.com'

```python
msg['To'] = 'bot@example.com'
```

### Step 4: Assign unknown = 'HTML only'

```python
msg['Subject'] = 'HTML only'
```

### Step 5: Call msg.add_alternative()

```python
msg.add_alternative('<p>Hello<br>world</p>', subtype='html')
```

### Step 6: Assign text = EmailChannel._extract_text_body(...)

```python
text = EmailChannel._extract_text_body(msg)
```

**Verification:**
```python
assert 'Hello' in text
```


## Complete Example

```python
# Workflow
msg = EmailMessage()
msg['From'] = 'alice@example.com'
msg['To'] = 'bot@example.com'
msg['Subject'] = 'HTML only'
msg.add_alternative('<p>Hello<br>world</p>', subtype='html')
text = EmailChannel._extract_text_body(msg)
assert 'Hello' in text
assert 'world' in text
```

## Next Steps


---

*Source: test_email_channel.py:208 | Complexity: Intermediate | Last updated: 2026-04-12*