# How To: Priority Ordering

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Generated assembly starts with identity section and ends with avoidance section.

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

### Step 1: 'Generated assembly starts with identity section and ends with avoidance section.'

```python
'Generated assembly starts with identity section and ends with avoidance section.'
```

**Verification:**
```python
assert identity_pos < avoidance_pos
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.AVOIDANCE, 'avoid1', 'jQuery'), _make_assertion(PatternCategory.IDENTITY, 'role', 'Engineer')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign assembled = gen.assemble(...)

```python
assembled = gen.assemble(prompts)
```

### Step 6: Assign identity_pos = assembled.find(...)

```python
identity_pos = assembled.find('Engineer')
```

### Step 7: Assign avoidance_pos = assembled.find(...)

```python
avoidance_pos = assembled.find('jQuery')
```

**Verification:**
```python
assert identity_pos < avoidance_pos
```


## Complete Example

```python
# Workflow
'Generated assembly starts with identity section and ends with avoidance section.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.AVOIDANCE, 'avoid1', 'jQuery'), _make_assertion(PatternCategory.IDENTITY, 'role', 'Engineer')]
prompts = gen.generate(patterns, 'profile_1')
assembled = gen.assemble(prompts)
identity_pos = assembled.find('Engineer')
avoidance_pos = assembled.find('jQuery')
if identity_pos >= 0 and avoidance_pos >= 0:
    assert identity_pos < avoidance_pos
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*