"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Camera, Upload, Bot, Shield, FileSearch, MapPin, Clock,
  CheckCircle, AlertTriangle, Thermometer, Activity, Eye,
  Radio, Layers, BarChart2, ChevronRight, Cpu, Lock,
} from "lucide-react";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

interface Pericia {
  id: string;
  title: string;
  obra: string;
  tipo: string;
  status: "vistoria" | "coleta" | "analise_ia" | "laudo" | "assinatura" | "custodia";
  risk: RiskLevel;
  perito: string;
  loc: string;
  evidencias: number;
  iaScore: number;
  findings: string[];
  date: string;
}

const PERICIAS: Pericia[] = [
  {
    id: "ANCH-09", title: "Perícia Estrutural — Torre Norte", obra: "OBRA-067",
    tipo: "Patologia Estrutural", status: "custodia", risk: "verde",
    perito: "Eng. G. Sousa", loc: "São Carlos, SP", evidencias: 147, iaScore: 94,
    findings: ["Sem fissuras críticas", "Infiltração nível 1 — subsolo", "Vibração OK"],
    date: "2025-05-03",
  },
  {
    id: "ANCH-14", title: "Perícia Ambiental — Rodovia SP-330", obra: "OBRA-022",
    tipo: "Dano Ambiental", status: "analise_ia", risk: "preto",
    perito: "Eng. P. Ferreira", loc: "Itatiba, SP", evidencias: 312, iaScore: 22,
    findings: ["Contaminação solo detectada", "APP suprimida irregularmente", "⚠ Embargo recomendado"],
    date: "2025-05-05",
  },
  {
    id: "ANCH-11", title: "Vistoria SST — Obra Parque Industrial", obra: "SPE-044",
    tipo: "NR18 / NR35", status: "laudo", risk: "amarelo",
    perito: "Eng. R. Santos", loc: "Londrina, PR", evidencias: 89, iaScore: 67,
    findings: ["2 não conformidades NR18", "EPI incompleto — setor A", "Sinalização pendente"],
    date: "2025-05-04",
  },
  {
    id: "ANCH-07", title: "Laudo Térmico — Fachada Edifício Arco", obra: "OBRA-031",
    tipo: "Termografia", status: "custodia", risk: "verde",
    perito: "Eng. M. Lima", loc: "Brasília, DF", evidencias: 63, iaScore: 91,
    findings: ["Sem anomalias térmicas", "Vedação aprovada", "Relatório OK"],
    date: "2025-04-28",
  },
];

const STEPS = [
  { id: "vistoria",    label: "Vistoria",    icon: Eye },
  { id: "coleta",      label: "Coleta",      icon: Camera },
  { id: "analise_ia",  label: "Análise IA",  icon: Cpu },
  { id: "laudo",       label: "Laudo",       icon: FileSearch },
  { id: "assinatura",  label: "Assinatura",  icon: Lock },
  { id: "custodia",    label: "Custódia",    icon: Shield },
];

const EVIDENCE_TYPES = [
  { label: "Drones",        icon: Radio,        count: 48, color: "text-blue-400" },
  { label: "Fotografias",   icon: Camera,       count: 156, color: "text-emerald-400" },
  { label: "Térmicas",      icon: Thermometer,  count: 34, color: "text-amber-400" },
  { label: "Sensores",      icon: Activity,     count: 22, color: "text-purple-400" },
  { label: "Vídeos",        icon: Layers,       count: 14, color: "text-cyan-400" },
];

const IA_DETECTIONS = [
  { tipo: "Fissura estrutural",   conf: 94, lok: "Pilar P-07, Base", color: "text-red-400" },
  { tipo: "Infiltração",          conf: 87, lok: "Subsolo, Junta",   color: "text-amber-400" },
  { tipo: "Vibração excessiva",   conf: 61, lok: "Laje 3º andar",    color: "text-amber-400" },
  { tipo: "Falha estrutural",     conf: 31, lok: "Não detectada",    color: "text-emerald-400" },
];

