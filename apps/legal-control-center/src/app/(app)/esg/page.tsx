"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Leaf, Droplets, Wind, Trash2, Users, HardHat, Building2,
  BarChart2, TrendingUp, CheckCircle, AlertTriangle, Shield,
  FileText, Download, Globe, Award,
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid,
} from "recharts";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";

type Tab = "ambiental" | "sst" | "governanca";

const RADAR = [
  { subject: "Carbono",   A: 78 },
  { subject: "Água",      A: 91 },
  { subject: "Resíduos",  A: 65 },
  { subject: "SST",       A: 84 },
  { subject: "Diversidade",A: 72 },
  { subject: "Gov.",      A: 88 },
];

const CARBON_DATA = Array.from({ length: 6 }, (_, i) => ({
  mes: ["Nov","Dez","Jan","Fev","Mar","Abr"][i],
  emissoes: Math.floor(1200 - i * 60 + Math.random() * 80),
  meta: 1100 - i * 50,
}));

const WASTE_DATA = [
  { tipo: "Madeira",   rec: 72, nrec: 28 },
  { tipo: "Concreto",  rec: 58, nrec: 42 },
  { tipo: "Metal",     rec: 91, nrec: 9  },
  { tipo: "Plástico",  rec: 44, nrec: 56 },
  { tipo: "Perigoso",  rec: 12, nrec: 88 },
];

const SST_EVENTS = [
  { id: "SST-001", tipo: "Quase-Acidente",       obra: "OBRA-022", nr: "NR18", severity: "vermelho", data: "05/05" },
  { id: "SST-002", tipo: "NR35 — Trabalho Altura",obra: "OBRA-067", nr: "NR35", severity: "amarelo",  data: "03/05" },
  { id: "SST-003", tipo: "Treinamento Concluído", obra: "OBRA-031", nr: "NR18", severity: "verde",    data: "01/05" },
  { id: "SST-004", tipo: "EPI Incompleto",        obra: "SPE-044",  nr: "NR6",  severity: "amarelo",  data: "30/04" },
  { id: "SST-005", tipo: "Auditoria Periódica",   obra: "OBRA-022", nr: "PCMAT",severity: "verde",    data: "28/04" },
];

const SUPPLIERS = [
  { name: "Meridian Construtora", score: 8.9, compliance: "OK",    trabalhista: "baixo", esg: "médio" },
  { name: "Engepavi Ltda",        score: 7.2, compliance: "ALERTA",trabalhista: "médio", esg: "baixo" },
  { name: "Steel Ind.",           score: 9.1, compliance: "OK",    trabalhista: "baixo", esg: "alto"  },
  { name: "Alpha Cimento",        score: 6.5, compliance: "ALERTA",trabalhista: "alto",  esg: "baixo" },
];

