# How To: Project Context Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given PROJECT_CONTEXT patterns, prompt names the project.

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

### Step 1: 'Given PROJECT_CONTEXT patterns, prompt names the project.'

```python
'Given PROJECT_CONTEXT patterns, prompt names the project.'
```

**Verification:**
```python
assert len(ctx_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'SuperLocalMemory' in ctx_prompts[0].content
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.PROJECT_CONTEXT, 'project', 'SuperLocalMemory'), _make_assertion(PatternCategory.PROJECT_CONTEXT, 'detail', 'v3.3 release')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign ctx_prompts = value

```python
ctx_prompts = [p for p in prompts if p.category == 'project_context']
```

**Verification:**
```python
assert len(ctx_prompts) == 1
```


## Complete Example

```python
# Workflow
'Given PROJECT_CONTEXT patterns, prompt names the project.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.PROJECT_CONTEXT, 'project', 'SuperLocalMemory'), _make_assertion(PatternCategory.PROJECT_CONTEXT, 'detail', 'v3.3 release')]
prompts = gen.generate(patterns, 'profile_1')
ctx_prompts = [p for p in prompts if p.category == 'project_context']
assert len(ctx_prompts) == 1
assert 'SuperLocalMemory' in ctx_prompts[0].content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:247 | Complexity: Intermediate | Last updated: 2026-05-05*