export default function PericiasPage() {
  const [selected, setSelected] = useState<Pericia>(PERICIAS[0]);

  const stepIdx = STEPS.findIndex(s => s.id === selected.status);

  return (
    <div className="p-6 h-full flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">MÓDULO PERÍCIAS ANCHOR</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Evidências · IA Forense · Cadeia de Custódia</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-700 hover:bg-purple-800 text-white text-xs font-mono rounded-lg transition-colors">
          <Upload className="w-3.5 h-3.5" />
          Nova Perícia
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Perícias Ativas"     value={34}  trend="up"     color="blue" />
        <KpiCard label="Em Análise IA"       value={8}   trend="stable" color="amber" />
        <KpiCard label="Laudos Emitidos"     value={127} trend="up"     color="green" />
        <KpiCard label="Casos Críticos"      value={4}   trend="up"     color="red" />
      </div>

      <div className="flex-1 overflow-hidden grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Pericia List */}
        <div className="xl:col-span-1 space-y-2 overflow-y-auto">
          {PERICIAS.map(p => (
            <motion.button
              key={p.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setSelected(p)}
              className={cn(
                "w-full text-left p-3 glass rounded-xl border transition-all",
                selected.id === p.id ? "border-purple-500/40 bg-purple-900/10" : "border-white/5 hover:border-white/10"
              )}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5">
                  <FileSearch className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span className="text-[11px] font-mono font-semibold text-slate-200">{p.id}</span>
                </div>
                <RiskBadge level={p.risk} />
              </div>
              <p className="text-[11px] font-mono text-slate-300 leading-tight mb-1.5 text-left">{p.title}</p>
              <div className="flex items-center gap-2 text-[9px] font-mono text-slate-600">
                <MapPin className="w-2.5 h-2.5" />
                <span>{p.loc}</span>
                <span>·</span>
                <span>{p.evidencias} evidências</span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2 space-y-4 overflow-y-auto">

          <Card>
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <FileSearch className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-mono font-bold text-white">{selected.id}</span>
                  <Badge variant="blue">{selected.tipo}</Badge>
                </div>
                <p className="text-sm font-semibold text-slate-200">{selected.title}</p>
                <div className="flex items-center gap-3 mt-1 text-[10px] font-mono text-slate-600">
                  <span className="flex items-center gap-1"><MapPin className="w-2.5 h-2.5" />{selected.loc}</span>
                  <span className="flex items-center gap-1"><Clock className="w-2.5 h-2.5" />{selected.date}</span>
                  <span>{selected.perito}</span>
                </div>
              </div>
              <RiskBadge level={selected.risk} />
            </div>

            {/* Timeline Pericial */}
            <div className="flex items-center gap-1 overflow-x-auto mb-2">
              {STEPS.map((s, i) => {
                const done = i < stepIdx;
                const current = i === stepIdx;
                return (
                  <div key={s.id} className="flex items-center shrink-0">
                    <div className={cn(
                      "flex flex-col items-center gap-1 px-2 py-2 rounded-lg transition-all",
                      current ? "bg-purple-500/20 border border-purple-500/30" :
                      done    ? "bg-emerald-900/20 border border-emerald-700/20" :
                      "bg-white/2 border border-white/5"
                    )}>
                      <s.icon className={cn("w-3.5 h-3.5", current ? "text-purple-400" : done ? "text-emerald-400" : "text-slate-600")} />
                      <span className={cn("text-[9px] font-mono", current ? "text-purple-400" : done ? "text-emerald-400" : "text-slate-600")}>
                        {s.label}
                      </span>
                    </div>
                    {i < STEPS.length - 1 && <ChevronRight className={cn("w-3 h-3 mx-1 shrink-0", done ? "text-emerald-700" : "text-slate-700")} />}
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Two columns: evidences + IA */}
          <div className="grid grid-cols-2 gap-4">
            {/* Evidence Upload */}
            <Card>
              <div className="flex items-center gap-2 mb-3">
                <Upload className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-mono font-semibold text-white">EVIDÊNCIAS</span>
              </div>
              <div className="space-y-2">
                {EVIDENCE_TYPES.map(ev => (
                  <div key={ev.label} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ev.icon className={cn("w-3.5 h-3.5", ev.color)} />
                      <span className="text-[11px] font-mono text-slate-400">{ev.label}</span>
                    </div>
                    <span className={cn("text-[11px] font-mono font-bold", ev.color)}>{ev.count}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="border-2 border-dashed border-white/10 rounded-lg p-3 flex flex-col items-center gap-1 cursor-pointer hover:border-purple-500/30 transition-colors">
                  <Upload className="w-4 h-4 text-slate-600" />
                  <span className="text-[10px] font-mono text-slate-600">Arrastar ou clicar para upload</span>
                </div>
              </div>
            </Card>

            {/* IA Forense */}
            <Card>
              <div className="flex items-center gap-2 mb-3">
                <Bot className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-mono font-semibold text-white">IA FORENSE</span>
                <Badge variant="blue">Score {selected.iaScore}</Badge>
              </div>
              <div className="space-y-2">
                {IA_DETECTIONS.map((det, i) => (
                  <div key={i} className="p-2 glass rounded-lg border border-white/5">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className={cn("text-[11px] font-mono font-semibold", det.color)}>{det.tipo}</span>
                      <span className={cn("text-[10px] font-mono font-bold", det.color)}>{det.conf}%</span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-1 mb-1">
                      <div className="h-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500" style={{ width: `${det.conf}%` }} />
                    </div>
                    <span className="text-[9px] font-mono text-slate-600">{det.lok}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Findings */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <BarChart2 className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">ACHADOS — {selected.id}</span>
            </div>
            <div className="space-y-2">
              {selected.findings.map((f, i) => (
                <div key={i} className="flex items-center gap-2 p-2 glass rounded-lg border border-white/5">
                  {f.startsWith("⚠") ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                  ) : (
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  <span className="text-[11px] font-mono text-slate-300">{f}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex items-center gap-3">
              <button className="flex-1 py-2 bg-purple-700 hover:bg-purple-800 text-white text-xs font-mono rounded-lg transition-colors flex items-center justify-center gap-2">
                <FileSearch className="w-3.5 h-3.5" />
                Gerar Laudo
              </button>
              <button className="flex-1 py-2 glass border border-white/10 text-slate-300 text-xs font-mono rounded-lg hover:bg-white/5 transition-colors flex items-center justify-center gap-2">
                <Lock className="w-3.5 h-3.5" />
                Assinar ICP
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
