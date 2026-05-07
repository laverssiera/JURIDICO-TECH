"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Siren, AlertTriangle, Radio, Clock, Globe, Users, Bot,
  Video, MessageSquare, FileText, Map, Activity, Zap,
  Shield, PhoneCall, SendHorizontal, XCircle, AlertCircle,
} from "lucide-react";
import { Card, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

interface Incident {
  id: string;
  title: string;
  type: "acidente" | "midia" | "embargo" | "judicial" | "ambiental";
  severity: RiskLevel;
  started: string;
  status: "ativo" | "contido" | "resolvido";
  updates: { ts: string; msg: string; user: string }[];
}

const INCIDENTS: Incident[] = [
  {
    id: "INC-001",
    title: "Embargo Ambiental — Rodovia SP-330",
    type: "ambiental",
    severity: "preto",
    started: "2025-05-07 06:40",
    status: "ativo",
    updates: [
      { ts: "07:10", msg: "IBAMA emitiu Auto de Infração #2249-SP", user: "Sistema" },
      { ts: "07:30", msg: "Equipe jurídica mobilizada", user: "Dr. Alencar" },
      { ts: "08:00", msg: "Liminar de suspensão em análise", user: "Dra. Lima" },
      { ts: "08:45", msg: "Perícia ambiental ANCHOR ativada — ANCH-14", user: "Sistema" },
      { ts: "09:14", msg: "John Legal recomendam habeas data + recurso administrativo", user: "John Legal IA" },
    ],
  },
  {
    id: "INC-002",
    title: "Crise de Mídia — Acidente SST Torre Norte",
    type: "midia",
    severity: "vermelho",
    started: "2025-05-06 14:20",
    status: "contido",
    updates: [
      { ts: "14:22", msg: "Notícia publicada — G1 SP", user: "Monitor Mídia" },
      { ts: "14:40", msg: "Nota oficial emitida", user: "Comunicação" },
      { ts: "15:00", msg: "Advogados on standby", user: "Dr. Costa" },
    ],
  },
  {
    id: "INC-003",
    title: "Ação Coletiva Trabalhista #1842",
    type: "judicial",
    severity: "vermelho",
    started: "2025-05-05 09:00",
    status: "ativo",
    updates: [
      { ts: "09:05", msg: "Petição inicial — 43 reclamantes", user: "TRT-15" },
      { ts: "10:00", msg: "Contestação preparada", user: "Dra. Lima" },
    ],
  },
];

const TYPE_CFG = {
  acidente:  { label: "Acidente",  color: "text-red-400",    icon: AlertTriangle },
  midia:     { label: "Mídia",     color: "text-amber-400",  icon: Radio },
  embargo:   { label: "Embargo",   color: "text-orange-400", icon: Shield },
  judicial:  { label: "Judicial",  color: "text-purple-400", icon: FileText },
  ambiental: { label: "Ambiental", color: "text-emerald-400",icon: Globe },
};

const TEAM = [
  { name: "Dr. Alencar",  role: "Sócio Responsável",       status: "online" },
  { name: "Dra. Lima",    role: "Contencioso Trabalhista",  status: "online" },
  { name: "Dr. Costa",    role: "Contratos",                status: "busy" },
  { name: "Eng. Sousa",   role: "Perícias ANCHOR",          status: "online" },
  { name: "ESG Team",     role: "Ambiental & Compliance",   status: "online" },
  { name: "Comunicação",  role: "Relações com Mídia",       status: "offline" },
];

const STATUS_DOT = { online: "bg-emerald-400", busy: "bg-amber-400 animate-pulse", offline: "bg-slate-600" };

export default function WarRoomPage() {
  const [selected, setSelected] = useState(INCIDENTS[0]);
  const [msg, setMsg] = useState("");

  const criticalCount = INCIDENTS.filter(i => i.severity === "preto" || i.severity === "vermelho").length;

  return (
    <div className="p-6 h-full flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-900/30 border border-red-700/40 flex items-center justify-center">
            <Siren className="w-4 h-4 text-red-400 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-mono font-bold text-red-400 tracking-wider">WAR ROOM</h1>
            <p className="text-xs font-mono text-slate-500 mt-0.5">
              {criticalCount} incidentes críticos · Operação ativa
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-900/20 border border-red-700/30 text-xs font-mono text-red-400">
            <div className="w-2 h-2 rounded-full bg-red-400 animate-ping" />
            CRISE ATIVA
          </div>
        </div>
      </div>

      {/* Incident Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {INCIDENTS.map(inc => {
          const TypeIcon = TYPE_CFG[inc.type].icon;
          return (
            <motion.button
              key={inc.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setSelected(inc)}
              className={cn(
                "text-left p-4 glass rounded-xl border transition-all",
                selected.id === inc.id ? "border-red-500/40 bg-red-900/10" : "border-white/5 hover:border-white/10"
              )}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <TypeIcon className={cn("w-4 h-4 shrink-0", TYPE_CFG[inc.type].color)} />
                  <span className="text-[10px] font-mono text-slate-400">{inc.id}</span>
                </div>
                <RiskBadge level={inc.severity} />
              </div>
              <p className="text-[11px] font-mono font-semibold text-slate-200 leading-tight mb-2">{inc.title}</p>
              <div className="flex items-center gap-2">
                <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded border",
                  inc.status === "ativo" ? "bg-red-900/30 text-red-400 border-red-700/30" :
                  inc.status === "contido" ? "bg-amber-900/30 text-amber-400 border-amber-700/30" :
                  "bg-emerald-900/30 text-emerald-400 border-emerald-700/30"
                )}>
                  {inc.status.toUpperCase()}
                </span>
                <span className="text-[9px] font-mono text-slate-600">{inc.started}</span>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Main War Room layout */}
      <div className="flex-1 overflow-hidden grid grid-cols-1 xl:grid-cols-4 gap-5">

        {/* Timeline & Chat */}
        <div className="xl:col-span-2 flex flex-col gap-4">
          <Card className="flex-1 flex flex-col">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-red-400" />
              <span className="text-xs font-mono font-semibold text-white">TIMELINE — {selected.id}</span>
              <Badge variant="red">{selected.updates.length} eventos</Badge>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 mb-3">
              {selected.updates.map((u, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex gap-3"
                >
                  <div className="flex flex-col items-center">
                    <div className={cn(
                      "w-2 h-2 rounded-full shrink-0 mt-1",
                      u.user === "John Legal IA" ? "bg-blue-400" :
                      u.user === "Sistema" ? "bg-amber-400" : "bg-slate-500"
                    )} />
                    {i < selected.updates.length - 1 && <div className="w-px flex-1 bg-white/5 mt-1" />}
                  </div>
                  <div className="pb-3">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[10px] font-mono font-bold text-slate-400">{u.ts}</span>
                      <span className={cn("text-[10px] font-mono",
                        u.user === "John Legal IA" ? "text-blue-400" :
                        u.user === "Sistema" ? "text-amber-400" : "text-slate-500"
                      )}>{u.user}</span>
                    </div>
                    <p className="text-[11px] font-mono text-slate-300 leading-relaxed">{u.msg}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Input */}
            <div className="flex gap-2 pt-3 border-t border-white/5">
              <input
                value={msg}
                onChange={e => setMsg(e.target.value)}
                placeholder="Registrar atualização..."
                className="flex-1 bg-white/5 border border-white/5 rounded-lg px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 outline-none focus:border-red-500/30"
              />
              <button className="px-3 py-2 bg-red-700 hover:bg-red-800 rounded-lg transition-colors">
                <SendHorizontal className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          </Card>
        </div>

        {/* Squad + IA */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-semibold text-white">SQUAD</span>
            </div>
            <div className="space-y-2">
              {TEAM.map(m => (
                <div key={m.name} className="flex items-center gap-2.5">
                  <div className="relative">
                    <div className="w-7 h-7 rounded-full bg-slate-700 border border-white/10 flex items-center justify-center text-[10px] font-mono font-bold text-slate-300">
                      {m.name[0]}
                    </div>
                    <div className={cn("absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-[#0d1117]", STATUS_DOT[m.status as keyof typeof STATUS_DOT])} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] font-mono font-semibold text-slate-200 truncate">{m.name}</p>
                    <p className="text-[9px] font-mono text-slate-600 truncate">{m.role}</p>
                  </div>
                  <button className="text-slate-600 hover:text-slate-300 transition-colors">
                    <PhoneCall className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Bot className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">JOHN LEGAL — IA</span>
            </div>
            <div className="space-y-2 text-[11px] font-mono">
              <div className="p-2.5 glass rounded-lg border border-blue-500/20 bg-blue-900/10">
                <p className="text-blue-400 font-semibold mb-1">Análise de Crise:</p>
                <p className="text-slate-400 leading-relaxed">Auto de Infração nº 2249 apresenta <span className="text-red-400">vícios formais</span>. Recomendo mandado de segurança preventivo + recurso administrativo paralelo.</p>
              </div>
              <div className="p-2.5 glass rounded-lg border border-amber-500/20 bg-amber-900/10">
                <p className="text-amber-400 font-semibold mb-1">Precedente:</p>
                <p className="text-slate-400">TRF-3 · Agravo 5004321-SP · "Embargo sem AIA prévia — nulidade"</p>
              </div>
              <div className="p-2.5 glass rounded-lg border border-emerald-500/20 bg-emerald-900/10">
                <p className="text-emerald-400 font-semibold mb-1">Ação Recomendada:</p>
                <p className="text-slate-400">Protocolar Habeas Data + Liminar em 6h. Convocar IBAMA para reunião técnica.</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Videowall + Map */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Video className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-semibold text-white">VIDEOWALL</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {["Cam 1 — Obra SP-330","Cam 2 — Acesso Norte","Cam 3 — Perímetro","Cam 4 — Drone Live"].map((cam, i) => (
                <div key={cam} className={cn(
                  "rounded-lg bg-[#0a0f1a] border border-white/5 flex flex-col items-center justify-center gap-1 relative",
                  i === 0 ? "h-24" : "h-14"
                )}>
                  <Video className="w-4 h-4 text-slate-700" />
                  <span className="text-[8px] font-mono text-slate-700 text-center px-1">{cam}</span>
                  {i === 0 && (
                    <div className="absolute top-1.5 right-1.5 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                      <span className="text-[8px] font-mono text-red-400">AO VIVO</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Map className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">MAPA OPERACIONAL</span>
            </div>
            <div className="h-28 bg-[#0a1628] rounded-lg border border-white/5 relative overflow-hidden flex items-center justify-center">
              <div className="text-[10px] font-mono text-slate-600">SP-330 km 42 · Itatiba-SP</div>
              <div className="absolute top-3 right-3 w-3 h-3 rounded-full bg-red-500 animate-ping opacity-60" />
              <div className="absolute top-3 right-3 w-3 h-3 rounded-full bg-red-500" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">AÇÕES RÁPIDAS</span>
            </div>
            <div className="space-y-1.5">
              {[
                { label: "Protocolar Liminar",   color: "bg-red-700 hover:bg-red-800" },
                { label: "Convocar IBAMA",        color: "bg-amber-700 hover:bg-amber-800" },
                { label: "Emitir Nota Oficial",   color: "bg-blue-700 hover:bg-blue-800" },
                { label: "Ativar Perícia",        color: "bg-purple-700 hover:bg-purple-800" },
              ].map(a => (
                <button key={a.label} className={cn("w-full py-2 text-xs font-mono text-white rounded-lg transition-colors text-left px-3", a.color)}>
                  {a.label}
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
