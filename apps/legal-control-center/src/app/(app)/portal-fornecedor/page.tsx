"use client";
import { motion } from "framer-motion";
import {
  Building2, Shield, Award, CheckCircle, AlertTriangle,
  FileText, Clock, TrendingUp, HardHat, Star, Upload,
} from "lucide-react";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

const SUPPLIERS = [
  { id: "FORN-001", name: "Steel Industries Brasil", score: 9.1, compliance: "OK", trabalhista: "baixo", esg: "alto",  risk: "verde"    as RiskLevel, homologado: true  },
  { id: "FORN-088", name: "Meridian Construtora",    score: 8.9, compliance: "OK", trabalhista: "baixo", esg: "médio", risk: "amarelo"  as RiskLevel, homologado: true  },
  { id: "FORN-012", name: "Engepavi Ltda",           score: 7.2, compliance: "ALERTA", trabalhista: "médio", esg: "baixo", risk: "amarelo" as RiskLevel, homologado: true  },
  { id: "FORN-042", name: "Alpha Cimento",           score: 6.5, compliance: "ALERTA", trabalhista: "alto", esg: "baixo", risk: "vermelho" as RiskLevel, homologado: false },
];

const CHECKLIST = [
  { item: "CNPJ válido e ativo",            ok: true },
  { item: "Certidão Negativa Débitos",      ok: true },
  { item: "FGTS em dia",                    ok: true },
  { item: "Certidão Trabalhista",           ok: true },
  { item: "Alvará de Funcionamento",        ok: true },
  { item: "Seguro Garantia",                ok: false },
  { item: "Certificado ISO 9001",           ok: false },
  { item: "Treinamento NR18 concluído",     ok: true },
];

const TRAININGS = [
  { nome: "NR18 — Segurança em Obras",   concluido: 87, total: 100 },
  { nome: "NR35 — Trabalho em Altura",   concluido: 64, total: 80 },
  { nome: "LGPD — Proteção de Dados",    concluido: 45, total: 60 },
  { nome: "Código de Conduta",           concluido: 100, total: 100 },
];

export default function PortalFornecedorPage() {
  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">PORTAL FORNECEDORES</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Homologação · Compliance · Score · Treinamentos</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-mono rounded-lg transition-colors">
          <Upload className="w-3.5 h-3.5" />
          Novos Documentos
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Fornecedores Ativos"   value={89}    trend="up"     color="blue" />
        <KpiCard label="Score Médio"           value="8.2"   trend="up"     color="green" />
        <KpiCard label="Em Análise"            value={12}    trend="stable" color="amber" />
        <KpiCard label="Bloqueados"            value={4}     trend="down"   color="red" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Supplier scorecards */}
        <div className="xl:col-span-2 space-y-3">
          <h2 className="text-sm font-mono font-semibold text-white flex items-center gap-2">
            <Star className="w-4 h-4 text-amber-400" />
            SCORE FORNECEDORES
          </h2>
          {SUPPLIERS.map((s, i) => (
            <motion.div key={s.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <Card>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[10px] font-mono text-slate-500">{s.id}</span>
                      {s.homologado
                        ? <Badge variant="green"><CheckCircle className="w-2.5 h-2.5 mr-1 inline" />Homologado</Badge>
                        : <Badge variant="red"><AlertTriangle className="w-2.5 h-2.5 mr-1 inline" />Pendente</Badge>
                      }
                    </div>
                    <p className="text-sm font-semibold text-slate-200">{s.name}</p>
                  </div>
                  <div className="text-right">
                    <div className={cn("text-2xl font-bold font-mono", s.score >= 8.5 ? "text-emerald-400" : s.score >= 7 ? "text-amber-400" : "text-red-400")}>
                      {s.score}
                    </div>
                    <div className="text-[9px] font-mono text-slate-600">/ 10.0</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Compliance",    val: s.compliance,  isOk: s.compliance === "OK" },
                    { label: "Risco Trab.",   val: s.trabalhista, isOk: s.trabalhista === "baixo" },
                    { label: "ESG",           val: s.esg,         isOk: s.esg === "alto" },
                  ].map(({ label, val, isOk }) => (
                    <div key={label} className="glass rounded-lg p-2 border border-white/5 text-center">
                      <div className={cn("text-xs font-mono font-bold", isOk ? "text-emerald-400" : "text-amber-400")}>{val}</div>
                      <div className="text-[9px] font-mono text-slate-600 mt-0.5">{label}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-semibold text-white">CHECKLIST HOMOLOGAÇÃO</span>
            </div>
            <div className="space-y-1.5">
              {CHECKLIST.map(c => (
                <div key={c.item} className="flex items-center gap-2">
                  <div className={cn("w-4 h-4 rounded border flex items-center justify-center shrink-0",
                    c.ok ? "bg-emerald-900/30 border-emerald-700/40" : "bg-red-900/20 border-red-700/30"
                  )}>
                    {c.ok ? <CheckCircle className="w-2.5 h-2.5 text-emerald-400" /> : <AlertTriangle className="w-2.5 h-2.5 text-red-400" />}
                  </div>
                  <span className={cn("text-[10px] font-mono", c.ok ? "text-slate-400" : "text-red-400")}>{c.item}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <HardHat className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">TREINAMENTOS</span>
            </div>
            <div className="space-y-3">
              {TRAININGS.map(t => (
                <div key={t.nome}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-slate-400 leading-tight">{t.nome}</span>
                    <span className="text-[10px] font-mono text-slate-500">{t.concluido}/{t.total}</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className={cn("h-1.5 rounded-full", t.concluido === t.total ? "bg-emerald-400" : "bg-amber-400")}
                      style={{ width: `${(t.concluido / t.total) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
