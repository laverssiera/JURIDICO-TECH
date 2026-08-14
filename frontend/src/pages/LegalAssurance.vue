<template>
  <main class="assurance-shell">
    <section class="intro">
      <p class="eyebrow">LEGAL ASSURANCE / LICEU 6</p>
      <h1>Contrato sob controle.</h1>
      <p class="lede">Gere uma minuta e teste, no mesmo movimento, compliance, responsabilidade e cobertura securitária.</p>
    </section>

    <section class="workspace">
      <form class="panel form-panel" @submit.prevent="runAssessment">
        <div class="panel-heading">
          <div>
            <p class="kicker">Nova análise</p>
            <h2>Contexto contratual</h2>
          </div>
          <span class="step">01 / 02</span>
        </div>

        <div class="field-grid">
          <label>
            Tipo de contrato
            <select v-model="form.contract_type">
              <option>MSA</option>
              <option>SOW</option>
              <option>NDA</option>
              <option>EPC</option>
              <option>PPP</option>
              <option>BOT</option>
            </select>
          </label>
          <label>
            Jurisdição
            <input v-model="form.jurisdiction" maxlength="12" />
          </label>
        </div>

        <label>
          Partes
          <input v-model="form.parties" placeholder="ACME, fornecedor principal" />
        </label>
        <label>
          Objetivo
          <input v-model="form.objective" placeholder="Operação de serviços tecnológicos" required />
        </label>

        <div class="section-rule"><span>Controles essenciais</span></div>
        <div class="control-grid">
          <label v-for="control in controlOptions" :key="control.key" class="toggle">
            <input v-model="form.controls[control.key]" type="checkbox" />
            <span class="toggle-mark"></span>
            <span>{{ control.label }}</span>
          </label>
        </div>

        <div class="field-grid">
          <label>
            Responsabilidade
            <select v-model="form.liability">
              <option value="false">Não definida</option>
              <option value="medium">Requer delimitação</option>
              <option value="high">Alta exposição</option>
            </select>
          </label>
          <label>
            Seguro
            <select v-model="form.insurance">
              <option value="false">Não confirmado</option>
              <option value="true">Cobertura confirmada</option>
              <option value="high">Cobertura insuficiente</option>
            </select>
          </label>
        </div>

        <button class="primary-button" :disabled="loading" type="submit">
          <span>{{ loading ? 'Processando análise...' : 'Gerar e analisar' }}</span>
          <span aria-hidden="true">↗</span>
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <section class="panel result-panel" aria-live="polite">
        <div class="panel-heading">
          <div>
            <p class="kicker">Resultado integrado</p>
            <h2>{{ result ? 'Parecer preliminar' : 'Aguardando dados' }}</h2>
          </div>
          <span v-if="result" class="status" :class="result.decision">{{ decisionLabel }}</span>
        </div>

        <template v-if="result">
          <div class="risk-line">
            <span>Índice de risco</span>
            <strong :class="`risk-${result.risk_level}`">{{ result.risk_level.toUpperCase() }}</strong>
          </div>
          <div class="metric-row">
            <div><small>Contrato</small><strong>{{ result.contract.contract_id }}</strong></div>
            <div><small>Compliance</small><strong>{{ result.compliance.compliance.score }} / 100</strong></div>
            <div><small>Cláusulas</small><strong>{{ result.contract.mandatory_clauses.length }}</strong></div>
          </div>
          <div class="result-block">
            <p class="kicker">Cláusulas obrigatórias</p>
            <div class="chips"><span v-for="clause in result.contract.mandatory_clauses" :key="clause">{{ clause.replaceAll('_', ' ') }}</span></div>
          </div>
          <div class="result-block actions">
            <p class="kicker">Próximas ações</p>
            <ol><li v-for="action in result.required_actions" :key="action">{{ action }}</li></ol>
          </div>
        </template>
        <div v-else class="empty-state">
          <span class="empty-mark">◎</span>
          <p>A análise vai combinar a minuta, os controles e a exposição jurídica neste painel.</p>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)
const form = reactive({
  contract_type: 'MSA',
  jurisdiction: 'BR',
  parties: 'ACME, fornecedor principal',
  objective: 'Operação de serviços tecnológicos',
  liability: 'medium',
  insurance: 'false',
  controls: { audit_trail: true, data_protection: true, dispute_clause: false },
})
const controlOptions = [
  { key: 'audit_trail', label: 'Trilha de auditoria' },
  { key: 'data_protection', label: 'Proteção de dados' },
  { key: 'dispute_clause', label: 'Cláusula de disputa' },
]
const decisionLabel = computed(() => ({ approved: 'Aprovado', pending: 'Revisão', blocked: 'Bloqueado' }[result.value?.decision] || 'Revisão'))

