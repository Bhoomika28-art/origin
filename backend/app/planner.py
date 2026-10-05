import json
import os
import httpx
from .models import WorkflowProfile, Proposal, Layout
from .schema import validate_layout


def deterministic_plan(profile: WorkflowProfile) -> Proposal:
    freq = profile.action_frequency

    focus = []

    if freq.get("quickAdd", 0) > 0:
        focus.append("quickAdd")
    if freq.get("today", 0) >= 2:
        focus.append("today")
    if freq.get("priority", 0) >= 2:
        focus.append("priority")
    if freq.get("markDone", 0) >= 2:
        focus.append("markDone")
    if freq.get("search", 0) >= 2:
        focus.append("search")

    if not focus:
        focus = ["today", "priority", "markDone"]

    components = ["FocusPanel", "TaskList", "Search"]

    layout = Layout(
        layoutVersion=2,
        components=components,
        focusItems=focus[:5],
        constraints={"allowCustomHtml": False},
    )

    ok, errors = validate_layout(layout.model_dump())
    if not ok:
        raise ValueError("; ".join(errors))

    evidence = [
        f"{name}: {count} interactions"
        for name, count in sorted(freq.items(), key=lambda x: -x[1])
        if count > 0
    ][:5]

    return Proposal(
        layout=layout,
        rationale="Frequent workflow actions were moved into a focused panel while the full task list remains available.",
        evidence=evidence,
    )


async def llm_plan(profile: WorkflowProfile) -> Proposal | None:
    base = os.getenv("LLM_BASE_URL")
    key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")

    if not (base and key and model):
        return None

    system = """
You are a UI personalization planner.
Return ONLY JSON:
{
  "layout": {
    "layoutVersion": 2,
    "components": ["..."],
    "focusItems": ["..."],
    "constraints": {"allowCustomHtml": false}
  },
  "rationale": "...",
  "evidence": ["..."]
}
Allowed components: Sidebar, TaskList, Search, Filters, FocusPanel, QuickAdd.
Allowed focusItems: quickAdd, today, priority, markDone, search.
Never output HTML, CSS, JavaScript or executable code.
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(profile.model_dump())},
        ],
        "temperature": 0.1,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{base.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)

            ok, errors = validate_layout(data["layout"])
            if not ok:
                return None

            return Proposal.model_validate(data)
    except Exception:
        return None
