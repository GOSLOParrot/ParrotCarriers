# How To: Avoidance Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given AVOIDANCE patterns, generated prompt contains 'avoid' and the items.

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

### Step 1: "Given AVOIDANCE patterns, generated prompt contains 'avoid' and the items."

```python
"Given AVOIDANCE patterns, generated prompt contains 'avoid' and the items."
```

**Verification:**
```python
assert len(avoid_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'jQuery' in content
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.AVOIDANCE, 'avoid1', 'jQuery'), _make_assertion(PatternCategory.AVOIDANCE, 'avoid2', 'PHP')]
```

**Verification:**
```python
assert 'PHP' in content
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign avoid_prompts = value

```python
avoid_prompts = [p for p in prompts if p.category == 'avoidance']
```

**Verification:**
```python
assert len(avoid_prompts) == 1
```

### Step 6: Assign content = value

```python
content = avoid_prompts[0].content
```

**Verification:**
```python
assert 'jQuery' in content
```


## Complete Example

```python
# Workflow
"Given AVOIDANCE patterns, generated prompt contains 'avoid' and the items."
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.AVOIDANCE, 'avoid1', 'jQuery'), _make_assertion(PatternCategory.AVOIDANCE, 'avoid2', 'PHP')]
prompts = gen.generate(patterns, 'profile_1')
avoid_prompts = [p for p in prompts if p.category == 'avoidance']
assert len(avoid_prompts) == 1
content = avoid_prompts[0].content
assert 'jQuery' in content
assert 'PHP' in content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:103 | Complexity: Intermediate | Last updated: 2026-05-05*