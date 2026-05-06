# How To: Communication Style Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given COMMUNICATION_STYLE patterns, prompt contains style description.

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

### Step 1: 'Given COMMUNICATION_STYLE patterns, prompt contains style description.'

```python
'Given COMMUNICATION_STYLE patterns, prompt contains style description.'
```

**Verification:**
```python
assert len(style_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'concise' in style_prompts[0].content.lower() or 'direct' in style_prompts[0].content.lower()
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.COMMUNICATION_STYLE, 'style', 'concise and direct'), _make_assertion(PatternCategory.COMMUNICATION_STYLE, 'tone', 'professional')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign style_prompts = value

```python
style_prompts = [p for p in prompts if p.category == 'communication_style']
```

**Verification:**
```python
assert len(style_prompts) == 1
```


## Complete Example

```python
# Workflow
'Given COMMUNICATION_STYLE patterns, prompt contains style description.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.COMMUNICATION_STYLE, 'style', 'concise and direct'), _make_assertion(PatternCategory.COMMUNICATION_STYLE, 'tone', 'professional')]
prompts = gen.generate(patterns, 'profile_1')
style_prompts = [p for p in prompts if p.category == 'communication_style']
assert len(style_prompts) == 1
assert 'concise' in style_prompts[0].content.lower() or 'direct' in style_prompts[0].content.lower()
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:212 | Complexity: Intermediate | Last updated: 2026-05-05*