async function runAssessment() {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(`${apiUrl}/legal/assurance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...form,
        parties: form.parties.split(',').map((party) => party.trim()).filter(Boolean),
        obligations: ['audit_trail', 'data_protection', 'dispute_clause'],
        frameworks: ['LGPD'],
        liability: form.liability === 'false' ? false : form.liability,
        insurance: form.insurance === 'false' ? false : form.insurance,
      }),
    })
    if (!response.ok) throw new Error('Não foi possível concluir a análise.')
    result.value = await response.json()
  } catch (requestError) {
    error.value = requestError instanceof Error ? requestError.message : 'Falha de comunicação com o runtime.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(body) { margin: 0; background: #f3f0e9; color: #182421; font-family: Georgia, 'Times New Roman', serif; }
.assurance-shell { min-height: 100vh; padding: clamp(2rem, 6vw, 5.5rem) clamp(1.2rem, 6vw, 7rem); background: radial-gradient(circle at 82% 8%, #e3d8c7 0, transparent 29rem), linear-gradient(135deg, #f8f5ef 0%, #eee9df 100%); }
.intro { max-width: 760px; margin-bottom: 3rem; }
.eyebrow, .kicker { margin: 0 0 .8rem; color: #a24d31; font: 700 .72rem/1.2 Arial, sans-serif; letter-spacing: .14em; text-transform: uppercase; }
h1 { max-width: 620px; margin: 0; font-size: clamp(3rem, 7vw, 6.6rem); line-height: .92; font-weight: 400; letter-spacing: 0; }
.lede { max-width: 520px; margin: 1.3rem 0 0; color: #53615d; font: 1.08rem/1.5 Arial, sans-serif; }
.workspace { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr); gap: 1.2rem; max-width: 1180px; }
.panel { border: 1px solid #d5cec1; background: rgba(255, 253, 248, .78); padding: clamp(1.3rem, 3vw, 2.2rem); box-shadow: 0 18px 50px rgba(74, 62, 44, .08); }
.panel-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; border-bottom: 1px solid #d8d0c3; padding-bottom: 1.2rem; margin-bottom: 1.5rem; }
h2 { margin: 0; font-size: 1.75rem; font-weight: 400; }
.step { color: #8a9690; font: .75rem Arial, sans-serif; }
label { display: flex; flex-direction: column; gap: .45rem; margin-bottom: 1rem; color: #53615d; font: .78rem Arial, sans-serif; text-transform: uppercase; letter-spacing: .06em; }
input, select { width: 100%; border: 1px solid #cfc7b9; border-radius: 0; background: #fffdf9; color: #182421; padding: .82rem .9rem; font: 1rem Georgia, serif; text-transform: none; letter-spacing: 0; }
input:focus, select:focus { outline: 2px solid #d47b54; outline-offset: 2px; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.section-rule { display: flex; align-items: center; gap: .8rem; margin: 1.6rem 0 1rem; color: #8a9690; font: .7rem Arial, sans-serif; text-transform: uppercase; letter-spacing: .1em; }
.section-rule::after { content: ''; height: 1px; flex: 1; background: #d8d0c3; }
.control-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; margin-bottom: 1.5rem; }
.toggle { flex-direction: row; align-items: center; gap: .55rem; margin: 0; color: #33423d; font-size: .82rem; text-transform: none; letter-spacing: 0; cursor: pointer; }
.toggle input { position: absolute; opacity: 0; width: 1px; }
.toggle-mark { width: 1.1rem; height: 1.1rem; border: 1px solid #9faaa3; background: #fffdf9; }
.toggle input:checked + .toggle-mark { border-color: #a24d31; background: #a24d31; box-shadow: inset 0 0 0 3px #fffdf9; }
.primary-button { display: flex; justify-content: space-between; width: 100%; margin-top: .5rem; border: 0; background: #182421; color: #fffdf9; padding: 1rem 1.1rem; cursor: pointer; font: 700 .8rem Arial, sans-serif; text-transform: uppercase; letter-spacing: .08em; }
.primary-button:disabled { cursor: wait; opacity: .6; }
.error { color: #a24d31; font: .85rem Arial, sans-serif; }
.status { padding: .35rem .55rem; font: 700 .68rem Arial, sans-serif; text-transform: uppercase; letter-spacing: .08em; }
.status.approved { color: #2c684c; background: #dceade; }.status.pending { color: #91622e; background: #f2e3c8; }.status.blocked { color: #9c3d32; background: #f3d8d1; }
.risk-line, .metric-row { display: flex; justify-content: space-between; gap: 1rem; border-bottom: 1px solid #d8d0c3; padding: 1rem 0; font: .85rem Arial, sans-serif; }
.risk-line strong { font-size: .75rem; letter-spacing: .1em; }.risk-low { color: #2c684c; }.risk-medium, .risk-high { color: #a46631; }.risk-critical { color: #9c3d32; }
.metric-row { justify-content: flex-start; gap: 2rem; }.metric-row div { display: flex; flex-direction: column; gap: .35rem; }.metric-row small { color: #8a9690; text-transform: uppercase; font-size: .65rem; letter-spacing: .08em; }.metric-row strong { font-size: .9rem; font-weight: 400; }
.result-block { margin-top: 1.7rem; }.chips { display: flex; flex-wrap: wrap; gap: .4rem; }.chips span { padding: .4rem .55rem; background: #e7dfd2; color: #4c5b55; font: .75rem Arial, sans-serif; text-transform: capitalize; }
.actions ol { margin: 0; padding-left: 1.2rem; color: #53615d; font: .9rem/1.55 Arial, sans-serif; }.actions li { padding: .25rem 0; }
.empty-state { display: grid; place-items: center; min-height: 320px; padding: 2rem; text-align: center; color: #8a9690; }.empty-state p { max-width: 260px; font: 1rem/1.5 Georgia, serif; }.empty-mark { color: #a24d31; font-size: 3rem; }
@media (max-width: 800px) { .workspace { grid-template-columns: 1fr; }.intro { margin-bottom: 2rem; }.metric-row { gap: 1rem; }.metric-row strong { font-size: .78rem; } }
@media (max-width: 480px) { .field-grid, .control-grid { grid-template-columns: 1fr; } h1 { font-size: 3.6rem; } }
</style>
