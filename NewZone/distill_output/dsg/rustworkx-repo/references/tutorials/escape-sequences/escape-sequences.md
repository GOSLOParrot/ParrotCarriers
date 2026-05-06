# How To: Escape Sequences

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test escape sequences

## Prerequisites

**Required Modules:**
- `os`
- `subprocess`
- `tempfile`
- `unittest`
- `rustworkx`
- `rustworkx.visualization`
- `PIL`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.path_graph(...)

```python
graph = rustworkx.generators.path_graph(2)
```

### Step 2: Assign escape_sequences = value

```python
escape_sequences = {'\\n': '\n', '\\t': '\t', "\\'": "'", '\\"': '"', '\\\\': '\\', '\\r': '\r', '\\b': '\x08', '\\f': '\x0c'}
```

### Step 3: Assign dot_str = graph.to_dot(...)

```python
dot_str = graph.to_dot(node_attr)
```

### Step 4: Call self.assertIn()

```python
self.assertIn(escaped_seq, dot_str, f'Escape sequence {escaped_seq} not found in dot output')
```

### Step 5: """

```python
"""
                    Define node attributes including escape sequences for labels and tooltips.
                    """
```

### Step 6: Assign label = value

```python
label = f'label{escaped_seq}'
```

### Step 7: Assign tooltip = value

```python
tooltip = f'tooltip{escaped_seq}'
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.path_graph(2)
escape_sequences = {'\\n': '\n', '\\t': '\t', "\\'": "'", '\\"': '"', '\\\\': '\\', '\\r': '\r', '\\b': '\x08', '\\f': '\x0c'}
for escaped_seq, raw_seq in escape_sequences.items():
    with self.subTest(chr=ord(raw_seq)):

        def node_attr(node):
            """
                    Define node attributes including escape sequences for labels and tooltips.
                    """
            label = f'label{escaped_seq}'
            tooltip = f'tooltip{escaped_seq}'
            return {'label': label, 'tooltip': tooltip}
        dot_str = graph.to_dot(node_attr)
        self.assertIn(escaped_seq, dot_str, f'Escape sequence {escaped_seq} not found in dot output')
```

## Next Steps


---

*Source: test_graphviz.py:202 | Complexity: Intermediate | Last updated: 2026-05-05*