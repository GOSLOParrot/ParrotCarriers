# How To: Workflow Pattern Prompt

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Given WORKFLOW_PATTERN patterns, prompt describes the workflow.

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

### Step 1: 'Given WORKFLOW_PATTERN patterns, prompt describes the workflow.'

```python
'Given WORKFLOW_PATTERN patterns, prompt describes the workflow.'
```

**Verification:**
```python
assert len(wf_prompts) == 1
```

### Step 2: Assign gen = SoftPromptGenerator(...)

```python
gen = SoftPromptGenerator(config=_make_config())
```

**Verification:**
```python
assert 'search' in wf_prompts[0].content
```

### Step 3: Assign patterns = value

```python
patterns = [_make_assertion(PatternCategory.WORKFLOW_PATTERN, 'flow', 'search -> read -> implement')]
```

### Step 4: Assign prompts = gen.generate(...)

```python
prompts = gen.generate(patterns, 'profile_1')
```

### Step 5: Assign wf_prompts = value

```python
wf_prompts = [p for p in prompts if p.category == 'workflow_pattern']
```

**Verification:**
```python
assert len(wf_prompts) == 1
```


## Complete Example

```python
# Workflow
'Given WORKFLOW_PATTERN patterns, prompt describes the workflow.'
gen = SoftPromptGenerator(config=_make_config())
patterns = [_make_assertion(PatternCategory.WORKFLOW_PATTERN, 'flow', 'search -> read -> implement')]
prompts = gen.generate(patterns, 'profile_1')
wf_prompts = [p for p in prompts if p.category == 'workflow_pattern']
assert len(wf_prompts) == 1
assert 'search' in wf_prompts[0].content
```

## Next Steps


---

*Source: test_soft_prompt_generator.py:228 | Complexity: Intermediate | Last updated: 2026-05-05*