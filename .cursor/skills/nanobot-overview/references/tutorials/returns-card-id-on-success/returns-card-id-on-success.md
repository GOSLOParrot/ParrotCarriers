# How To: Returns Card Id On Success

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test returns card id on success

## Prerequisites

**Required Modules:**
- `time`
- `types`
- `unittest.mock`
- `pytest`
- `nanobot.bus.queue`
- `nanobot.channels.feishu`


## Step-by-Step Guide

### Step 1: Assign ch = _make_channel(...)

```python
ch = _make_channel()
```

**Verification:**
```python
assert result == 'card_123'
```

### Step 2: Assign ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response(...)

```python
ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response('card_123')
```

### Step 3: Assign ch._client.im.v1.message.create.return_value = _mock_send_response(...)

```python
ch._client.im.v1.message.create.return_value = _mock_send_response()
```

### Step 4: Assign result = ch._create_streaming_card_sync(...)

```python
result = ch._create_streaming_card_sync('chat_id', 'oc_chat1')
```

**Verification:**
```python
assert result == 'card_123'
```

### Step 5: Call ch._client.cardkit.v1.card.create.assert_called_once()

```python
ch._client.cardkit.v1.card.create.assert_called_once()
```

### Step 6: Call ch._client.im.v1.message.create.assert_called_once()

```python
ch._client.im.v1.message.create.assert_called_once()
```


## Complete Example

```python
# Workflow
ch = _make_channel()
ch._client.cardkit.v1.card.create.return_value = _mock_create_card_response('card_123')
ch._client.im.v1.message.create.return_value = _mock_send_response()
result = ch._create_streaming_card_sync('chat_id', 'oc_chat1')
assert result == 'card_123'
ch._client.cardkit.v1.card.create.assert_called_once()
ch._client.im.v1.message.create.assert_called_once()
```

## Next Steps


---

*Source: test_feishu_streaming.py:62 | Complexity: Intermediate | Last updated: 2026-04-12*