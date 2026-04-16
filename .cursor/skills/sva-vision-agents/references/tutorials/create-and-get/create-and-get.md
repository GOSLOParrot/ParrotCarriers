# How To: Create And Get

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test creating and retrieving calls.

## Prerequisites

**Required Modules:**
- `datetime`
- `dotenv`
- `vision_agents.plugins`
- `vision_agents.plugins.twilio`
- `getstream.video.rtc.track_util`
- `numpy`


## Step-by-Step Guide

### Step 1: 'Test creating and retrieving calls.'

```python
'Test creating and retrieving calls.'
```

**Verification:**
```python
assert call.call_sid == 'CA123'
```

### Step 2: Assign registry = twilio.TwilioCallRegistry(...)

```python
registry = twilio.TwilioCallRegistry()
```

**Verification:**
```python
assert call.from_number == '+123'
```

### Step 3: Assign webhook_data = CallWebhookInput(...)

```python
webhook_data = CallWebhookInput(CallSid='CA123', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+123', Caller='+123', To='+456', Called='+456')
```

**Verification:**
```python
assert retrieved is call
```

### Step 4: Assign call = registry.create(...)

```python
call = registry.create('CA123', webhook_data=webhook_data)
```

**Verification:**
```python
assert call.call_sid == 'CA123'
```

### Step 5: Assign retrieved = registry.get(...)

```python
retrieved = registry.get('CA123')
```

**Verification:**
```python
assert retrieved is call
```


## Complete Example

```python
# Workflow
'Test creating and retrieving calls.'
registry = twilio.TwilioCallRegistry()
webhook_data = CallWebhookInput(CallSid='CA123', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+123', Caller='+123', To='+456', Called='+456')
call = registry.create('CA123', webhook_data=webhook_data)
assert call.call_sid == 'CA123'
assert call.from_number == '+123'
retrieved = registry.get('CA123')
assert retrieved is call
```

## Next Steps


---

*Source: test_twilio.py:55 | Complexity: Advanced | Last updated: 2026-04-12*