from typing import Literal, Any
from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    title: str
    due: Literal["today", "tomorrow", "later"]
    priority: Literal["low", "medium", "high"]
    completed: bool = False


class Event(BaseModel):
    action: str
    timestamp: float


class WorkflowProfile(BaseModel):
    action_frequency: dict[str, int] = {}
    action_recency: dict[str, float] = {}
    top_actions: list[str] = []
    preferences: dict[str, Any] = {}


class Layout(BaseModel):
    layoutVersion: int = 1
    components: list[str]
    focusItems: list[str] = []
    constraints: dict[str, Any] = {"allowCustomHtml": False}


class Proposal(BaseModel):
    layout: Layout
    rationale: str
    evidence: list[str] = []


class Decision(BaseModel):
    action: Literal["accept", "reject", "adjust", "reset"]
    layout: Layout | None = None


class Version(BaseModel):
    id: int
    layout: Layout
    created_at: float
    decision: str


class Metrics(BaseModel):
    clicks: int
    seconds: float
    task_success: bool


class MetricsComparison(BaseModel):
    baseline: Metrics
    personalized: Metrics
    click_reduction_percent: float
    time_reduction_percent: float
