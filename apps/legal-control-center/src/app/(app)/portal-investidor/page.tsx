"use client";
import { motion } from "framer-motion";
import {
  BarChart2, TrendingUp, Shield, FileText, Building2,
  Globe, Award, Download, DollarSign, Lock, Users,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

const SPES = [
  { id: "SPE-044", nome: "Parque Industrial PR",   valor: "R$ 120M", retorno: "18,2%",  compliance: "OK",    risk: "verde"    as RiskLevel },
  { id: "SPE-031", nome: "Residencial Arco DF",    valor: "R$ 85M",  retorno: "14,7%",  compliance: "OK",    risk: "verde"    as RiskLevel },
  { id: "SPE-022", nome: "Comercial SP-330",       valor: "R$ 48M",  retorno: "—",      compliance: "ALERTA",risk: "vermelho" as RiskLevel },
  { id: "SPE-018", nome: "Fundo Logístico Sul",    valor: "R$ 62M",  retorno: "21,0%",  compliance: "OK",    risk: "verde"    as RiskLevel },
];

const PORTFOLIO_DATA = [
  { mes: "Jan", valor: 280 },
  { mes: "Fev", valor: 295 },
  { mes: "Mar", valor: 310 },
  { mes: "Abr", valor: 305 },
  { mes: "Mai", valor: 315 },
];

const PIE_DATA = [
  { name: "Residencial", value: 35, color: "#3b82f6" },
  { name: "Comercial",   value: 28, color: "#10b981" },
  { name: "Industrial",  value: 25, color: "#f59e0b" },
  { name: "Logística",   value: 12, color: "#8b5cf6" },
];

const RISK_ITEMS = [
  { categoria: "Jurídico",    nivel: "baixo",   val: "2 processos" },
  { categoria: "Regulatório", nivel: "medio",   val: "1 alvará pendente" },
  { categoria: "Mercado",     nivel: "baixo",   val: "Estável" },
  { categoria: "Ambiental",   nivel: "alto",    val: "OBRA-022 embargada" },
];

export default function PortalInvestidorPage() {
  const totalPortfolio = "R$ 315M";
  const retornoMedio = "18,0%";

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">PORTAL INVESTIDORES — CEA</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">SPEs · Governança · Compliance · Retorno</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 glass border border-white/10 text-slate-300 text-xs font-mono rounded-lg hover:bg-white/5 transition-colors">
            <Lock className="w-3.5 h-3.5" />
            Acesso Restrito
          </button>
          <button className="flex items-center gap-2 px-4 py-2 glass border border-blue-500/30 text-blue-400 text-xs font-mono rounded-lg hover:bg-blue-900/20 transition-colors">
            <Download className="w-3.5 h-3.5" />
            Relatório CEA
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Portfolio Total"     value={totalPortfolio} trend="up"     color="green" />
        <KpiCard label="Retorno Médio"       value={retornoMedio}   trend="up"     color="blue" />
        <KpiCard label="SPEs Ativas"         value={4}              trend="stable" color="amber" />
        <KpiCard label="Risco Jurídico"      value="BAIXO"          trend="down"   color="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Portfolio Chart + Pie */}
        <div className="xl:col-span-2 grid grid-cols-2 gap-4">
          <Card className="col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <BarChart2 className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">EVOLUÇÃO PORTFOLIO (R$ M)</span>
            </div>
            <ResponsiveContainer width="100%" height={120}>
              <AreaChart data={PORTFOLIO_DATA}>
                <defs>
                  <linearGradient id="portf" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area type="monotone" dataKey="valor" stroke="#3b82f6" fill="url(#portf)" strokeWidth={2} dot={false} />
                <XAxis dataKey="mes" tick={{ fontSize: 9, fill: "#475569", fontFamily: "monospace" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "8px", fontSize: "10px" }} formatter={(v) => `R$ ${v}M`} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-2">
              <Globe className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-semibold text-white">MIX PORTFÓLIO</span>
            </div>
            <div className="flex items-center gap-3">
              <PieChart width={80} height={80}>
                <Pie data={PIE_DATA} cx="50%" cy="50%" innerRadius={25} outerRadius={38} dataKey="value" strokeWidth={0}>
                  {PIE_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
              <div className="space-y-1 flex-1">
                {PIE_DATA.map(p => (
                  <div key={p.name} className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: p.color }} />
                    <span className="text-[9px] font-mono text-slate-500 flex-1">{p.name}</span>
                    <span className="text-[9px] font-mono text-slate-400 font-bold">{p.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">RISCO JURÍDICO</span>
            </div>
            <div className="space-y-2">
              {RISK_ITEMS.map(r => (
                <div key={r.categoria} className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">{r.categoria}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-mono text-slate-600">{r.val}</span>
                    <span className={cn("text-[9px] font-mono font-bold px-1.5 py-0.5 rounded",
                      r.nivel === "baixo" ? "bg-emerald-900/30 text-emerald-400" :
                      r.nivel === "medio" ? "bg-amber-900/30 text-amber-400" :
                      "bg-red-900/30 text-red-400"
                    )}>
                      {r.nivel.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* SPEs */}
          {SPES.map(spe => (
            <motion.div key={spe.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Card>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-[10px] font-mono text-slate-600">{spe.id}</span>
                    <p className="text-[11px] font-mono font-semibold text-slate-200 leading-tight mt-0.5">{spe.nome}</p>
                  </div>
                  <RiskBadge level={spe.risk} />
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-emerald-400 font-bold">{spe.valor}</span>
                  <span className={cn("font-bold", spe.retorno === "—" ? "text-slate-600" : "text-blue-400")}>{spe.retorno}</span>
                </div>
                <div className="mt-2">
                  <Badge variant={spe.compliance === "OK" ? "green" : "amber"}>{spe.compliance}</Badge>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Compliance / Governance */}
        <div className="space-y-4">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Award className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">GOVERNANÇA CEA</span>
            </div>
            <div className="space-y-2">
              {[
                { item: "Demonstrações CVM",        ok: true },
                { item: "Ata Reunião Cotistas",      ok: true },
                { item: "Relatório Anual Administr.",ok: true },
                { item: "Due Diligence ESG",         ok: true },
                { item: "Auditoria BDO",             ok: false },
              ].map(g => (
                <div key={g.item} className="flex items-center gap-2 p-2 glass rounded-lg border border-white/5">
                  <div className={cn("w-1.5 h-1.5 rounded-full", g.ok ? "bg-emerald-400" : "bg-amber-400 animate-pulse")} />
                  <span className={cn("text-[11px] font-mono", g.ok ? "text-slate-300" : "text-amber-400")}>{g.item}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">COTISTAS</span>
            </div>
            <div className="text-center mb-4">
              <div className="text-3xl font-bold font-mono text-blue-400">127</div>
              <div className="text-[10px] font-mono text-slate-500">investidores ativos</div>
            </div>
            <div className="space-y-1.5 text-[11px] font-mono">
              {[
                { label: "Pessoas Físicas",  val: "84" },
                { label: "Pessoas Jurídicas",val: "31" },
                { label: "Fundos",           val: "12" },
              ].map(({ label, val }) => (
                <div key={label} className="flex justify-between">
                  <span className="text-slate-500">{label}</span>
                  <span className="text-slate-300 font-bold">{val}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
