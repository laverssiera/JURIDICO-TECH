"use client";
import { motion } from "framer-motion";
import {
  Shield, CheckCircle, AlertTriangle, Clock, FileText,
  BarChart2, TrendingUp, Zap, Globe, RefreshCw, Lock,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, Tooltip, ResponsiveContainer,
  RadialBarChart, RadialBar,
} from "recharts";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

const FRAMEWORKS = [
  { name: "LGPD",        score: 96, status: "OK",      expires: "—" },
  { name: "ISO 9001",    score: 92, status: "OK",      expires: "2026-01" },
  { name: "ISO 14001",   score: 88, status: "OK",      expires: "2025-12" },
  { name: "ISO 45001",   score: 61, status: "PENDENTE",expires: "—" },
  { name: "SOX",         score: 94, status: "OK",      expires: "—" },
  { name: "COSO ERM",    score: 87, status: "OK",      expires: "—" },
  { name: "NR18",        score: 79, status: "ALERTA",  expires: "—" },
  { name: "NR35",        score: 85, status: "OK",      expires: "—" },
];

const RISKS = [
  { area: "Trabalhista", n: 42, risk: "vermelho" as RiskLevel },
  { area: "Ambiental",   n: 27, risk: "amarelo"  as RiskLevel },
  { area: "Contratual",  n: 61, risk: "verde"    as RiskLevel },
  { area: "Tributário",  n: 18, risk: "amarelo"  as RiskLevel },
  { area: "Societário",  n: 33, risk: "verde"    as RiskLevel },
];

const RADIAL = [
  { name: "Score", value: 94, fill: "#10b981" },
];

const AUDIT_LOG = [
  { ts: "09:14:22", action: "Auditoria SOX — aprovada",          user: "Auditor Externo", ok: true },
  { ts: "08:30:00", action: "NR18 — não conformidade registrada",user: "Sistema",         ok: false },
  { ts: "07:55:10", action: "LGPD DPA assinado — Fornecedor X",  user: "DPO",             ok: true },
  { ts: "06:00:00", action: "Varredura automática — 0 alertas",   user: "IA Compliance",  ok: true },
  { ts: "05/05",    action: "Relatório ESG enviado — CEO",         user: "ESG Team",       ok: true },
];

export default function CompliancePage() {
  const overall = 94;

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">COMPLIANCE CENTER</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">LGPD · ISO · SOX · NRs · Trilha Auditável</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass border border-teal-500/30 text-teal-400 text-xs font-mono rounded-lg hover:bg-teal-900/20 transition-colors">
          <RefreshCw className="w-3.5 h-3.5" />
          Varredura Agora
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Score Global"       value="94%"  trend="up"     color="green" />
        <KpiCard label="Frameworks OK"      value={6}    trend="stable" color="green" />
        <KpiCard label="Pendências"         value={3}    trend="down"   color="amber" />
        <KpiCard label="Alertas Críticos"   value={1}    trend="down"   color="red" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Score gauge */}
        <Card className="flex flex-col items-center justify-center">
          <div className="relative">
            <ResponsiveContainer width={160} height={160}>
              <RadialBarChart cx="50%" cy="50%" innerRadius={50} outerRadius={70} data={RADIAL} startAngle={230} endAngle={-50}>
                <RadialBar dataKey="value" cornerRadius={6} background={{ fill: "rgba(255,255,255,0.05)" }} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold font-mono text-emerald-400">{overall}</span>
              <span className="text-[10px] font-mono text-slate-500">Compliance</span>
            </div>
          </div>
          <div className="text-center mt-2">
            <p className="text-sm font-mono font-bold text-emerald-400">APROVADO</p>
            <p className="text-[10px] font-mono text-slate-600">Última varredura: hoje, 06:00</p>
          </div>
        </Card>

        {/* Frameworks */}
        <div className="xl:col-span-2">
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-4 h-4 text-teal-400" />
              <span className="text-xs font-mono font-semibold text-white">FRAMEWORKS & NORMAS</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {FRAMEWORKS.map((f, i) => (
                <motion.div key={f.name} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}
                  className="flex items-center gap-3 p-2.5 glass rounded-lg border border-white/5">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[11px] font-mono font-bold text-slate-200">{f.name}</span>
                      <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded",
                        f.status === "OK"      ? "bg-emerald-900/30 text-emerald-400" :
                        f.status === "ALERTA"  ? "bg-amber-900/30 text-amber-400" :
                        "bg-blue-900/30 text-blue-400"
                      )}>
                        {f.status}
                      </span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-1">
                      <div className={cn("h-1 rounded-full", f.score >= 90 ? "bg-emerald-400" : f.score >= 75 ? "bg-amber-400" : "bg-red-400")}
                        style={{ width: `${f.score}%` }} />
                    </div>
                  </div>
                  <span className={cn("text-sm font-mono font-bold shrink-0",
                    f.score >= 90 ? "text-emerald-400" : f.score >= 75 ? "text-amber-400" : "text-red-400"
                  )}>
                    {f.score}
                  </span>
                </motion.div>
              ))}
            </div>
          </Card>
        </div>

        {/* Risk chart */}
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <BarChart2 className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-mono font-semibold text-white">RISCOS POR ÁREA</span>
          </div>
          <div className="space-y-2">
            {RISKS.map(r => (
              <div key={r.area} className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-slate-500 w-20">{r.area}</span>
                <div className="flex-1 bg-white/5 rounded-full h-2">
                  <div className={cn("h-2 rounded-full",
                    r.risk === "verde" ? "bg-emerald-400" : r.risk === "amarelo" ? "bg-amber-400" : "bg-red-400"
                  )} style={{ width: `${(r.n / 80) * 100}%` }} />
                </div>
                <span className="text-[10px] font-mono text-slate-400 w-6 text-right">{r.n}</span>
                <RiskBadge level={r.risk} />
              </div>
            ))}
          </div>
        </Card>

        {/* Audit log */}
        <div className="xl:col-span-2">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Lock className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">TRILHA DE AUDITORIA</span>
              <Badge variant="amber">Blockchain</Badge>
            </div>
            <div className="space-y-2">
              {AUDIT_LOG.map((log, i) => (
                <div key={i} className="flex items-center gap-3 p-2.5 glass rounded-lg border border-white/5">
                  {log.ok ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />}
                  <div className="flex-1">
                    <p className="text-[11px] font-mono text-slate-200">{log.action}</p>
                    <p className="text-[9px] font-mono text-slate-600">{log.user} · {log.ts}</p>
                  </div>
                  <span className="text-[9px] font-mono text-slate-700 font-mono">0x{Math.random().toString(16).slice(2, 10)}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
