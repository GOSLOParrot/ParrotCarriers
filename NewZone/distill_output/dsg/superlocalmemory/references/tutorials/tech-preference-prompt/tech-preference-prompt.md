# How To: Tech Preference Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given 3 TECH_PREFERENCE patterns, generated prompt contains all as comma-separated.

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

### Step 1: 'Given 3 TECH_PREFERENCE patterns, generated prompt contains all as comma-separated.'

```python
'Given 3 TECH_PREFERENCE patterns, generated prompt contains all as comma-separated.'
```

**Verification:**
```python
assert len(tech_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'TypeScript' in content
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.TECH_PREFERENCE, 'lang1', 'TypeScript'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'lang2', 'Python'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'framework', 'React')]
```

**Verification:**
```python
assert 'Python' in content
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

**Verification:**
```python
assert 'React' in content
```

### Step 5: Assign tech_prompts = value

```python
tech_prompts = [p for p in prompts if p.category == 'tech_preference']
```

**Verification:**
```python
assert len(tech_prompts) == 1
```

### Step 6: Assign content = value

```python
content = tech_prompts[0].content
```

**Verification:**
```python
assert 'TypeScript' in content
```


## Complete Example

```python
# Workflow
'Given 3 TECH_PREFERENCE patterns, generated prompt contains all as comma-separated.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.TECH_PREFERENCE, 'lang1', 'TypeScript'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'lang2', 'Python'), _make_assertion(PatternCategory.TECH_PREFERENCE, 'framework', 'React')]
prompts = gen.generate(patterns, 'profile_1')
tech_prompts = [p for p in prompts if p.category == 'tech_preference']
assert len(tech_prompts) == 1
content = tech_prompts[0].content
assert 'TypeScript' in content
assert 'Python' in content
assert 'React' in content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:82 | Complexity: Intermediate | Last updated: 2026-05-05*