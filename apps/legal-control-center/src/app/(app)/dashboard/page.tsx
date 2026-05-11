"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle, Building2, FileText, Gavel, Globe, Radio,
  Shield, TrendingUp, Zap, Activity, MapPin, Clock, CheckCircle,
  AlertCircle, XCircle, Flame, Wind, Droplets,
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, ResponsiveContainer,
  XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { api } from "@/lib/api";
import { useLegalStore } from "@/store/legal";
import { Card, KpiCard, Badge, RiskBadge, SectionHeader } from "@/components/ui";
import type { RiskLevel } from "@/components/ui";

/* ─── mock data ─────────────────────────────────────────── */
type KpiItem = {
  label: string;
  value: number | string;
  trend: "up" | "down" | "stable";
  color: "blue" | "amber" | "green" | "red";
  icon: typeof Building2;
};

const KPI_DATA: KpiItem[] = [
  { label: "Obras Monitoradas",    value: 247,   trend: "up",     color: "blue",  icon: Building2 },
  { label: "Processos Ativos",     value: 1_843, trend: "up",     color: "amber", icon: Gavel },
  { label: "Contratos Vigentes",   value: 612,   trend: "stable", color: "green", icon: FileText },
  { label: "Incidentes Abertos",   value: 18,    trend: "down",   color: "red",   icon: AlertTriangle },
  { label: "Compliance Score",     value: "94%",trend: "up",     color: "green", icon: Shield },
  { label: "Fornecedores Ativos",  value: 389,   trend: "up",     color: "blue",  icon: Globe },
];

const HEATMAP_ITEMS: { id: string; label: string; tipo: string; risk: RiskLevel; loc: string }[] = [
  { id: "OBRA-22", label: "Ponte Rodovia SP-330",   tipo: "Embargo Ambiental",    risk: "preto",    loc: "SP" },
  { id: "FORN-88", label: "Construtora Meridian",   tipo: "Risco Trabalhista",    risk: "vermelho", loc: "MG" },
  { id: "PROC-14", label: "Ação Coletiva NR18",     tipo: "Litígio Trabalhista",  risk: "vermelho", loc: "RJ" },
  { id: "SPE-44",  label: "SPE Parque Industrial",  tipo: "Compliance Aprovado",  risk: "verde",    loc: "PR" },
  { id: "OBRA-67", label: "Edifício Torre Norte",   tipo: "Vistoria Pendente",    risk: "amarelo",  loc: "DF" },
  { id: "FORN-12", label: "Engepavi Ltda",          tipo: "ESG — Desvio hídrico", risk: "amarelo",  loc: "BA" },
  { id: "ARB-03",  label: "Arbitragem CEA-2024",    tipo: "Audiência 14/05",      risk: "vermelho", loc: "SP" },
  { id: "ANCH-09", label: "Perícia ANCHOR #09",     tipo: "Laudo Emitido",        risk: "verde",    loc: "SC" },
];

const AREA_DATA = Array.from({ length: 12 }, (_, i) => ({
  mes: ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][i],
  processos: Math.floor(1200 + Math.random() * 400),
  contratos: Math.floor(400 + Math.random() * 200),
  risco: Math.floor(10 + Math.random() * 30),
}));

const BAR_DATA = [
  { area: "Trabalhista", valor: 42 },
  { area: "Ambiental",  valor: 27 },
  { area: "Contratual", valor: 61 },
  { area: "Tributário", valor: 18 },
  { area: "Societário", valor: 33 },
  { area: "Arbitragem", valor: 15 },
];

const MAP_PINS: { lat: number; lng: number; id: string; risk: RiskLevel; label: string }[] = [
  { lat: 64,  lng: 42,  id: "OBRA-22", risk: "preto",    label: "SP" },
  { lat: 50,  lng: 55,  id: "FORN-88", risk: "vermelho", label: "MG" },
  { lat: 58,  lng: 65,  id: "SPE-44",  risk: "verde",    label: "PR" },
  { lat: 46,  lng: 70,  id: "OBRA-67", risk: "amarelo",  label: "DF" },
  { lat: 35,  lng: 58,  id: "PROC-14", risk: "vermelho", label: "RJ" },
  { lat: 30,  lng: 35,  id: "FORN-12", risk: "amarelo",  label: "BA" },
  { lat: 20,  lng: 45,  id: "ANCH-09", risk: "verde",    label: "SC" },
];

