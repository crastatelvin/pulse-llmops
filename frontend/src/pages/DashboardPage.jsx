import { useCallback, useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { getAlerts, getCalls, getModels, getSummary, getTimeseries, runSupportDemo } from "../services/api";

const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws";

function Kpi({ label, value }) {
  return (
    <div className="card">
      <div style={{ color: "var(--muted)", fontSize: 11 }}>{label}</div>
      <div style={{ fontSize: 22, color: "var(--teal)", marginTop: 6 }}>{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState({});
  const [timeseries, setTimeseries] = useState([]);
  const [calls, setCalls] = useState([]);
  const [models, setModels] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [wsUp, setWsUp] = useState(false);
  const [runningDemo, setRunningDemo] = useState(false);
  const [demoMessage, setDemoMessage] = useState("");

  const loadAll = useCallback(async () => {
    const [s, t, c, m, a] = await Promise.all([getSummary(), getTimeseries(), getCalls(), getModels(), getAlerts()]);
    setSummary(s);
    setTimeseries(t);
    setCalls(c);
    setModels(m);
    setAlerts(a);
  }, []);

  useEffect(() => {
    loadAll();
    const poll = setInterval(loadAll, 12000);
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setWsUp(true);
    ws.onclose = () => setWsUp(false);
    ws.onmessage = () => loadAll();
    return () => {
      clearInterval(poll);
      ws.close();
    };
  }, [loadAll]);

  const handleRunDemo = async () => {
    if (runningDemo) return;
    setRunningDemo(true);
    setDemoMessage("Running demo support tickets...");
    try {
      const result = await runSupportDemo();
      const okCount = (result.results || []).filter((r) => r.success).length;
      setDemoMessage(`Demo completed: ${okCount}/${result.count} calls succeeded (${result.session_id}).`);
      await loadAll();
    } catch (err) {
      setDemoMessage(`Demo failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setRunningDemo(false);
    }
  };

  return (
    <div className="wrap">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <h1 style={{ margin: 0 }}>PULSE LLMOps</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            onClick={handleRunDemo}
            disabled={runningDemo}
            style={{
              background: runningDemo ? "rgba(0,212,170,0.15)" : "var(--teal)",
              color: runningDemo ? "var(--teal)" : "#031010",
              border: "none",
              borderRadius: 6,
              padding: "8px 12px",
              fontWeight: 700,
              cursor: runningDemo ? "not-allowed" : "pointer"
            }}
          >
            {runningDemo ? "Running Demo..." : "Run Demo Tickets"}
          </button>
          <div style={{ fontSize: 12, color: wsUp ? "var(--teal)" : "var(--red)" }}>{wsUp ? "LIVE" : "OFFLINE"}</div>
        </div>
      </div>
      {demoMessage ? (
        <div className="card" style={{ marginBottom: 10, fontSize: 12, color: "var(--text)" }}>
          {demoMessage}
        </div>
      ) : null}

      <div className="kpi-grid">
        <Kpi label="Total Calls" value={summary.total_calls || 0} />
        <Kpi label="Error Rate %" value={summary.error_rate_pct || 0} />
        <Kpi label="Avg Latency ms" value={summary.avg_latency_ms || 0} />
        <Kpi label="Total Cost USD" value={summary.total_cost_usd || 0} />
      </div>

      <div className="two-grid">
        <div className="card" style={{ height: 260 }}>
          <div style={{ marginBottom: 8 }}>Latency Trend</div>
          <ResponsiveContainer width="100%" height={210}>
            <LineChart data={timeseries}>
              <XAxis dataKey="time_bucket" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line dataKey="avg_latency" stroke="#00d4aa" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card" style={{ height: 260 }}>
          <div style={{ marginBottom: 8 }}>Token Trend</div>
          <ResponsiveContainer width="100%" height={210}>
            <LineChart data={timeseries}>
              <XAxis dataKey="time_bucket" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line dataKey="tokens" stroke="#6da8ff" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="two-grid">
        <div className="card">
          <div style={{ marginBottom: 8 }}>Recent Calls</div>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Model</th>
                <th>Latency</th>
                <th>Tokens</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {calls.slice(0, 10).map((call) => (
                <tr key={call.id}>
                  <td>#{call.id}</td>
                  <td>{call.model}</td>
                  <td>{Math.round(call.latency_ms || 0)}ms</td>
                  <td>{call.total_tokens || 0}</td>
                  <td style={{ color: call.success ? "var(--teal)" : "var(--red)" }}>{call.success ? "OK" : "ERR"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card">
          <div style={{ marginBottom: 8 }}>Alerts / Model Breakdown</div>
          <div style={{ marginBottom: 12 }}>
            {alerts.length === 0 ? (
              <div style={{ color: "var(--teal)", fontSize: 12 }}>No active alerts</div>
            ) : (
              alerts.slice(0, 5).map((a) => (
                <div key={a.id} style={{ marginBottom: 6, fontSize: 12 }}>
                  <strong>{a.type}</strong> - {a.message}
                </div>
              ))
            )}
          </div>
          {models.map((m) => (
            <div key={m.model} style={{ marginBottom: 8, fontSize: 12 }}>
              {m.model}: {m.calls} calls, avg latency {Math.round(m.avg_latency || 0)}ms
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
