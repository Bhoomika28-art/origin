import { useEffect, useState } from "react";

const API = "http://localhost:8000/api";

type Task = {
  id: number;
  title: string;
  due: "today" | "tomorrow" | "later";
  priority: "low" | "medium" | "high";
  completed: boolean;
};

type Layout = {
  layoutVersion: number;
  components: string[];
  focusItems: string[];
  constraints: { allowCustomHtml: boolean };
};

type Proposal = {
  layout: Layout;
  rationale: string;
  evidence: string[];
};

type Profile = {
  action_frequency: Record<string, number>;
  action_recency: Record<string, number>;
  top_actions: string[];
};

async function api(path: string, options?: RequestInit) {
  const response = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [layout, setLayout] = useState<Layout | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Default interface active.");

  async function refresh() {
    const [t, l, v] = await Promise.all([
      api("/tasks"),
      api("/layout"),
      api("/versions")
    ]);
    setTasks(t);
    setLayout(l);
    setVersions(v);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function track(action: string) {
    await api(`/events/${action}`, { method: "POST" });
  }

  async function analyze() {
    setProfile(await api("/profile"));
    setMessage("Workflow profile updated.");
  }

  async function generate() {
    setLoading(true);
    try {
      setProfile(await api("/profile"));
      const p = await api("/proposal", { method: "POST" });
      setProposal(p);
      setMessage("AI proposal generated and policy-validated.");
    } finally {
      setLoading(false);
    }
  }

  async function decide(action: "accept" | "reject" | "reset") {
    const body: any = { action };
    if (action === "accept" && proposal) body.layout = proposal.layout;
    const result = await api("/decision", {
      method: "POST",
      body: JSON.stringify(body)
    });
    setLayout(result.layout);
    setProposal(null);
    await refresh();
    setMessage(
      action === "accept"
        ? "Personalized layout activated."
        : action === "reset"
        ? "Returned to default layout."
        : "Proposal rejected."
    );
  }

  async function rollback(id: number) {
    const result = await api(`/rollback/${id}`, { method: "POST" });
    setLayout(result.layout);
    await refresh();
    setMessage(`Rolled back to version ${id}.`);
  }

  async function toggleTask(id: number) {
    setTasks(prev =>
      prev.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
    );
    await track("markDone");
  }

  if (!layout) return <div className="loading">Loading AdaptUI-Agent...</div>;

  const focus = new Set(layout.focusItems);

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">ORIGIN 2026 • AI CUSTOMIZED UI</div>
          <h1>AdaptUI-Agent</h1>
          <p>Same task data. Different composition. Same core functionality.</p>
        </div>
        <div className="status">
          <span className="dot" /> {layout.layoutVersion === 1 ? "Default" : "Personalized"}
        </div>
      </header>

      <main className="content">
        <section className="control-panel">
          <div>
            <h2>AI Personalization Control Center</h2>
            <p>{message}</p>
          </div>
          <div className="actions">
            <button onClick={analyze}>Analyze workflow</button>
            <button className="primary" onClick={generate} disabled={loading}>
              {loading ? "Thinking..." : "Generate AI layout"}
            </button>
            <button onClick={() => decide("reset")}>Reset default</button>
          </div>
        </section>

        <section className="grid">
          <aside className="sidebar card">
            <h3>Navigation</h3>
            <button onClick={() => track("today")}>Today</button>
            <button onClick={() => track("priority")}>High Priority</button>
            <button onClick={() => track("search")}>Search</button>
            <button onClick={() => track("quickAdd")}>Quick Add</button>
            <hr />
            <small>Allowed components only</small>
          </aside>

          <section className="workspace">
            {focus.size > 0 && (
              <div className="focus card">
                <div className="section-title">
                  <span>FOCUS VIEW</span>
                  <b>AI-composed</b>
                </div>
                <div className="focus-grid">
                  {focus.has("today") && <FocusButton label="Today" onClick={() => track("today")} />}
                  {focus.has("priority") && <FocusButton label="High priority" onClick={() => track("priority")} />}
                  {focus.has("quickAdd") && <FocusButton label="+ Quick add" onClick={() => track("quickAdd")} />}
                  {focus.has("markDone") && <FocusButton label="Mark done" onClick={() => track("markDone")} />}
                  {focus.has("search") && <FocusButton label="Search" onClick={() => track("search")} />}
                </div>
              </div>
            )}

            <div className="card task-card">
              <div className="section-title">
                <span>TASK LIST</span>
                <b>{tasks.filter(t => !t.completed).length} active</b>
              </div>

              {tasks.map(task => (
                <div className={`task ${task.completed ? "completed" : ""}`} key={task.id}>
                  <button className="check" onClick={() => toggleTask(task.id)}>
                    {task.completed ? "✓" : ""}
                  </button>
                  <div className="task-main">
                    <strong>{task.title}</strong>
                    <span>{task.due}</span>
                  </div>
                  <span className={`priority ${task.priority}`}>{task.priority}</span>
                </div>
              ))}
            </div>
          </section>

          <aside className="rightbar">
            {profile && (
              <div className="card">
                <div className="section-title"><span>WORKFLOW PROFILE</span></div>
                {Object.entries(profile.action_frequency).length === 0 ? (
                  <p className="muted">No interaction data yet.</p>
                ) : (
                  Object.entries(profile.action_frequency)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 6)
                    .map(([key, value]) => (
                      <div className="metric-row" key={key}>
                        <span>{key}</span><b>{value}</b>
                      </div>
                    ))
                )}
              </div>
            )}

            <div className="card">
              <div className="section-title"><span>VERSION HISTORY</span></div>
              {versions.slice().reverse().slice(0, 5).map(v => (
                <div className="version" key={v.id}>
                  <div>
                    <b>v{v.id}</b>
                    <span>{v.decision}</span>
                  </div>
                  {v.id !== versions[versions.length - 1]?.id && (
                    <button onClick={() => rollback(v.id)}>Rollback</button>
                  )}
                </div>
              ))}
            </div>
          </aside>
        </section>

        {proposal && (
          <div className="modal-backdrop">
            <div className="modal">
              <div className="section-title">
                <span>AI LAYOUT PROPOSAL</span>
                <b>Validated</b>
              </div>
              <h2>Focus-oriented workspace</h2>
              <p>{proposal.rationale}</p>

              <div className="proposal-box">
                <div><b>Components</b><span>{proposal.layout.components.join(" • ")}</span></div>
                <div><b>Focus items</b><span>{proposal.layout.focusItems.join(" • ")}</span></div>
                <div><b>Custom HTML</b><span>Forbidden</span></div>
              </div>

              <h4>Evidence</h4>
              <ul>
                {proposal.evidence.length
                  ? proposal.evidence.map(x => <li key={x}>{x}</li>)
                  : <li>Using safe demo workflow defaults.</li>}
              </ul>

              <div className="modal-actions">
                <button onClick={() => decide("reject")}>Reject</button>
                <button className="primary" onClick={() => decide("accept")}>Accept & Render</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function FocusButton({ label, onClick }: { label: string; onClick: () => void }) {
  return <button className="focus-btn" onClick={onClick}>{label}</button>;
}
