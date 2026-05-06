# How To: Decision History Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given DECISION_HISTORY patterns, prompt lists decisions.

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

### Step 1: 'Given DECISION_HISTORY patterns, prompt lists decisions.'

```python
'Given DECISION_HISTORY patterns, prompt lists decisions.'
```

**Verification:**
```python
assert len(dec_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'React' in dec_prompts[0].content
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.DECISION_HISTORY, 'd1', 'Chose React over Vue')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign dec_prompts = value

```python
dec_prompts = [p for p in prompts if p.category == 'decision_history']
```

**Verification:**
```python
assert len(dec_prompts) == 1
```


## Complete Example

```python
# Workflow
'Given DECISION_HISTORY patterns, prompt lists decisions.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.DECISION_HISTORY, 'd1', 'Chose React over Vue')]
prompts = gen.generate(patterns, 'profile_1')
dec_prompts = [p for p in prompts if p.category == 'decision_history']
assert len(dec_prompts) == 1
assert 'React' in dec_prompts[0].content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:263 | Complexity: Intermediate | Last updated: 2026-05-05*