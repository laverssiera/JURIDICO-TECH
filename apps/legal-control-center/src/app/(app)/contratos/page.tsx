"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  FileText, Plus, Search, Filter, Bot, Shield, GitBranch,
  Lock, CheckCircle, Clock, AlertTriangle, Eye, Download,
  PenLine, Zap, BarChart2, BookOpen, ExternalLink,
} from "lucide-react";
import { Badge, Card, KpiCard, RiskBadge, SectionHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

interface Contract {
  id: string;
  title: string;
  parties: string[];
  value: string;
  status: "draft" | "review_ai" | "review_human" | "signing" | "active" | "expired";
  risk: RiskLevel;
  riskScore: number;
  version: number;
  signed: boolean;
  expires: string;
  clauses: number;
  flags: string[];
}

const CONTRACTS: Contract[] = [
  { id: "CTR-0441", title: "Contrato Obra SP-330 — Ponte Infraestrutura",    parties: ["JT Engenharia","Prefeitura SP"],       value: "R$ 48,2M", status: "active",       risk: "vermelho", riskScore: 72, version: 3, signed: true,  expires: "2026-12-31", clauses: 42, flags: ["Embargo","Ambiental"] },
  { id: "CTR-0388", title: "Fornecimento Meridian Construtora — NR18",       parties: ["Meridian","JT Engenharia"],            value: "R$ 3,1M",  status: "review_ai",    risk: "amarelo",  riskScore: 55, version: 1, signed: false, expires: "2025-06-30", clauses: 28, flags: ["SST","NR18"] },
  { id: "CTR-0412", title: "SPE Parque Industrial — Contrato Social",        parties: ["SPE-44","Sócios Fundadores"],          value: "R$ 120M",  status: "signing",      risk: "verde",    riskScore: 91, version: 2, signed: false, expires: "2030-01-01", clauses: 67, flags: ["SPE","M&A"] },
  { id: "CTR-0297", title: "Licença Engepavi — Fornecedor Água",             parties: ["Engepavi","SABESP"],                   value: "R$ 800K",  status: "active",       risk: "amarelo",  riskScore: 63, version: 1, signed: true,  expires: "2025-07-31", clauses: 14, flags: ["ESG","Hídrico"] },
  { id: "CTR-0519", title: "Arbitragem CEA-2024 — Cláusula Compromissória",  parties: ["JT Eng","Construtora Alpha"],          value: "R$ 15M",   status: "review_human", risk: "vermelho", riskScore: 34, version: 4, signed: false, expires: "2025-09-15", clauses: 8,  flags: ["Câmara CCI","Urgente"] },
  { id: "CTR-0102", title: "Contrato Manutenção Torre Norte — SST",          parties: ["Torre Norte LTDA","JT Engenharia"],   value: "R$ 2,4M",  status: "active",       risk: "verde",    riskScore: 88, version: 1, signed: true,  expires: "2027-03-31", clauses: 22, flags: ["NR35","Vigente"] },
  { id: "CTR-0600", title: "Due Diligence Aquisição Terreno DF-10",         parties: ["JT Engenharia","Fundo Imob. AB"],     value: "R$ 55M",   status: "draft",        risk: "amarelo",  riskScore: 60, version: 1, signed: false, expires: "—",          clauses: 0,  flags: ["M&A","Rascunho"] },
];

const STATUS_CFG = {
  draft:        { label: "Rascunho",      color: "text-slate-400",   bg: "bg-slate-900/30 border-slate-700/30" },
  review_ai:    { label: "Revisão IA",    color: "text-blue-400",    bg: "bg-blue-900/20 border-blue-700/30" },
  review_human: { label: "Revisão Jur.",  color: "text-purple-400",  bg: "bg-purple-900/20 border-purple-700/30" },
  signing:      { label: "Assinatura",    color: "text-amber-400",   bg: "bg-amber-900/20 border-amber-700/30" },
  active:       { label: "Vigente",       color: "text-emerald-400", bg: "bg-emerald-900/20 border-emerald-700/30" },
  expired:      { label: "Encerrado",     color: "text-slate-600",   bg: "bg-slate-900/20 border-slate-700/20" },
};

const WORKFLOW = [
  { step: "Criação",      icon: PenLine,    desc: "Editor IA + templates" },
  { step: "Revisão IA",   icon: Bot,        desc: "Análise cláusulas e riscos" },
  { step: "Jurídico",     icon: FileText,   desc: "Revisão humana especializada" },
  { step: "Assinatura",   icon: Lock,       desc: "ICP-Brasil / DocuSign" },
  { step: "Ativação",     icon: Zap,        desc: "Runtime jurídico ativado" },
];

const CLAUSE_FLAGS = [
  { clause: "5.2 — Rescisão Unilateral",  risk: "vermelho" as RiskLevel, jurisp: "STJ REsp 1.234.567",      action: "Revisar prazo de 30→60 dias" },
  { clause: "8.1 — Penalidades SST",      risk: "amarelo"  as RiskLevel, jurisp: "TST RR-1001-24.2019",     action: "Alinhar com NR18 atualizada" },
  { clause: "12.4 — Foro de Eleição",     risk: "verde"    as RiskLevel, jurisp: "TJSP Ap. 0001234-SP",    action: "Aprovado" },
  { clause: "15.1 — Garantia de Obra",    risk: "amarelo"  as RiskLevel, jurisp: "STJ REsp 1.876.234",     action: "Exigir seguro-garantia" },
  { clause: "3.7 — Reajuste INCC",        risk: "verde"    as RiskLevel, jurisp: "TJSP 0009876",            action: "OK com cláusula espelho" },
];

export default function ContratosPage() {
  const [contracts, setContracts] = useState<Contract[]>(CONTRACTS);
  const [selected, setSelected] = useState<Contract | null>(CONTRACTS[0]);
  const [activeTab, setActiveTab] = useState<"editor" | "clausulas" | "historico" | "assinatura">("editor");

  useEffect(() => {
    let cancelled = false;

    type ContractListApi = {
      total: number;
      items: Array<{
        contract_id: string;
        title: string;
        contract_type: string;
        status: string;
        risk_score: number;
        created_at: string;
      }>;
    };

    const mapRisk = (score: number): RiskLevel => {
      if (score >= 80) return "verde";
      if (score >= 60) return "amarelo";
      if (score >= 40) return "vermelho";
      return "preto";
    };

    const loadContracts = async () => {
      try {
        const data = await api.get<ContractListApi>("/contracts/");
        if (cancelled || !data.items.length) return;

        const normalized: Contract[] = data.items.map((item) => ({
          id: item.contract_id,
          title: item.title,
          parties: ["Contratante", "Contratada"],
          value: "N/A",
          status: item.status === "active" ? "active" : item.status === "draft" ? "draft" : "review_ai",
          risk: mapRisk(item.risk_score),
          riskScore: Math.round(item.risk_score),
          version: 1,
          signed: item.status === "active",
          expires: "—",
          clauses: 0,
          flags: [item.contract_type],
        }));

        setContracts(normalized);
        setSelected(normalized[0]);
      } catch {
        // fallback: mantém dados mock locais
      }
    };

    loadContracts();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="p-6 h-full flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">MÓDULO CONTRATOS</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Legal OS · Editor Inteligente · ICP-Brasil</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-mono rounded-lg transition-colors">
          <Plus className="w-3.5 h-3.5" />
          Novo Contrato
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Contratos Vigentes"   value={612}  trend="up"     color="green" />
        <KpiCard label="Em Revisão IA"        value={24}   trend="stable" color="blue" />
        <KpiCard label="Aguardando Assin."    value={8}    trend="down"   color="amber" />
        <KpiCard label="Risco Alto"           value={17}   trend="up"     color="red" />
      </div>

      {/* Main layout */}
      <div className="flex-1 overflow-hidden grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Contract list */}
        <div className="xl:col-span-1 flex flex-col gap-3">
          <div className="flex gap-2">
            <div className="flex-1 flex items-center gap-2 glass rounded-lg border border-white/5 px-3 py-2">
              <Search className="w-3.5 h-3.5 text-slate-500" />
              <input
                placeholder="Buscar contratos..."
                className="flex-1 bg-transparent text-xs font-mono text-slate-300 placeholder-slate-600 outline-none"
              />
            </div>
            <button className="glass rounded-lg border border-white/5 px-2.5 py-2 text-slate-500 hover:text-slate-300 transition-colors">
              <Filter className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2 overflow-y-auto flex-1">
            {contracts.map(c => {
              const st = STATUS_CFG[c.status];
              return (
                <motion.button
                  key={c.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => setSelected(c)}
                  className={cn(
                    "w-full text-left p-3 glass rounded-xl border transition-all",
                    selected?.id === c.id ? "border-blue-500/40 bg-blue-900/10" : "border-white/5 hover:border-white/10"
                  )}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <span className="text-[11px] font-mono font-semibold text-slate-200 leading-tight line-clamp-2 text-left">
                      {c.title}
                    </span>
                    <RiskBadge level={c.risk} />
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[9px] font-mono text-slate-600">{c.id}</span>
                    <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded border", st.bg, st.color)}>
                      {st.label}
                    </span>
                    <span className="text-[9px] font-mono text-emerald-400">{c.value}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-[9px] font-mono text-slate-600">v{c.version} · {c.clauses} cláusulas</span>
                    {c.signed && <CheckCircle className="w-2.5 h-2.5 text-emerald-400" />}
                  </div>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Editor / Detail */}
        {selected && (
          <div className="xl:col-span-2 flex flex-col gap-4">
            <Card>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-mono font-bold text-white">{selected.id}</span>
                    <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded border",
                      STATUS_CFG[selected.status].bg, STATUS_CFG[selected.status].color
                    )}>
                      {STATUS_CFG[selected.status].label}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 font-semibold">{selected.title}</p>
                  <p className="text-xs text-slate-600 font-mono mt-0.5">{selected.parties.join(" · ")}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 glass rounded-lg border border-white/5 text-slate-500 hover:text-slate-300 transition-colors">
                    <Download className="w-3.5 h-3.5" />
                  </button>
                  <button className="p-2 glass rounded-lg border border-white/5 text-slate-500 hover:text-slate-300 transition-colors">
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Metrics row */}
              <div className="grid grid-cols-4 gap-3 mb-4">
                {[
                  { label: "Valor", val: selected.value, color: "text-emerald-400" },
                  { label: "Score IA", val: selected.riskScore, color: selected.riskScore >= 80 ? "text-emerald-400" : selected.riskScore >= 60 ? "text-amber-400" : "text-red-400" },
                  { label: "Cláusulas", val: selected.clauses, color: "text-blue-400" },
                  { label: "Versão", val: `v${selected.version}`, color: "text-slate-300" },
                ].map(({ label, val, color }) => (
                  <div key={label} className="glass rounded-lg p-3 border border-white/5 text-center">
                    <div className={cn("text-lg font-bold font-mono", color)}>{val}</div>
                    <div className="text-[9px] font-mono text-slate-600 mt-0.5">{label}</div>
                  </div>
                ))}
              </div>

              {/* Tabs */}
              <div className="flex gap-1 mb-4 border-b border-white/5 pb-2">
                {(["editor","clausulas","historico","assinatura"] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={cn(
                      "px-3 py-1.5 rounded text-[11px] font-mono transition-all",
                      activeTab === tab ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-300"
                    )}
                  >
                    {tab === "editor" ? "EDITOR" : tab === "clausulas" ? "CLÁUSULAS IA" : tab === "historico" ? "HISTÓRICO" : "ASSINATURA"}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              {activeTab === "editor" && (
                <div className="space-y-3">
                  {/* Workflow progress */}
                  <div className="flex items-center gap-1 overflow-x-auto">
                    {WORKFLOW.map((w, i) => {
                      const stepIdx = ["draft","review_ai","review_human","signing","active"].indexOf(selected.status);
                      const done = i <= stepIdx;
                      const current = i === stepIdx;
                      return (
                        <div key={w.step} className="flex items-center">
                          <div className={cn("flex flex-col items-center gap-1 px-2 py-1.5 rounded-lg transition-all", current ? "bg-blue-500/20 border border-blue-500/30" : done ? "bg-emerald-900/20" : "bg-white/2")}>
                            <w.icon className={cn("w-3.5 h-3.5", current ? "text-blue-400" : done ? "text-emerald-400" : "text-slate-600")} />
                            <span className={cn("text-[9px] font-mono", current ? "text-blue-400" : done ? "text-emerald-400" : "text-slate-600")}>{w.step}</span>
                          </div>
                          {i < WORKFLOW.length - 1 && (
                            <div className={cn("w-4 h-px mx-1", done ? "bg-emerald-700" : "bg-white/5")} />
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Mock editor */}
                  <div className="bg-[#0a0f1a] rounded-lg border border-white/5 p-4 font-mono text-xs text-slate-400 min-h-[160px] leading-relaxed">
                    <div className="text-slate-600 mb-2">{/* Contrato — {selected.id} v{selected.version} */}</div>
                    <p className="text-slate-300 mb-2"><span className="text-blue-400">CONTRATO</span> DE {selected.title.toUpperCase()}</p>
                    <p className="mb-2">As partes <span className="text-amber-400">{selected.parties[0]}</span> e <span className="text-amber-400">{selected.parties[1]}</span>, doravante denominadas CONTRATANTE e CONTRATADA...</p>
                    <p className="text-slate-600 italic">[ {selected.clauses} cláusulas carregadas — Editor IA ativo ]</p>
                    <div className="flex items-center gap-1.5 mt-3">
                      <Bot className="w-3 h-3 text-blue-400" />
                      <span className="text-blue-400 text-[10px]">John Legal analisando cláusulas...</span>
                      <div className="w-1 h-1 rounded-full bg-blue-400 animate-pulse" />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "clausulas" && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 mb-3">
                    <Bot className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-mono text-blue-400">Clause Intelligence — IA Forense</span>
                  </div>
                  {CLAUSE_FLAGS.map((cf, i) => (
                    <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.07 }}
                      className="flex items-start gap-3 p-3 glass rounded-lg border border-white/5">
                      <RiskBadge level={cf.risk} />
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-mono font-semibold text-slate-200">{cf.clause}</p>
                        <p className="text-[10px] font-mono text-blue-400 mt-0.5">{cf.jurisp}</p>
                        <p className="text-[10px] font-mono text-slate-500 mt-0.5">{cf.action}</p>
                      </div>
                      <BookOpen className="w-3.5 h-3.5 text-slate-600 shrink-0 mt-0.5" />
                    </motion.div>
                  ))}
                </div>
              )}

              {activeTab === "assinatura" && (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 glass rounded-xl border border-emerald-500/20 bg-emerald-900/10">
                    <Lock className="w-5 h-5 text-emerald-400" />
                    <div>
                      <p className="text-sm font-mono font-semibold text-emerald-400">ICP-Brasil + DocuSign</p>
                      <p className="text-xs font-mono text-slate-500">Trilha auditável blockchain · Hash imutável</p>
                    </div>
                  </div>
                  {selected.parties.map((p, i) => (
                    <div key={p} className="flex items-center justify-between p-3 glass rounded-lg border border-white/5">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-xs font-mono font-bold text-blue-400">
                          {p[0]}
                        </div>
                        <span className="text-xs font-mono text-slate-300">{p}</span>
                      </div>
                      <div className={cn("flex items-center gap-1.5 text-xs font-mono", selected.signed && i === 0 ? "text-emerald-400" : "text-slate-600")}>
                        {selected.signed && i === 0 ? <><CheckCircle className="w-3.5 h-3.5" /> Assinado</> : <><Clock className="w-3.5 h-3.5" /> Pendente</>}
                      </div>
                    </div>
                  ))}
                  <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-mono rounded-lg transition-colors flex items-center justify-center gap-2">
                    <Lock className="w-3.5 h-3.5" />
                    Solicitar Assinatura ICP-Brasil
                  </button>
                </div>
              )}

              {activeTab === "historico" && (
                <div className="space-y-2">
                  {[
                    { ver: `v${selected.version}`, user: "Dr. Alencar", action: "Edição cláusula 5.2", ts: "Hoje, 09:14" },
                    { ver: `v${selected.version - 1 > 0 ? selected.version - 1 : 1}`, user: "John Legal IA", action: "Análise automática concluída", ts: "Ontem, 18:30" },
                    { ver: "v1", user: "Dra. Lima", action: "Criação do contrato", ts: "12/04/2025" },
                  ].map((h, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 glass rounded-lg border border-white/5">
                      <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-[9px] font-mono font-bold text-blue-400">{h.ver}</div>
                      <div className="flex-1">
                        <p className="text-[11px] font-mono text-slate-200">{h.action}</p>
                        <p className="text-[9px] font-mono text-slate-600">{h.user} · {h.ts}</p>
                      </div>
                      <GitBranch className="w-3.5 h-3.5 text-slate-600" />
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
