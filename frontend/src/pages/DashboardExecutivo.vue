<template>
  <main class="exec-shell">
    <section class="hero">
      <div>
        <p class="eyebrow">LICEU Mission Control</p>
        <h1>Dashboard Executivo Jurídico</h1>
        <p class="subtitle">
          Runtime regulatório vivo para risco sistêmico, governança e resposta crítica.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn primary" @click="refreshAll">Atualizar Painel</button>
        <button class="btn" @click="runSupplierSimulation">Simular Quebra de Fornecedor</button>
      </div>
    </section>

    <section class="grid-kpis">
      <article class="kpi-card">
        <h3>Digital Twins</h3>
        <p class="kpi">{{ kpis.twinsTotal }}</p>
        <small>{{ kpis.twinsCritical }} críticos</small>
      </article>

      <article class="kpi-card">
        <h3>Radar Regulatório</h3>
        <p class="kpi">{{ kpis.signalsTotal }}</p>
        <small>{{ kpis.signalsHigh }} sinais high/critical</small>
      </article>

      <article class="kpi-card">
        <h3>War Room</h3>
        <p class="kpi">{{ kpis.incidentsOpen }}</p>
        <small>{{ kpis.incidentsCritical }} incidentes críticos</small>
      </article>

      <article class="kpi-card">
        <h3>Legal OS</h3>
        <p class="kpi">{{ kpis.decisionsBlocked }}</p>
        <small>operações bloqueadas</small>
      </article>

      <article class="kpi-card accent">
        <h3>Simulações Globais</h3>
        <p class="kpi">{{ kpis.simulationsTotal }}</p>
        <small>{{ kpis.simulationsHigh }} risco alto/crítico</small>
      </article>

      <article class="kpi-card accent">
        <h3>Trust Médio</h3>
        <p class="kpi">{{ trustPreview.trust_score }}</p>
        <small>{{ trustPreview.trust_tier }}</small>
      </article>
    </section>

    <section class="board">
      <article class="panel">
        <h2>Eventos em Tempo Real</h2>
        <p class="panel-sub">WebSocket /events/ws</p>
        <ul class="events">
          <li v-for="item in liveEvents" :key="item.id">
            <span class="tag">{{ item.type }}</span>
            <span>{{ item.summary }}</span>
            <time>{{ item.time }}</time>
          </li>
        </ul>
      </article>

      <article class="panel">
        <h2>Última Simulação Jurídica</h2>
        <p class="panel-sub">Global Legal Simulation</p>
        <div v-if="lastSimulation">
          <p><strong>ID:</strong> {{ lastSimulation.scenario_id }}</p>
          <p><strong>Tipo:</strong> {{ lastSimulation.scenario_type }}</p>
          <p><strong>Risco:</strong> {{ lastSimulation.risk_level }} ({{ lastSimulation.legal_risk_score }})</p>
          <ul>
            <li v-for="action in lastSimulation.recommended_actions" :key="action">{{ action }}</li>
          </ul>
        </div>
        <p v-else>Nenhuma simulação executada ainda.</p>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

type RiskPayload = {
  legal_exposure?: number
  severity?: string
}

const twins = ref<any[]>([])
const signals = ref<any[]>([])
const incidents = ref<any[]>([])
const decisions = ref<any[]>([])
const simulations = ref<any[]>([])
const trustPreview = reactive({ trust_score: 0, trust_tier: 'N/A' })
const lastSimulation = ref<any | null>(null)
const liveEvents = ref<Array<{ id: string; type: string; summary: string; time: string }>>([])

let ws: WebSocket | null = null
let pingTimer: number | null = null

const kpis = computed(() => ({
  twinsTotal: twins.value.length,
  twinsCritical: twins.value.filter((t) => (t.legal_exposure || 0) >= 80).length,
  signalsTotal: signals.value.length,
  signalsHigh: signals.value.filter((s) => ['high', 'critical'].includes(String(s.severity || '').toLowerCase())).length,
  incidentsOpen: incidents.value.length,
  incidentsCritical: incidents.value.filter((i) => String(i.severity || '').toLowerCase() === 'critical').length,
  decisionsBlocked: decisions.value.filter((d) => d.allow === false).length,
  simulationsTotal: simulations.value.length,
  simulationsHigh: simulations.value.filter((s) => ['HIGH', 'CRITICAL'].includes(s.risk_level)).length,
}))

function nowLabel(): string {
  return new Date().toLocaleTimeString('pt-BR', { hour12: false })
}

function pushEvent(type: string, payload: Record<string, unknown>): void {
  const summary = JSON.stringify(payload).slice(0, 120)
  liveEvents.value.unshift({
    id: `${type}-${Date.now()}-${Math.random()}`,
    type,
    summary,
    time: nowLabel(),
  })
  liveEvents.value = liveEvents.value.slice(0, 30)
}

async function getJson(path: string): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`Falha em ${path}`)
  return await res.json()
}

async function postJson(path: string, body: Record<string, unknown>): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`Falha em ${path}`)
  return await res.json()
}

