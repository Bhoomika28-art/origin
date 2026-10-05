# AdaptUI-Agent

A runnable proof-of-concept for ORIGIN-2026-PS06: AI-Customized User Interfaces.

## Architecture

User/Task App
→ Telemetry
→ Workflow Profile
→ AI Planner
→ UI Gateway
→ Policy Engine
→ Renderer
→ Audit/Version Store

The AI planner returns a structured layout configuration. It never returns executable HTML/JS.

## Requirements

- Python 3.10+
- Node.js 18+

## Run backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000
API docs: http://localhost:8000/docs

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Optional real LLM

The project works without an API key using a deterministic demo planner.

To connect an OpenAI-compatible structured-output endpoint, create
`backend/.env`:

```env
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=your_key
LLM_MODEL=your_model
```

The planner still validates every returned layout before it can be rendered.

## Demo flow

1. Open the dashboard.
2. Perform repeated actions such as Today, High Priority and Mark Done.
3. Click "Analyze workflow".
4. Click "Generate AI layout".
5. Preview the proposed layout.
6. Accept, reject, or reset it.
7. Compare baseline and personalized task metrics.
8. Open Version History and rollback if required.
