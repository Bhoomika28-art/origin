from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time

from . import state
from .models import Decision, Layout, Metrics, MetricsComparison
from .telemetry import record, build_profile
from .schema import validate_layout
from .planner import deterministic_plan, llm_plan

app = FastAPI(title="AdaptUI-Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "AdaptUI-Agent"}


@app.get("/api/tasks")
def get_tasks():
    return [t.model_dump() for t in state.tasks]


@app.post("/api/events/{action}")
def event(action: str):
    allowed = {"today", "priority", "markDone", "quickAdd", "search", "taskOpen"}
    if action not in allowed:
        raise HTTPException(400, "Unknown telemetry action")
    record(action)
    return {"ok": True}


@app.get("/api/profile")
def profile():
    return build_profile().model_dump()


@app.get("/api/layout")
def layout():
    return state.current_layout.model_dump()


@app.post("/api/proposal")
async def proposal():
    p = build_profile()

    # Use an external LLM only if configured; otherwise use a deterministic demo planner.
    generated = await llm_plan(p)
    if generated is None:
        generated = deterministic_plan(p)

    ok, errors = validate_layout(generated.layout.model_dump())
    if not ok:
        raise HTTPException(422, {"errors": errors})

    return generated.model_dump()


@app.post("/api/decision")
def decision(body: Decision):
    if body.action == "reject":
        return {"status": "rejected", "layout": state.current_layout.model_dump()}

    if body.action == "reset":
        state.current_layout = state.default_layout
        state.versions.append(
            __import__("app.models", fromlist=["Version"]).Version(
                id=len(state.versions) + 1,
                layout=state.default_layout,
                created_at=time.time(),
                decision="reset",
            )
        )
        return {"status": "reset", "layout": state.current_layout.model_dump()}

    if body.layout is None:
        raise HTTPException(400, "layout is required")

    ok, errors = validate_layout(body.layout.model_dump())
    if not ok:
        raise HTTPException(422, {"errors": errors})

    state.current_layout = body.layout
    state.versions.append(
        __import__("app.models", fromlist=["Version"]).Version(
            id=len(state.versions) + 1,
            layout=body.layout,
            created_at=time.time(),
            decision=body.action,
        )
    )

    return {"status": body.action, "layout": state.current_layout.model_dump()}


@app.get("/api/versions")
def versions():
    return [v.model_dump() for v in state.versions]


@app.post("/api/rollback/{version_id}")
def rollback(version_id: int):
    target = next((v for v in state.versions if v.id == version_id), None)
    if not target:
        raise HTTPException(404, "Version not found")

    state.current_layout = target.layout
    state.versions.append(
        __import__("app.models", fromlist=["Version"]).Version(
            id=len(state.versions) + 1,
            layout=target.layout,
            created_at=time.time(),
            decision=f"rollback->{version_id}",
        )
    )
    return {"status": "rolled_back", "layout": state.current_layout.model_dump()}


@app.post("/api/metrics/compare", response_model=MetricsComparison)
def compare(metrics: dict):
    baseline = Metrics.model_validate(metrics["baseline"])
    personalized = Metrics.model_validate(metrics["personalized"])

    click_reduction = 0 if baseline.clicks == 0 else (
        (baseline.clicks - personalized.clicks) / baseline.clicks * 100
    )
    time_reduction = 0 if baseline.seconds == 0 else (
        (baseline.seconds - personalized.seconds) / baseline.seconds * 100
    )

    return MetricsComparison(
        baseline=baseline,
        personalized=personalized,
        click_reduction_percent=round(click_reduction, 2),
        time_reduction_percent=round(time_reduction, 2),
    )