async function refreshAll(): Promise<void> {
  const [tw, sg, ic, dc, sm] = await Promise.all([
    getJson('/liceu/twin/'),
    getJson('/liceu/radar-global/signals'),
    getJson('/liceu/war-room/incidents?status=open'),
    getJson('/liceu/legal-os/decisions'),
    getJson('/liceu/simulacao-global/'),
  ])

  twins.value = tw.twins || []
  signals.value = sg.signals || []
  incidents.value = ic.incidents || []
  decisions.value = dc.decisions || []
  simulations.value = sm.scenarios || []

  if (simulations.value.length > 0) {
    lastSimulation.value = simulations.value[0]
  }

  const trust = await postJson('/liceu/trust/score', {
    entity_id: 'EXEC-DASHBOARD',
    entity_type: 'ecossistema',
    metrics: {
      compliance: 84,
      historico: 82,
      litigios: 70,
      performance: 88,
      esg: 86,
      financeiro: 81,
      comportamento: 79,
      reputacao: 90,
    },
  })
  trustPreview.trust_score = trust.trust_score
  trustPreview.trust_tier = trust.trust_tier
}

async function runSupplierSimulation(): Promise<void> {
  const sim = await postJson('/liceu/simulacao-global/supplier-failure', {
    supplier_id: 'SUP-22',
    affected_works: 4,
    affected_contracts: 3,
    financial_exposure: 8000000,
    contingency_ready: false,
  })
  lastSimulation.value = sim
  await refreshAll()
}

function connectLiveStream(): void {
  const wsUrl = API_BASE.replace(/^http/, 'ws') + '/events/ws'
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    pingTimer = window.setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 15000)
  }

  ws.onmessage = (message: MessageEvent<string>) => {
    try {
      const parsed = JSON.parse(message.data)
      pushEvent(parsed.type || 'event', parsed.payload || {})
    } catch {
      pushEvent('raw', { data: message.data })
    }
  }

  ws.onerror = () => pushEvent('stream.error', { message: 'Falha no websocket' })
  ws.onclose = () => pushEvent('stream.closed', { message: 'Conexão encerrada' })
}

onMounted(async () => {
  try {
    await refreshAll()
    connectLiveStream()
  } catch (err) {
    pushEvent('dashboard.error', { message: String(err) })
  }
})

onBeforeUnmount(() => {
  if (pingTimer) window.clearInterval(pingTimer)
  if (ws) ws.close()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

.exec-shell {
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at 15% 15%, rgba(8, 93, 81, 0.18), transparent 40%),
    radial-gradient(circle at 85% 10%, rgba(217, 95, 2, 0.18), transparent 45%),
    linear-gradient(120deg, #f5f7f2 0%, #e9f0eb 55%, #f7efe6 100%);
  color: #12322f;
  font-family: 'Space Grotesk', sans-serif;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  color: #0b5e53;
}

h1 {
  margin: 0.2rem 0;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
}

.subtitle {
  margin: 0;
  max-width: 65ch;
  color: #3b5c57;
}

.hero-actions {
  display: flex;
  gap: 0.7rem;
}

.btn {
  border: 1px solid #0f6b5f;
  color: #0f6b5f;
  background: #ffffffd9;
  padding: 0.66rem 0.9rem;
  border-radius: 0.6rem;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  background: #0f6b5f;
  color: #fff;
}

.grid-kpis {
  display: grid;
  grid-template-columns: repeat(6, minmax(130px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.2rem;
}

.kpi-card {
  background: #ffffffde;
  border: 1px solid #d3e0dd;
  border-radius: 0.9rem;
  padding: 0.9rem;
  animation: rise 0.55s ease both;
}

.kpi-card.accent {
  border-color: #e2c5aa;
  background: #fff4ea;
}

.kpi-card h3 {
  margin: 0;
  font-size: 0.88rem;
  color: #2f5550;
}

.kpi {
  margin: 0.2rem 0;
  font-size: 1.7rem;
  font-weight: 700;
}

.board {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 1rem;
}

.panel {
  background: #ffffffde;
  border: 1px solid #d7e2df;
  border-radius: 1rem;
  padding: 1rem;
}

.panel h2 {
  margin: 0;
  font-size: 1.05rem;
}

.panel-sub {
  margin: 0.25rem 0 0.8rem;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.76rem;
  color: #4e706b;
}

.events {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
  max-height: 420px;
  overflow: auto;
}

.events li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.6rem;
  align-items: center;
  border: 1px solid #e4ecea;
  border-radius: 0.65rem;
  padding: 0.42rem 0.5rem;
  font-size: 0.82rem;
}

.tag {
  font-family: 'IBM Plex Mono', monospace;
  color: #0f6b5f;
  background: #e2f0ed;
  border-radius: 0.45rem;
  padding: 0.16rem 0.3rem;
}

time {
  color: #557670;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .grid-kpis {
    grid-template-columns: repeat(3, minmax(120px, 1fr));
  }

  .board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .exec-shell {
    padding: 1rem;
  }

  .hero {
    flex-direction: column;
    align-items: start;
  }

  .grid-kpis {
    grid-template-columns: repeat(2, minmax(110px, 1fr));
  }
}
</style>
