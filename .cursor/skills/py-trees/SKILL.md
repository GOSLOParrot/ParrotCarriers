---
name: py-trees
description: Use when working with py-trees behaviour trees (Behaviour, Selector, Sequence, Parallel, Blackboard V2, event-driven tick)
---

# py_trees: A Python Behaviour Tree Implementation

## Description
`py-trees` is a Python library that provides a robust implementation of behaviour trees, a hierarchical state machine designed for creating complex decision-making systems, particularly useful in robotics and AI applications. It offers a comprehensive set of tools including behaviours, decorators, composites (sequences, selectors, parallels), and a blackboard for data sharing. This skill allows Gemini to understand, generate, and troubleshoot `py-trees` code, helping users effectively design and implement behaviour trees.

**Repository:** [splintered-reality/py_trees](https://github.com/splintered-reality/py_trees)
**Homepage:** https://py-trees.readthedocs.io/
**Language:** Python
**License:** Other

## Table of Contents
*   [Description](#description)
*   [Key Concepts](#key-concepts)
*   [When to Use This Skill](#when-to-use-this-skill)
*   [⚡ Quick Reference](#-quick-reference)
    *   [1. Defining a Custom Behaviour](#1-defining-a-custom-behaviour)
    *   [2. Building a Composite Tree (Sequence, Selector, Parallel)](#2-building-a-composite-tree-sequence-selector-parallel)
    *   [3. Using the Blackboard for Data Sharing](#3-using-the-blackboard-for-data-sharing)
    *   [4. Executing a Behaviour Tree](#4-executing-a-behaviour-tree)
    *   [5. Displaying a Behaviour Tree](#5-displaying-a-behaviour-tree)
    *   [6. Using the ForEach Decorator](#6-using-the-foreach-decorator)
    *   [7. Comparing Blackboard Variables](#7-comparing-blackboard-variables)
    *   [8. Creating an Eternal Guard](#8-creating-an-eternal-guard)
*   [Practical Usage Guidance](#practical-usage-guidance)
*   [⚠️ Known Issues](#️-known-issues)
*   [Recent Releases](#recent-releases)
*   [File Structure](#file-structure)
*   [Changelog Highlights](#changelog-highlights)
*   [📖 Available References](#-available-references)

## Key Concepts

*   **Behaviour (`behaviour.Behaviour`)**: The fundamental building block of a behaviour tree. A behaviour is a single task or decision. It returns one of three statuses: `Status.SUCCESS`, `Status.FAILURE`, or `Status.RUNNING`. The `update()` method contains the behaviour's logic.
*   **Composites (`Selector`, `Sequence`, `Parallel`)**: Nodes that manage and execute their children.
    *   **`Selector`**: Tries children in order until one succeeds. If all fail, the selector fails. Can be configured `with memory` (starting from the last running child) or `without memory` (always starting from the first child).
    *   **`Sequence`**: Tries children in order until one fails. If all succeed, the sequence succeeds. Can be configured `with memory` or `without memory`.
    *   **`Parallel`**: Ticks all its children simultaneously. Its success/failure is determined by a configurable `policy` (e.g., `SuccessOnAll`, `SuccessOnOne`).
*   **Blackboard (`blackboard.Client`, `namespace`)**: A shared memory space used by behaviours to read and write data. Behaviours use `attach_blackboard_client` to create clients, `register_key` to declare access (`Access.READ`, `Access.WRITE`), and can define `namespace`s to prevent key conflicts.
*   **Decorators (`ForEach`, `StatusToBlackboard`, `EternalGuard`)**: Behaviours that wrap a single child behaviour, modifying its execution or status.
*   **BehaviourTree (`BehaviourTree`)**: The top-level class that manages the tree's execution, including `tick()` (single step) and `tick_tock()` (repeated ticking).
*   **Visitors (`Visitor`)**: Objects that traverse the behaviour tree, useful for introspection, debugging, and visualization.

## When to Use This Skill

Use this skill when you need to:
*   Design and implement decision-making logic using behaviour trees in Python.
*   Understand the core components of `py-trees` (behaviours, composites, blackboard, decorators).
*   Look up API documentation for specific `py-trees` classes or functions.
*   Find examples for common tasks like creating custom behaviours, managing data with the blackboard, or building complex tree structures.
*   Troubleshoot `py-trees` implementations or understand common design patterns.
*   Explore recent changes, new features, or known issues in the library.

## ⚡ Quick Reference

Here are practical code examples demonstrating common `py-trees` tasks.

### 1. Defining a Custom Behaviour
Create a basic behaviour that performs a task and returns a status. The core logic resides in the `update()` method.

```python
import py_trees
import py_trees.common

class MySimpleBehaviour(py_trees.behaviour.Behaviour):
    """
    A basic custom behaviour that always succeeds.
    """
    def __init__(self, name="MySimpleBehaviour"):
        super(MySimpleBehaviour, self).__init__(name)

    def update(self):
        """
        Executes the behaviour's logic.
        """
        self.feedback_message = "Executing a simple task."
        return py_trees.common.Status.SUCCESS
```

### 2. Building a Composite Tree (Sequence, Selector, Parallel)
Composites (`Sequence`, `Selector`, `Parallel`) organize and execute child behaviours. This example shows a `Sequence` with `memory`.

```python
import py_trees
import py_trees.composites
import py_trees.common
from py_trees.behaviours import Success, Failure # Built-in simple behaviours

# Create a sequence with memory (continues from where it left off if a child is RUNNING)
sequence = py_trees.composites.Sequence(
    name="My Sequence",
    memory=True, # Introduced in v2.2.x, default is True for Sequence
    children=[
        Success(name="Task 1 (Success)"),
        Failure(name="Task 2 (Failure)"),
        Success(name="Task 3 (Success)")
    ]
)

# Example of Parallel composite with a custom policy (from CHANGELOG 2.2.x)
parallel = py_trees.composites.Parallel(
    name="My Parallel",
    policy=py_trees.common.ParallelPolicy.SuccessOnAll() # Requires all children to succeed
)
parallel.add_children([
    MySimpleBehaviour("Parallel Task A"),
    MySimpleBehaviour("Parallel Task B")
])
```

### 3. Using the Blackboard for Data Sharing
The blackboard allows behaviours to share data. `attach_blackboard_client` with optional `namespace`s and `register_key` are used.

```python
import py_trees
import py_trees.blackboard
import py_trees.common
import py_trees.behaviour

class BlackboardWriter(py_trees.behaviour.Behaviour):
    def __init__(self, name="BlackboardWriter"):
        super(BlackboardWriter, self).__init__(name)
        # Attach a blackboard client, optionally with a namespace (from CHANGELOG 1.4.x)
        self.blackboard = self.attach_blackboard_client(
            name="MyWriterClient",
            namespace="robot_status"
        )
        # Register a key with write access (from CHANGELOG 1.4.x)
        self.blackboard.register_key(
            key="current_speed",
            access=py_trees.common.Access.WRITE,
            required=True # Ensure key exists before setup completes (from CHANGELOG 1.4.x)
        )

    def update(self):
        self.blackboard.current_speed = 5.0 # Set a value
        self.feedback_message = f"Set robot_status/current_speed to {self.blackboard.current_speed}"
        return py_trees.common.Status.SUCCESS

class BlackboardReader(py_trees.behaviour.Behaviour):
    def __init__(self, name="BlackboardReader"):
        super(BlackboardReader, self).__init__(name)
        self.blackboard = self.attach_blackboard_client(
            name="MyReaderClient",
            namespace="robot_status"
        )
        self.blackboard.register_key(
            key="current_speed",
            access=py_trees.common.Access.READ,
            required=True
        )

    def update(self):
        speed = self.blackboard.current_speed
        self.feedback_message = f"Read robot_status/current_speed: {speed}"
        return py_trees.common.Status.SUCCESS
```

### 4. Executing a Behaviour Tree
The `BehaviourTree` class manages the lifecycle and ticking of the tree.

```python
import py_trees
import py_trees.trees
import py_trees.behaviours

# Create a root composite for the tree
root = py_trees.composites.Sequence(name="Root Sequence")
root.add_children([
    py_trees.behaviours.CheckBlackboardVariableExists(
        name="Check Flag",
        key="initialised_flag"
    ),
    py_trees.behaviours.SetBlackboardVariable(
        name="Set Flag",
        variable_name="initialised_flag",
        value=True,
        overwrite=True
    )
])

# Create and set up the behaviour tree
tree = py_trees.trees.BehaviourTree(root)
tree.setup(timeout=15) # `setup()` with timeout (from CHANGELOG 1.2.2)

# Tick the tree once
print("\n--- Single Tick ---")
tree.tick()

# Tick the tree repeatedly (from CHANGELOG 1.1.x, `tick_tock` usage)
print("\n--- Tick-Tock ---")
for i in tree.tick_tock(period_ms=500, number_of_iterations=3):
    print(f"Tick {i} completed. Current root status: {tree.root.status}")

tree.shutdown() # Ensure clean shutdown (from CHANGELOG 1.2.x)
```

### 5. Displaying a Behaviour Tree
Visualize the tree structure and its current state in the console.

```python
import py_trees
import py_trees.display
import py_trees.trees
import py_trees.behaviours

root = py_trees.composites.Selector(name="Main Selector")
root.add_children([
    py_trees.behaviours.Running(name="Running Task"),
    py_trees.behaviours.Success(name="Succeeding Task")
])

tree = py_trees.trees.BehaviourTree(root)
tree.setup(timeout=1)
tree.tick() # Tick once to get some status

print("\n--- Unicode Tree Display ---")
# Display the tree with current status (from CHANGELOG 1.2.x `unicode_tree`)
print(py_trees.display.unicode_tree(root, show_status=True))

print("\n--- Blackboard Activity Display ---")
# Display the blackboard activity stream (from CHANGELOG 1.3.x)
# Note: For a real output, blackboard variables need to be set/read during tree ticks.
# The previous `BlackboardWriter` and `BlackboardReader` examples would populate this.
print(py_trees.display.unicode_blackboard(
    py_trees.blackboard.Blackboard(), # Global blackboard
    display_mode=py_trees.display.BlackboardDisplayMode.ACTIVITY_STREAM # From CHANGELOG 1.3.x
))
tree.shutdown()
```

### 6. Using the ForEach Decorator
The `ForEach` decorator iterates over a list, applying its child behaviour to each item.

```python
import py_trees
import py_trees.behaviour
import py_trees.decorators
import py_trees.common

class ProcessItemBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, name="ProcessItem"):
        super().__init__(name)
        self.item = None # This will be set by ForEach

    def update(self):
        if self.item == "fail":
            self.feedback_message = f"Failed to process: {self.item}"
            return py_trees.common.Status.FAILURE
        self.feedback_message = f"Successfully processed: {self.item}"
        return py_trees.common.Status.SUCCESS

# Example list to iterate over
items_to_process = ["apple", "banana", "orange", "fail", "grape"]

# The ForEach decorator (from CHANGELOG 2.4.0)
for_each = py_trees.decorators.ForEach(
    name="ProcessAllItems",
    iterate_list=items_to_process,
    behaviour=ProcessItemBehaviour() # ForEach injects the current item into `behaviour.item`
)

# In a real tree, this decorator would be part of a composite.
# Example usage (simplified, actual ticking would be via a BehaviourTree)
# for_each.setup(timeout=1)
# for _ in range(len(items_to_process)): # Simulate ticking enough times
#     for_each.tick()
#     print(f"{for_each.name} status: {for_each.status}, child status: {for_each.decorated.status}")
# for_each.shutdown()
```

### 7. Comparing Blackboard Variables
The `CompareBlackboardVariables` behaviour allows logical checks across blackboard values using comparison expressions.

```python
import py_trees
import py_trees.behaviours
import py_trees.common

# Set up a blackboard with some variables
blackboard = py_trees.blackboard.Blackboard()
blackboard.set("x", 10)
blackboard.set("y", 20)
blackboard.set("z", 10)

# A behaviour to compare blackboard variables (from CHANGELOG 2.4.0)
# This checks if 'x' is equal to 'z' AND 'y' is greater than 'x'
compare_behaviour = py_trees.behaviours.CompareBlackboardVariables(
    name="Compare X and Y",
    check=py_trees.common.ComparisonExpression(
        variable="x",
        comparator=py_trees.common.ComparisonExpression.Operator.EQUAL,
        value="z", # Can be a blackboard key or a literal
        namespace="/" # Explicitly indicate global blackboard key
    ),
    check_also=py_trees.common.ComparisonExpression(
        variable="y",
        comparator=py_trees.common.ComparisonExpression.Operator.GREATER_THAN,
        value="x",
        namespace="/"
    )
)

# Manual setup and update for demonstration
compare_behaviour.setup(timeout=1)
compare_behaviour.update()
print(f"Comparison Result: {compare_behaviour.status}") # Should be SUCCESS if 10==10 and 20>10
compare_behaviour.shutdown()

blackboard.set("x", 5) # Change 'x' to make the second check false
compare_behaviour.setup(timeout=1)
compare_behaviour.update()
print(f"Comparison Result (after change): {compare_behaviour.status}") # Should be FAILURE
compare_behaviour.shutdown()
```

### 8. Creating an Eternal Guard
The `EternalGuard` decorator continuously guards a subtree, similar to Unreal Engine's conditions.

```python
import py_trees
import py_trees.decorators
import py_trees.behaviours
import py_trees.blackboard
import py_trees.common

# Set a blackboard key that the guard will check
blackboard = py_trees.blackboard.Blackboard()
blackboard.set("is_door_open", False, overwrite=True)

# A condition behaviour that checks the blackboard key
class CheckDoorOpen(py_trees.behaviour.Behaviour):
    def __init__(self, name="CheckDoorOpen"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="CheckDoorOpenClient")
        self.blackboard.register_key(key="is_door_open", access=py_trees.common.Access.READ)

    def update(self):
        if self.blackboard.is_door_open:
            self.feedback_message = "Door is open."
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Door is closed."
            return py_trees.common.Status.FAILURE

# A behaviour that represents entering the room
class EnterRoom(py_trees.behaviour.Behaviour):
    def __init__(self, name="EnterRoom"):
        super().__init__(name)
    def update(self):
        self.feedback_message = "Entering the room."
        return py_trees.common.Status.RUNNING # Might take time

# The EternalGuard decorator (from CHANGELOG 1.2.1)
# The `CheckDoorOpen` behaviour acts as the guard condition
eternal_guard = py_trees.decorators.EternalGuard(
    name="DoorGuard",
    condition=CheckDoorOpen(),
    blackboard_entries=["is_door_open"], # Keys to monitor (from CHANGELOG 1.3.x)
    child=EnterRoom()
)

# Example of how it would behave in a tree
tree_root = py_trees.composites.Sequence(name="Main Task")
tree_root.add_children([eternal_guard])

bt = py_trees.trees.BehaviourTree(tree_root)
bt.setup(timeout=1)

print("Tick 1 (Door closed):")
bt.tick()
print(py_trees.display.unicode_tree(tree_root, show_status=True))

blackboard.set("is_door_open", True, overwrite=True)

print("\nTick 2 (Door open):")
bt.tick()
print(py_trees.display.unicode_tree(tree_root, show_status=True))

bt.shutdown()
```

## Practical Usage Guidance

*   **Start Simple**: Begin by defining individual `Behaviour` nodes for atomic tasks.
*   **Build with Composites**: Combine behaviours into `Sequence`, `Selector`, and `Parallel` nodes to form logical flows. Understand the implications of `memory=True` vs. `memory=False` for sequences and selectors.
*   **Utilize the Blackboard**: For data sharing between behaviours, leverage `blackboard.Client`. Use `namespace`s and `register_key` with `Access.READ` or `Access.WRITE` to manage data access and prevent conflicts.
*   **Visualize for Debugging**: Use `py_trees.display.unicode_tree()` to get a real-time snapshot of your tree's status in the console. For more advanced visualization, consider `py_trees_ros_viewer` or rendering `dot_tree` graphs.
*   **Explore Demos**: The `README.md` (`Getting Started` section) points to various `py-trees-demo-*` scripts, which are excellent starting points for understanding common patterns and API usage.
*   **Consult the Changelog**: The `CHANGELOG.md` is a rich source of information for new features, breaking API changes, and bug fixes across different versions. When upgrading or facing unexpected behavior, it's a good first stop.
*   **Reference ReadTheDocs**: The official documentation linked in `README.md` is comprehensive and provides detailed explanations and tutorials.

## ⚠️ Known Issues

*Recent issues from GitHub*

*   **#484**: Switch to `uv` or `pixi` instead of poetry/tox (`flag:help wanted`)
*   **#448**: Confused about the generator design?
*   **#467**: Best practices to handle namespacing to avoid blackboard key conflicts?
*   **#63**: Design by YAML (`flag:question`, `component:display`)
*   **#453**: Looking forward to a conda-forge installed version

*See `references/issues.md` for a complete list*

## Recent Releases

*   **2.4.0** (2025-11-13): Introduces `ForEach` decorator, `CompareBlackboardVariables` behaviour, and callable comparison expressions.
*   **2.3.0** (2025-01-11): Adds support for Python 3.12, drops Python 3.8.
*   **2.2.2** (2023-01-28): Major feature allowing `Sequence` and `Selector` composites to operate `with` or `without memory`. Significantly improved development environment with robust formatting, testing, and linting.

## File Structure

The `py-trees` repository is organized as follows:

```
📁 .devcontainer      - Development container configuration
📁 .github            - GitHub Actions workflows
📄 .gitignore         - Git ignore file
📄 .readthedocs.yaml  - ReadTheDocs configuration
📁 .vscode            - VSCode specific settings
📄 CHANGELOG.rst      - Detailed version history and changes
📄 CONTRIBUTING.md    - Guidelines for contributing
📄 DEVELOPING.md      - Development instructions
📄 LICENSE            - Project license
📄 Makefile           - Makefile for common tasks
📄 README.md          - Project overview and getting started guide
📁 docs               - Sphinx documentation source files
📄 package.xml        - ROS package manifest
📄 poetry.lock        - Poetry dependency lock file
📁 py_trees           - Main source code for the py_trees library
📄 pyproject.toml     - Poetry project configuration
📄 setup.py           - Setup script for installation
📁 tests              - Unit and integration tests
📄 tox.ini            - Tox configuration for testing across environments
```

*See `references/file_structure.md` for a complete list of files and directories.*

## Changelog Highlights

The `CHANGELOG.md` provides a detailed history of the project, including:

*   **2.4.0 (2025-11-13)**: New `ForEach` decorator for iterating over lists, `CompareBlackboardVariables` behaviour, and support for callables in comparison expressions.
*   **2.3.0 (2025-01-11)**: Updated Python support (3.12 added, 3.8 dropped).
*   **2.2.x (2023-01-23)**: Introduction of `Sequence` and `Selector` with and without memory, `Repeat` and `Retry` decorators, and extensive development environment improvements. Also significant **Breaking API** changes related to explicit composite arguments and behaviour refactoring.
*   **2.0.x (2019-11-15)**: Major overhaul of the blackboard system ("Blackboards v2"), including exclusive write access, key remappings, and formalised namespaces.
*   **1.4.x (2019-11-07)**: **Breaking API** for blackboard key registration (`py_trees.common.Access`), removal of `SubBlackboard`. New features include namespaced blackboard clients, required keys, and `SnapshotVisitor` tracking.
*   **1.3.x (2019-10-03)**: **Breaking API** for `EternalGuard` and blackboard behaviours. New features include read/write access configuration, blackboard activity logging, and new display options.
*   **1.2.x (2019-04-28)**: Clean `shutdown()` methods for trees and behaviours. `StatusToBlackboard` and `EternalGuard` decorators.
*   **1.0.0 (2019-01-18)**: Stable 1.0 release with refactored decorators, new parallel policies, and blackboard clearing methods.

## 📖 Available References

-   `references/README.md` - Complete README documentation
-   `references/CHANGELOG.md` - Version history and changes
-   `references/issues.md` - Recent GitHub issues
-   `references/releases.md` - Release notes
-   `references/file_structure.md` - Repository structure