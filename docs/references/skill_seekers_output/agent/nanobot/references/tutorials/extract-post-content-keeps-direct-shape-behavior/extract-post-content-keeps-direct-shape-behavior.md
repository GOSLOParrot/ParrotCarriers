# How To: Extract Post Content Keeps Direct Shape Behavior

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: test extract post content keeps direct shape behavior

## Prerequisites

**Required Modules:**
- `nanobot.channels.feishu`
- `nanobot.channels`
- `pytest`


## Step-by-Step Guide

### Step 1: Assign payload = value

```python
payload = {'title': 'Daily', 'content': [[{'tag': 'text', 'text': 'report'}, {'tag': 'img', 'image_key': 'img_a'}, {'tag': 'img', 'image_key': 'img_b'}]]}
```


## Complete Example

```python
# Workflow
payload = {'title': 'Daily', 'content': [[{'tag': 'text', 'text': 'report'}, {'tag': 'img', 'image_key': 'img_a'}, {'tag': 'img', 'image_key': 'img_b'}]]}
```

## Next Steps


---

*Source: test_feishu_post_content.py:37 | Complexity: Beginner | Last updated: 2026-04-12*