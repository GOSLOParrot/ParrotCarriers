# How To: Token Budget Respected

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given 7 categories each with content, final assembled prompt is
<= max_prompt_tokens. Lower-confidence categories are dropped.

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

### Step 1: 'Given 7 categories each with content, final assembled prompt is\n    <= max_prompt_tokens. Lower-confidence categories are dropped.'

```python
'Given 7 categories each with content, final assembled prompt is\n    <= max_prompt_tokens. Lower-confidence categories are dropped.'
```

**Verification:**
```python
assert estimated_tokens <= 200
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config(max_prompt_tokens=200))
```

### Step 3: Assign patterns = value

```python
patterns = []
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign assembled = gen.assemble(...)

```python
assembled = gen.assemble(prompts)
```

### Step 6: Assign estimated_tokens = SoftPromptGenerator._estimate_tokens(...)

```python
estimated_tokens = SoftPromptGenerator._estimate_tokens(assembled)
```

**Verification:**
```python
assert estimated_tokens <= 200
```

### Step 7: Assign cat = PatternCategory(...)

```python
cat = PatternCategory(cat_val)
```

### Step 8: Call patterns.append()

```python
patterns.append(_make_assertion(category=cat, key=f'key_{cat_val}', value=f'This is a long description for {cat_val} ' * 10, confidence=0.8))
```


## Complete Example

```python
# Workflow
'Given 7 categories each with content, final assembled prompt is\n    <= max_prompt_tokens. Lower-confidence categories are dropped.'
gen = SoftPromptGenerator(config=_make_config(max_prompt_tokens=200))
patterns = []
for cat_val in ['identity', 'tech_preference', 'communication_style', 'workflow_pattern', 'project_context', 'decision_history', 'avoidance']:
    cat = PatternCategory(cat_val)
    patterns.append(_make_assertion(category=cat, key=f'key_{cat_val}', value=f'This is a long description for {cat_val} ' * 10, confidence=0.8))
prompts = gen.generate(patterns, 'profile_1')
assembled = gen.assemble(prompts)
estimated_tokens = SoftPromptGenerator._estimate_tokens(assembled)
assert estimated_tokens <= 200
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:122 | Complexity: Advanced | Last updated: 2026-05-05*