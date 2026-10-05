import time
from .models import Task, Event, Layout, Version

tasks = [
    Task(id=1, title="Submit assignment", due="today", priority="high"),
    Task(id=2, title="Team meeting", due="today", priority="high"),
    Task(id=3, title="Read research paper", due="later", priority="medium"),
    Task(id=4, title="Plan project", due="tomorrow", priority="low"),
    Task(id=5, title="Review notes", due="today", priority="medium"),
]

events: list[Event] = []
preferences = {
    "compact": False,
    "focusMode": True,
}

default_layout = Layout(
    layoutVersion=1,
    components=["Sidebar", "TaskList", "Search", "Filters"],
    focusItems=[],
)

current_layout = default_layout
versions: list[Version] = [
    Version(id=1, layout=default_layout, created_at=time.time(), decision="default")
]
