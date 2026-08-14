import React, { useEffect, useMemo, useState } from "react";

const WS_URL = "ws://localhost:8000/events/ws";

function decisionByRisk(level) {
  if (level === "high") {
    return "BLOCK";
  }
  if (level === "medium") {
    return "REVIEW";
  }
  return "AUTO_APPROVE";
}

export default function LegalTradingDesk() {
  const [contracts, setContracts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [riskMap, setRiskMap] = useState({});
  const [selected, setSelected] = useState(null);
  const [connection, setConnection] = useState("connecting");

  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket(WS_URL);
      setConnection("connecting");

      ws.onopen = () => setConnection("online");
      ws.onclose = () => {
        setConnection("offline");
        reconnectTimer = setTimeout(connect, 1500);
      };
      ws.onerror = () => setConnection("offline");

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "legal.contract.created") {
          setContracts((prev) => [data.payload, ...prev].slice(0, 80));
        }

        if (data.type === "legal.risk.flagged") {
          setAlerts((prev) => [data.payload, ...prev].slice(0, 80));
        }

        if (data.type === "legal.risk.update") {
          setRiskMap((prev) => ({
            ...prev,
            [data.payload.deal_id]: data.payload,
          }));
        }
      };
    };

    connect();
    return () => {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const riskRows = useMemo(() => Object.values(riskMap), [riskMap]);

  return (
    <div className="desk">
      <header className="desk-header">
        <div>
          <h1>JuridicoTech Trading Desk</h1>
          <p>Mesa juridica em tempo real para operacao e risco do ecossistema.</p>
        </div>
        <div className={`status-chip ${connection}`}>{connection.toUpperCase()}</div>
      </header>

      <section className="metrics-row">
        <div className="metric-card">
          <span>Contratos</span>
          <strong>{contracts.length}</strong>
        </div>
        <div className="metric-card">
          <span>Alertas Criticos</span>
          <strong>{alerts.length}</strong>
        </div>
        <div className="metric-card">
          <span>Deals no Radar</span>
          <strong>{riskRows.length}</strong>
        </div>
      </section>

      <main className="grid">
        <section className="panel contracts-panel">
          <h2>Contratos em Tempo Real</h2>
          {contracts.length === 0 && <p className="empty">Aguardando eventos de contrato...</p>}
          {contracts.map((c, i) => (
            <button key={`${c.id}-${i}`} className="card" onClick={() => setSelected(c)}>
              <div className="card-title">{c.type || "intermediation"}</div>
              <div className="card-sub">Deal: {c.deal_id || "n/a"}</div>
              <div className="badge">Status: {c.status || "draft"}</div>
            </button>
          ))}
        </section>

        <section className="panel alerts-panel">
          <h2>Alertas Juridicos</h2>
          {alerts.length === 0 && <p className="empty">Sem alertas no momento.</p>}
          {alerts.map((a, i) => (
            <article key={`alert-${i}`} className="alert">
              <div className="alert-title">Risco Elevado</div>
              <div>{a.message}</div>
              <div className="alert-meta">Deal: {a.deal_id || "n/a"}</div>
            </article>
          ))}
        </section>

        <section className="panel risk-panel">
          <h2>Risk Engine</h2>
          {riskRows.length === 0 && <p className="empty">Sem deals monitorados.</p>}
          {riskRows.map((r) => (
            <article key={r.deal_id} className={`risk ${r.risk_level}`}>
              <div className="risk-head">
                <span>Deal {r.deal_id}</span>
                <span className="decision">{decisionByRisk(r.risk_level)}</span>
              </div>
              <div className="risk-body">
                <div>Risco: {r.risk_level}</div>
                <div>Score: {r.score}</div>
              </div>
            </article>
          ))}
        </section>
      </main>

      {selected && (
        <aside className="modal-backdrop" onClick={() => setSelected(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Contrato Selecionado</h3>
            <pre>{JSON.stringify(selected, null, 2)}</pre>
            <button className="close-btn" onClick={() => setSelected(null)}>
              Fechar
            </button>
          </div>
        </aside>
      )}
    </div>
  );
}
