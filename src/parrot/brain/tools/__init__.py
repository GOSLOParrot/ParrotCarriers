"""Brain function tools — available to the LLM during AgentSession."""

from parrot.brain.tools.animate import animate
from parrot.brain.tools.dispatch_task import dispatch_task
from parrot.brain.tools.fly_to import fly_to

ALL_TOOLS = [fly_to, animate, dispatch_task]

__all__ = ["fly_to", "animate", "dispatch_task", "ALL_TOOLS"]
