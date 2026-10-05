from collections import Counter
import time
from .models import Event, WorkflowProfile
from . import state


def record(action: str):
    state.events.append(Event(action=action, timestamp=time.time()))
    if len(state.events) > 500:
        state.events.pop(0)


def build_profile() -> WorkflowProfile:
    counts = Counter(e.action for e in state.events)
    recency = {}

    for action in counts:
        matching = [e for e in state.events if e.action == action]
        recency[action] = time.time() - max(e.timestamp for e in matching)

    top = [name for name, _ in counts.most_common(5)]

    return WorkflowProfile(
        action_frequency=dict(counts),
        action_recency=recency,
        top_actions=top,
        preferences=state.preferences,
    )