const RISK_COLOR: Record<RiskLevel, string> = {
  verde:    "#10b981",
  amarelo:  "#f59e0b",
  vermelho: "#ef4444",
  preto:    "#dc2626",
};

/* ─── Event Feed ─────────────────────────────────────────── */
const SEED_EVENTS = [
  { id: "1", type: "OBRA-22 → embargo ambiental",       ts: "09:14:22", level: "preto" },
  { id: "2", type: "FORN-88 → risco trabalhista",        ts: "09:12:01", level: "vermelho" },
  { id: "3", type: "SPE-44 → compliance aprovado",       ts: "09:10:44", level: "verde" },
  { id: "4", type: "ANCHOR → perícia concluída #09",     ts: "09:08:17", level: "verde" },
  { id: "5", type: "ARB-03 → audiência agendada 14/05",  ts: "08:59:02", level: "amarelo" },
  { id: "6", type: "OBRA-67 → vistoria SST solicitada",  ts: "08:45:30", level: "amarelo" },
  { id: "7", type: "NR18 → treinamento concluído",       ts: "08:30:00", level: "verde" },
];

function levelIcon(level: string) {
  if (level === "preto" || level === "vermelho") return <XCircle className="w-3.5 h-3.5 text-red-400" />;
  if (level === "amarelo") return <AlertCircle className="w-3.5 h-3.5 text-amber-400" />;
  return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />;
}

