# How To: Lookup P99 Under 2Ms

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: 10k lookups; p99 < 2 ms. Manifest Track C.1 perf test.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `contextlib`
- `superlocalmemory.learning`
- `contextlib`
- `psutil`
- `os`
- `superlocalmemory.learning`
- `sqlite3`
- `superlocalmemory.learning.trigram_index`
- `inspect`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: index
```

## Step-by-Step Guide

### Step 1: '10k lookups; p99 < 2 ms. Manifest Track C.1 perf test.'

```python
'10k lookups; p99 < 2 ms. Manifest Track C.1 perf test.'
```

**Verification:**
```python
assert p99 < 2.0, f'p99 lookup latency {p99:.3f} ms >= 2 ms budget'
```

### Step 2: Call index.bootstrap()

```python
index.bootstrap()
```

### Step 3: Assign prompts = value

```python
prompts = ['what is SuperLocalMemory', 'Qualixar and AgentAssert architecture', 'how does TrigramIndex work in LivingBrain', 'Claude Code hook latency', 'benchmark harness for retrieval', 'tell me about PolarQuant and TurboQuant', 'Varun Bhardwaj at Accenture NeurIPS 2026', 'SkillFortify and FidelityBench comparison', 'HotPath budget for InlineEntity detection', 'ReinforcementLearn with Anthropic models']
```

### Step 4: Assign N = 10000

```python
N = 10000
```

### Step 5: Call timings.sort()

```python
timings.sort()
```

### Step 6: Assign p99 = value

```python
p99 = timings[int(N * 0.99)]
```

**Verification:**
```python
assert p99 < 2.0, f'p99 lookup latency {p99:.3f} ms >= 2 ms budget'
```

### Step 7: Call index.lookup()

```python
index.lookup(p)
```

### Step 8: Assign p = value

```python
p = prompts[i % len(prompts)]
```

### Step 9: Assign t0 = time.perf_counter_ns(...)

```python
t0 = time.perf_counter_ns()
```

### Step 10: Call index.lookup()

```python
index.lookup(p)
```

### Step 11: Call timings.append()

```python
timings.append((time.perf_counter_ns() - t0) / 1000000.0)
```


## Complete Example

```python
# Setup
# Fixtures: index

# Workflow
'10k lookups; p99 < 2 ms. Manifest Track C.1 perf test.'
index.bootstrap()
prompts = ['what is SuperLocalMemory', 'Qualixar and AgentAssert architecture', 'how does TrigramIndex work in LivingBrain', 'Claude Code hook latency', 'benchmark harness for retrieval', 'tell me about PolarQuant and TurboQuant', 'Varun Bhardwaj at Accenture NeurIPS 2026', 'SkillFortify and FidelityBench comparison', 'HotPath budget for InlineEntity detection', 'ReinforcementLearn with Anthropic models']
N = 10000
timings: list[float] = []
for p in prompts:
    index.lookup(p)
for i in range(N):
    p = prompts[i % len(prompts)]
    t0 = time.perf_counter_ns()
    index.lookup(p)
    timings.append((time.perf_counter_ns() - t0) / 1000000.0)
timings.sort()
p99 = timings[int(N * 0.99)]
assert p99 < 2.0, f'p99 lookup latency {p99:.3f} ms >= 2 ms budget'
```

## Next Steps


---

*Source: test_trigram_index.py:207 | Complexity: Advanced | Last updated: 2026-05-05*