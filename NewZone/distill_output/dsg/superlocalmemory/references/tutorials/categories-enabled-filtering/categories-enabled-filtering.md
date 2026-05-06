# How To: Categories Enabled Filtering

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Only enabled categories produce prompts.

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

### Step 1: 'Only enabled categories produce prompts.'

```python
'Only enabled categories produce prompts.'
```

**Verification:**
```python
assert 'identity' not in categories
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config(categories_enabled=('tech_preference',)))
```

**Verification:**
```python
assert 'tech_preference' in categories
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.IDENTITY, 'role', 'Architect'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'lang', 'Python')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign categories = value

```python
categories = [p.category for p in prompts]
```

**Verification:**
```python
assert 'identity' not in categories
```


## Complete Example

```python
# Workflow
'Only enabled categories produce prompts.'
gen = SoftPromptGenerator(config=_make_config(categories_enabled=('tech_preference',)))
patterns = [_make_assertion(PatternCategory.IDENTITY, 'role', 'Architect'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'lang', 'Python')]
prompts = gen.generate(patterns, 'profile_1')
categories = [p.category for p in prompts]
assert 'identity' not in categories
assert 'tech_preference' in categories
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:338 | Complexity: Intermediate | Last updated: 2026-05-05*