export default function EsgPage() {
  const [tab, setTab] = useState<Tab>("ambiental");

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">ESG + COMPLIANCE CENTER</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Ambiental · SST · Governança · Fornecedores</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass border border-emerald-500/30 text-emerald-400 text-xs font-mono rounded-lg hover:bg-emerald-900/20 transition-colors">
          <Download className="w-3.5 h-3.5" />
          Relatório ESG
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Score ESG Global"      value="82/100" trend="up"     color="green" />
        <KpiCard label="Incidentes SST"        value={6}      trend="down"   color="amber" />
        <KpiCard label="Compliance Score"      value="94%"    trend="up"     color="green" />
        <KpiCard label="Auditoria Fornecedor"  value={23}     trend="stable" color="blue" />
      </div>

      {/* Radar + Tabs */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-5">
        <Card>
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono font-semibold text-white">RADAR ESG</span>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={RADAR}>
              <PolarGrid stroke="rgba(255,255,255,0.05)" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fill: "#64748b", fontFamily: "monospace" }} />
              <Radar dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={1.5} dot={false} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        <div className="xl:col-span-3">
          {/* Tab selector */}
          <div className="flex gap-1 mb-4 p-1 glass rounded-lg border border-white/5 w-fit">
            {([
              { id: "ambiental",  label: "🌱 AMBIENTAL",  },
              { id: "sst",        label: "👷 SST",          },
              { id: "governanca", label: "🏛️ GOVERNANÇA",  },
            ] as const).map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={cn(
                  "px-3 py-1.5 rounded text-[11px] font-mono transition-all",
                  tab === t.id ? "bg-emerald-500/20 text-emerald-400" : "text-slate-500 hover:text-slate-300"
                )}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Ambiental */}
          {tab === "ambiental" && (
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <div className="flex items-center gap-2 mb-3">
                  <Wind className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-mono font-semibold text-white">EMISSÕES CO₂ (tCO₂e)</span>
                </div>
                <ResponsiveContainer width="100%" height={120}>
                  <LineChart data={CARBON_DATA}>
                    <CartesianGrid stroke="rgba(255,255,255,0.03)" />
                    <XAxis dataKey="mes" tick={{ fontSize: 9, fill: "#475569", fontFamily: "monospace" }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "8px", fontSize: "10px" }} />
                    <Line type="monotone" dataKey="emissoes" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="Real" />
                    <Line type="monotone" dataKey="meta" stroke="#10b981" strokeWidth={1} dot={false} strokeDasharray="4 2" name="Meta" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              <Card>
                <div className="flex items-center gap-2 mb-3">
                  <Trash2 className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-mono font-semibold text-white">RESÍDUOS (% reciclado)</span>
                </div>
                <ResponsiveContainer width="100%" height={120}>
                  <BarChart data={WASTE_DATA} barSize={8}>
                    <Bar dataKey="rec" fill="#10b981" radius={[2,2,0,0]} name="Reciclado" stackId="a" />
                    <Bar dataKey="nrec" fill="#ef4444" radius={[2,2,0,0]} name="Não reciclado" stackId="a" />
                    <XAxis dataKey="tipo" tick={{ fontSize: 8, fill: "#475569", fontFamily: "monospace" }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "8px", fontSize: "10px" }} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <Card>
                <div className="flex items-center gap-2 mb-2">
                  <Droplets className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-mono font-semibold text-white">CONSUMO HÍDRICO</span>
                </div>
                <div className="text-3xl font-bold font-mono text-cyan-400 mb-1">12.4 <span className="text-lg">mil m³</span></div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white/5 rounded-full h-2">
                    <div className="h-2 rounded-full bg-cyan-400" style={{ width: "68%" }} />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">68% da meta</span>
                </div>
              </Card>

              <Card>
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-mono font-semibold text-white">CARBONO NEUTRO</span>
                </div>
                <div className="text-3xl font-bold font-mono text-emerald-400 mb-1">2030</div>
                <p className="text-[10px] font-mono text-slate-500">Meta NetZero · Progresso: 42%</p>
                <div className="mt-2 flex-1 bg-white/5 rounded-full h-2">
                  <div className="h-2 rounded-full bg-gradient-to-r from-emerald-700 to-emerald-400" style={{ width: "42%" }} />
                </div>
              </Card>
            </div>
          )}

          {/* SST */}
          {tab === "sst" && (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <KpiCard label="Acidentes (12M)" value={2}  trend="down" color="green" />
                <KpiCard label="Quase-acidentes"  value={14} trend="up"   color="amber" />
                <KpiCard label="Treinamentos"     value={89} trend="up"   color="blue" />
              </div>
              <Card>
                <div className="flex items-center gap-2 mb-3">
                  <HardHat className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-mono font-semibold text-white">EVENTOS SST</span>
                </div>
                <div className="space-y-2">
                  {SST_EVENTS.map(ev => (
                    <div key={ev.id} className="flex items-center gap-3 p-2.5 glass rounded-lg border border-white/5">
                      <RiskBadge level={ev.severity as any} />
                      <div className="flex-1">
                        <p className="text-[11px] font-mono font-semibold text-slate-200">{ev.tipo}</p>
                        <p className="text-[9px] font-mono text-slate-600">{ev.obra} · {ev.nr} · {ev.data}</p>
                      </div>
                      <Badge variant={ev.severity === "verde" ? "green" : ev.severity === "amarelo" ? "amber" : "red"}>{ev.nr}</Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* Governança */}
          {tab === "governanca" && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Card>
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-mono font-semibold text-white">SCORE FORNECEDORES</span>
                  </div>
                  <div className="space-y-2">
                    {SUPPLIERS.map(s => (
                      <div key={s.name} className="flex items-center gap-3 p-2 glass rounded-lg border border-white/5">
                        <div className="flex-1 min-w-0">
                          <p className="text-[11px] font-mono font-semibold text-slate-200 truncate">{s.name}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className={cn("text-[9px] font-mono", s.compliance === "OK" ? "text-emerald-400" : "text-amber-400")}>
                              Compliance: {s.compliance}
                            </span>
                            <span className={cn("text-[9px] font-mono", s.esg === "alto" ? "text-emerald-400" : s.esg === "médio" ? "text-amber-400" : "text-red-400")}>
                              ESG: {s.esg}
                            </span>
                          </div>
                        </div>
                        <div className={cn("text-lg font-bold font-mono", s.score >= 8.5 ? "text-emerald-400" : s.score >= 7 ? "text-amber-400" : "text-red-400")}>
                          {s.score}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card>
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="w-4 h-4 text-purple-400" />
                    <span className="text-xs font-mono font-semibold text-white">AUDITORIA</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { label: "ISO 9001:2015",   status: "OK",      exp: "2026-01" },
                      { label: "ISO 14001:2015",  status: "OK",      exp: "2025-12" },
                      { label: "ISO 45001",       status: "PENDENTE",exp: "—" },
                      { label: "LGPD",            status: "OK",      exp: "—" },
                      { label: "SOX",             status: "OK",      exp: "—" },
                    ].map(a => (
                      <div key={a.label} className="flex items-center justify-between p-2 glass rounded-lg border border-white/5">
                        <span className="text-[11px] font-mono text-slate-300">{a.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-[9px] font-mono text-slate-600">{a.exp}</span>
                          <span className={cn("text-[9px] font-mono font-bold px-1.5 py-0.5 rounded",
                            a.status === "OK" ? "bg-emerald-900/30 text-emerald-400" : "bg-amber-900/30 text-amber-400"
                          )}>{a.status}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