/* ─── Component ─────────────────────────────────────────── */
export default function DashboardPage() {
  const { events, wsStatus } = useLegalStore();
  const [tick, setTick] = useState(0);
  const [kpiData, setKpiData] = useState<KpiItem[]>(KPI_DATA);
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    const t = setInterval(() => setTick(v => v + 1), 3000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let cancelled = false;

    type ContractsResp = { total: number };
    type ArbitrationResp = { total: number };
    type ComplianceChecksResp = {
      total: number;
      items: Array<{ score: number }>;
    };
    type ComplianceAlert = {
      id: string;
      severity: "low" | "medium" | "high" | "critical";
    };

    const load = async () => {
      try {
        const [contracts, arbitrations, checks, alerts] = await Promise.all([
          api.get<ContractsResp>("/contracts/"),
          api.get<ArbitrationResp>("/arbitration/"),
          api.get<ComplianceChecksResp>("/compliance/checks"),
          api.get<ComplianceAlert[]>("/compliance/alerts/open"),
        ]);

        if (cancelled) return;

        const complianceAvg = checks.items.length
          ? Math.round(checks.items.reduce((acc, c) => acc + c.score, 0) / checks.items.length)
          : 0;
        const criticalAlerts = alerts.filter((a) => a.severity === "critical" || a.severity === "high").length;

        setKpiData([
          { ...KPI_DATA[0], value: 247 },
          { ...KPI_DATA[1], value: arbitrations.total },
          { ...KPI_DATA[2], value: contracts.total },
          { ...KPI_DATA[3], value: alerts.length },
          { ...KPI_DATA[4], value: `${complianceAvg}%` },
          { ...KPI_DATA[5], value: Math.max(criticalAlerts, 0) },
        ]);
      } catch {
        // mantém KPI_DATA mock caso API indisponível
      }
    };

    load();
    const id = setInterval(load, 12000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const feedEvents = [...SEED_EVENTS, ...events.slice(0, 10).map(e => ({
    id: e.id, type: e.type, ts: new Date(e.ts).toLocaleTimeString("pt-BR"), level: "verde",
  }))];
  const currentDateLabel = now
    ? now.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })
    : "...";
  const currentTimeLabel = now ? now.toLocaleTimeString("pt-BR") : "--:--:--";

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">
            HOME OPERACIONAL
          </h1>
          <p className="text-xs text-slate-500 font-mono mt-0.5">
            LICEU 6.x · LEGAL COMMAND CENTER · {currentDateLabel}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-mono ${
            wsStatus === "connected"
              ? "bg-emerald-900/20 border-emerald-700/30 text-emerald-400"
              : "bg-red-900/20 border-red-700/30 text-red-400"
          }`}>
            <Radio className="w-3 h-3" />
            {wsStatus === "connected" ? "NATS LIVE" : "OFFLINE"}
          </div>
          <div className="text-xs font-mono text-slate-600 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {currentTimeLabel}
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
        {kpiData.map(({ label, value, trend, color, icon: Icon }) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className={`glass rounded-xl p-4 border ${
              color === "blue"  ? "border-blue-500/20"    :
              color === "green" ? "border-emerald-500/20" :
              color === "amber" ? "border-amber-500/20"   :
              "border-red-500/20"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <Icon className={`w-4 h-4 ${
                color === "blue"  ? "text-blue-400"    :
                color === "green" ? "text-emerald-400" :
                color === "amber" ? "text-amber-400"   :
                "text-red-400"
              }`} />
              <span className={`text-xs font-mono ${
                trend === "up" ? "text-emerald-400" : trend === "down" ? "text-red-400" : "text-slate-500"
              }`}>
                {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"}
              </span>
            </div>
            <div className={`text-2xl font-bold font-mono ${
              color === "blue"  ? "text-blue-400"    :
              color === "green" ? "text-emerald-400" :
              color === "amber" ? "text-amber-400"   :
              "text-red-400"
            }`}>{typeof value === "number" ? value.toLocaleString("pt-BR") : value}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1 leading-tight">{label}</div>
          </motion.div>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Mapa Global LICEU */}
        <div className="xl:col-span-2">
          <Card className="h-[420px] relative overflow-hidden">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-mono font-semibold text-white tracking-wide">MAPA GLOBAL LICEU</span>
              </div>
              <div className="flex gap-2">
                {(["verde","amarelo","vermelho","preto"] as RiskLevel[]).map(r => (
                  <div key={r} className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: RISK_COLOR[r] }} />
                    <span className="text-[10px] font-mono text-slate-500">{r.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* SVG Map of Brazil (simplified) */}
            <div className="relative w-full h-[340px] bg-[#0a1628] rounded-lg border border-white/5 overflow-hidden">
              <svg viewBox="0 0 100 100" className="w-full h-full opacity-20">
                <rect x="0" y="0" width="100" height="100" fill="none" stroke="#1e3a5f" strokeWidth="0.2" />
                {Array.from({ length: 10 }, (_, i) => (
                  <line key={`h${i}`} x1="0" y1={i*10} x2="100" y2={i*10} stroke="#1e3a5f" strokeWidth="0.1" />
                ))}
                {Array.from({ length: 10 }, (_, i) => (
                  <line key={`v${i}`} x1={i*10} y1="0" x2={i*10} y2="100" stroke="#1e3a5f" strokeWidth="0.1" />
                ))}
              </svg>

              {/* Brazil outline simplified */}
              <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full">
                <path
                  d="M25,10 L35,8 L45,10 L55,8 L65,12 L72,18 L75,28 L78,38 L80,50 L78,62 L72,70 L65,78 L55,85 L45,88 L35,85 L28,78 L22,68 L18,55 L15,42 L18,30 L22,20 Z"
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth="0.5"
                  opacity="0.3"
                />
              </svg>

              {MAP_PINS.map((pin, idx) => (
                <motion.div
                  key={pin.id}
                  className="absolute"
                  style={{ left: `${pin.lng}%`, top: `${pin.lat}%` }}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  {/* pulse ring for critical */}
                  {(pin.risk === "preto" || pin.risk === "vermelho") && (
                    <div className="absolute -inset-2 rounded-full animate-ping"
                      style={{ backgroundColor: RISK_COLOR[pin.risk], opacity: 0.2 }} />
                  )}
                  <div
                    className="w-3 h-3 rounded-full border-2 border-white/20 cursor-pointer relative z-10"
                    style={{ backgroundColor: RISK_COLOR[pin.risk] }}
                    title={`${pin.id} · ${pin.label}`}
                  />
                  <div className="absolute left-4 top-0 text-[9px] font-mono text-slate-400 whitespace-nowrap">
                    {pin.id}
                  </div>
                </motion.div>
              ))}

              {/* Legend overlay */}
              <div className="absolute bottom-3 left-3 glass rounded-lg p-2 space-y-1">
                {[
                  { label: "Obras", icon: Building2 },
                  { label: "Processos", icon: Gavel },
                  { label: "Fornecedores", icon: Globe },
                  { label: "SPEs", icon: Shield },
                ].map(({ label, icon: Icon }) => (
                  <div key={label} className="flex items-center gap-1.5">
                    <Icon className="w-2.5 h-2.5 text-slate-500" />
                    <span className="text-[9px] font-mono text-slate-500">{label}</span>
                  </div>
                ))}
              </div>

              {/* Status overlay */}
              <div className="absolute top-3 right-3 glass rounded-lg px-2 py-1">
                <div className="text-[10px] font-mono text-slate-400">
                  <span className="text-blue-400 font-bold">247</span> ativos · <span className="text-red-400 font-bold">3</span> críticos
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Event Feed NATS */}
        <div>
          <Card className="h-[420px] flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-mono font-semibold text-white">EVENT FEED</span>
              </div>
              <Badge variant="amber">NATS RT</Badge>
            </div>

            <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
              <AnimatePresence initial={false}>
                {feedEvents.map((ev, i) => (
                  <motion.div
                    key={ev.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="flex items-start gap-2 p-2 rounded-lg bg-white/3 border border-white/5 hover:bg-white/5 transition-colors"
                  >
                    {levelIcon(ev.level)}
                    <div className="flex-1 min-w-0">
                      <p className="text-[11px] font-mono text-slate-300 leading-tight truncate">{ev.type}</p>
                      <p className="text-[9px] font-mono text-slate-600 mt-0.5">{ev.ts}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-600">Últimas 50 mensagens</span>
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] font-mono text-emerald-400">live</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Heatmap de Risco */}
        <div className="xl:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-red-400" />
                <span className="text-sm font-mono font-semibold text-white">HEATMAP DE RISCO</span>
              </div>
              <div className="flex gap-2 text-[10px] font-mono">
                <span className="text-emerald-400">● 4 verde</span>
                <span className="text-amber-400">● 2 amarelo</span>
                <span className="text-red-400">● 2 crítico</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {HEATMAP_ITEMS.map((item, i) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:scale-[1.02] ${
                    item.risk === "preto"    ? "border-red-900 bg-red-900/20 animate-pulse"   :
                    item.risk === "vermelho" ? "border-red-700/40 bg-red-900/10"               :
                    item.risk === "amarelo"  ? "border-yellow-700/40 bg-yellow-900/10"         :
                    "border-emerald-700/30 bg-emerald-900/10"
                  }`}
                >
                  <div className="flex items-start justify-between gap-1 mb-1">
                    <span className="text-[10px] font-mono font-bold text-slate-300">{item.id}</span>
                    <RiskBadge level={item.risk} />
                  </div>
                  <p className="text-[10px] font-mono text-slate-400 leading-tight truncate">{item.label}</p>
                  <p className="text-[9px] font-mono text-slate-600 mt-1 leading-tight">{item.tipo}</p>
                  <div className="flex items-center gap-1 mt-1.5">
                    <MapPin className="w-2.5 h-2.5 text-slate-600" />
                    <span className="text-[9px] font-mono text-slate-600">{item.loc}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="space-y-4">
          {/* Area Chart */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">PROCESSOS 12M</span>
            </div>
            <ResponsiveContainer width="100%" height={100}>
              <AreaChart data={AREA_DATA}>
                <defs>
                  <linearGradient id="proc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area type="monotone" dataKey="processos" stroke="#3b82f6" fill="url(#proc)" strokeWidth={1.5} dot={false} />
                <XAxis dataKey="mes" tick={{ fontSize: 9, fill: "#475569", fontFamily: "monospace" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "8px", fontSize: "10px" }} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Bar Chart */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">RISCO POR ÁREA</span>
            </div>
            <ResponsiveContainer width="100%" height={100}>
              <BarChart data={BAR_DATA} barSize={8}>
                <Bar dataKey="valor" fill="#f59e0b" radius={[2,2,0,0]} />
                <XAxis dataKey="area" tick={{ fontSize: 8, fill: "#475569", fontFamily: "monospace" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "#0d1117", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "8px", fontSize: "10px" }} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </div>
    </div>
  );
}
