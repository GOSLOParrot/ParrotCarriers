# How To: Identity Prompt Generation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given IDENTITY patterns with role='Senior Architect' and domains='AI, cloud',
generated prompt contains those values.

## Prerequisites

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.parameterization.pattern_extractor`
- `superlocalmemory.parameterization.soft_prompt_generator`
- `unittest.mock`
- `unittest.mock`


## Step-by-Step Guide

### Step 1: "Given IDENTITY patterns with role='Senior Architect' and domains='AI, cloud',\n    generated prompt contains those values."

```python
"Given IDENTITY patterns with role='Senior Architect' and domains='AI, cloud',\n    generated prompt contains those values."
```

**Verification:**
```python
assert len(prompts) >= 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert len(identity_prompts) == 1
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(category=PatternCategory.IDENTITY, key='role', value='Senior Architect'), _make_assertion(category=PatternCategory.IDENTITY, key='expertise', value='AI and cloud', confidence=0.75)]
```

**Verification:**
```python
assert 'Senior Architect' in content
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

**Verification:**
```python
assert len(prompts) >= 1
```

### Step 5: Assign identity_prompts = value

```python
identity_prompts = [p for p in prompts if p.category == 'identity']
```

**Verification:**
```python
assert len(identity_prompts) == 1
```

### Step 6: Assign content = value

```python
content = identity_prompts[0].content
```

**Verification:**
```python
assert 'Senior Architect' in content
```


## Complete Example

```python
# Workflow
"Given IDENTITY patterns with role='Senior Architect' and domains='AI, cloud',\n    generated prompt contains those values."
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(category=PatternCategory.IDENTITY, key='role', value='Senior Architect'), _make_assertion(category=PatternCategory.IDENTITY, key='expertise', value='AI and cloud', confidence=0.75)]
prompts = gen.generate(patterns, 'profile_1')
assert len(prompts) >= 1
identity_prompts = [p for p in prompts if p.category == 'identity']
assert len(identity_prompts) == 1
content = identity_prompts[0].content
assert 'Senior Architect' in content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:53 | Complexity: Intermediate | Last updated: 2026-05-05*