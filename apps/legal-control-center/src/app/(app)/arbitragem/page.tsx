"use client";
import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Scale, Calendar, Users, FileText, Clock, Globe, TrendingUp,
  CheckCircle, AlertTriangle, MessageSquare, Download, Gavel,
} from "lucide-react";
import { api } from "@/lib/api";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

const CASES = [
  { id: "ARB-001", title: "JT Engenharia vs Construtora Alpha", camara: "CCI Brasil", valor: "R$ 15,2M", status: "Audiência", risk: "vermelho" as RiskLevel, data: "14/05/2025", fase: "Instrução" },
  { id: "ARB-002", title: "SPE-44 vs Fundo Imobiliário AB",    camara: "CAM-CCBC",   valor: "R$ 8,7M",  status: "Perito",   risk: "amarelo"  as RiskLevel, data: "20/05/2025", fase: "Pericial" },
  { id: "ARB-003", title: "OBRA-031 — Revisão Contratual",     camara: "FGV RJ",      valor: "R$ 3,1M",  status: "Sentence", risk: "verde"    as RiskLevel, data: "30/05/2025", fase: "Sentença" },
  { id: "ARB-004", title: "Engepavi vs JT Engenharia",         camara: "CCI Brasil",  valor: "R$ 2,0M",  status: "Mediação", risk: "amarelo"  as RiskLevel, data: "10/06/2025", fase: "Mediação" },
];

const TIMELINE = [
  { fase: "Pré-Arbitral", desc: "Cláusula compromissória · Notificação", done: true },
  { fase: "Instalação",   desc: "Escolha árbitros · Ata missão",          done: true },
  { fase: "Instrução",    desc: "Memorial · Provas · Peritos",             done: false, current: true },
  { fase: "Oral",         desc: "Audiência de instrução",                  done: false },
  { fase: "Sentença",     desc: "Laudo arbitral · Execução",               done: false },
];

export default function ArbitragemPage() {
  type ArbitrationEvent = {
    id: string;
    case_id: string;
    event_type: string;
    description: string;
    created_at: string;
  };
  type ArbitrationCaseApi = {
    id: string;
    case_number: string;
    title: string;
    status: string;
    parties_json: string;
    award_amount: number | null;
    created_at: string;
    events: ArbitrationEvent[];
  };

  const [cases, setCases] = useState(CASES);
  const [selectedId, setSelectedId] = useState<string>(CASES[0].id);

  useEffect(() => {
    let cancelled = false;

    const mapRisk = (status: string): RiskLevel => {
      if (status === "open") return "vermelho";
      if (status === "hearing") return "amarelo";
      if (status === "award" || status === "closed") return "verde";
      return "amarelo";
    };

    const mapStatusLabel = (status: string) => {
      if (status === "open") return "Audiência";
      if (status === "hearing") return "Instrução";
      if (status === "award") return "Sentence";
      if (status === "closed") return "Concluído";
      return "Mediação";
    };

    const mapFase = (status: string) => {
      if (status === "open") return "Instalação";
      if (status === "hearing") return "Instrução";
      if (status === "award") return "Sentença";
      if (status === "closed") return "Pós-Laudo";
      return "Mediação";
    };

    const load = async () => {
      try {
        const data = await api.get<{ total: number; items: ArbitrationCaseApi[] }>("/arbitration/");
        if (cancelled || !data.items.length) return;

        const normalized = data.items.map((c) => ({
          id: c.id,
          title: c.title,
          camara: "Arbitragem LICEU",
          valor: c.award_amount ? `R$ ${Math.round(c.award_amount).toLocaleString("pt-BR")}` : "N/A",
          status: mapStatusLabel(c.status),
          risk: mapRisk(c.status),
          data: new Date(c.created_at).toLocaleDateString("pt-BR"),
          fase: mapFase(c.status),
          events: c.events,
        }));

        setCases(normalized);
        setSelectedId(normalized[0].id);
      } catch {
        // fallback mock
      }
    };

    load();
    const id = setInterval(load, 12000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const selectedCase = useMemo(() => cases.find((c) => c.id === selectedId) ?? cases[0], [cases, selectedId]);

  const timelineDynamic = useMemo(() => {
    const events = (selectedCase as { events?: ArbitrationEvent[] } | undefined)?.events ?? [];
    if (!events.length) return TIMELINE;

    const ordered = [...events].sort((a, b) => a.created_at.localeCompare(b.created_at));
    return ordered.slice(-5).map((e, idx) => ({
      fase: e.event_type.replace(/_/g, " ").toUpperCase(),
      desc: e.description,
      done: idx < ordered.length - 1,
      current: idx === ordered.length - 1,
    }));
  }, [selectedCase]);

  const activeCases = cases.length;
  const totalDispute = cases.reduce((acc, c) => {
    const numeric = Number(String(c.valor).replace(/[^\d]/g, ""));
    return acc + (Number.isFinite(numeric) ? numeric : 0);
  }, 0);

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">ARBITRAGEM</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">CCI · CAM-CCBC · FGV · Câmaras Nacionais</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-amber-700 hover:bg-amber-800 text-white text-xs font-mono rounded-lg">
          <Scale className="w-3.5 h-3.5" />
          Nova Demanda
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Casos Ativos"       value={activeCases} trend="up"     color="amber" />
        <KpiCard label="Valor em Disputa"   value={`R$ ${Math.round(totalDispute / 1_000_000)}M`} trend="stable" color="red" />
        <KpiCard label="Câmaras"            value={1} trend="stable" color="blue" />
        <KpiCard label="Laudos Favoráveis"  value={activeCases ? `${Math.round((cases.filter((c) => c.status === "Sentence" || c.status === "Concluído").length / activeCases) * 100)}%` : "0%"} trend="up" color="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        {/* Cases */}
        <div className="xl:col-span-2 space-y-3">
          {cases.map((c, i) => (
            <motion.div key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07 }}>
              <Card className={cn(selectedId === c.id ? "border-amber-500/40" : "")}> 
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Gavel className="w-4 h-4 text-amber-400 shrink-0" />
                      <span className="text-[11px] font-mono font-bold text-slate-400">{c.id}</span>
                      <Badge variant="amber">{c.camara}</Badge>
                    </div>
                    <p className="text-sm font-semibold text-slate-200 mb-2">{c.title}</p>
                    <div className="flex items-center gap-4 text-[10px] font-mono text-slate-600">
                      <span className="flex items-center gap-1"><TrendingUp className="w-3 h-3 text-emerald-400" />{c.valor}</span>
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{c.data}</span>
                      <span className="flex items-center gap-1"><Scale className="w-3 h-3" />{c.fase}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <RiskBadge level={c.risk} />
                    <span className={cn("text-[9px] font-mono px-2 py-0.5 rounded border",
                      c.status === "Audiência" ? "bg-red-900/30 text-red-400 border-red-700/30" :
                      c.status === "Sentence"  ? "bg-emerald-900/30 text-emerald-400 border-emerald-700/30" :
                      "bg-amber-900/30 text-amber-400 border-amber-700/30"
                    )}>
                      {c.status}
                    </span>
                    <button
                      onClick={() => setSelectedId(c.id)}
                      className="text-[9px] font-mono text-blue-400 hover:text-blue-300"
                    >
                      Ver timeline
                    </button>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Timeline */}
        <div className="space-y-4">
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">FASES ARBITRAIS</span>
            </div>
            <div className="space-y-3">
              {timelineDynamic.map((t, i) => (
                <div key={t.fase} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className={cn("w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0",
                      t.done    ? "border-emerald-500 bg-emerald-900/30" :
                      t.current ? "border-amber-500 bg-amber-900/30 animate-pulse" :
                      "border-white/10 bg-white/5"
                    )}>
                      {t.done ? <CheckCircle className="w-3 h-3 text-emerald-400" /> :
                        t.current ? <span className="w-2 h-2 rounded-full bg-amber-400" /> :
                        <span className="w-2 h-2 rounded-full bg-slate-700" />}
                    </div>
                    {i < TIMELINE.length - 1 && <div className="w-px flex-1 mt-1" style={{ background: t.done ? "#10b981" : "rgba(255,255,255,0.05)" }} />}
                  </div>
                  <div className="pb-3">
                    <p className={cn("text-xs font-mono font-semibold",
                      t.done ? "text-emerald-400" : t.current ? "text-amber-400" : "text-slate-600"
                    )}>{t.fase}</p>
                    <p className="text-[10px] font-mono text-slate-600 mt-0.5">{t.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-mono font-semibold text-white">PRÓXIMAS AUDIÊNCIAS</span>
            </div>
            <div className="space-y-2">
              {[
                { id: "ARB-001", txt: "Audiência de Instrução CCI", data: "14/05 · 14h00", local: "SP" },
                { id: "ARB-002", txt: "Apresentação Laudo Pericial", data: "20/05 · 10h00", local: "RJ" },
              ].map(a => (
                <div key={a.id} className="p-2.5 glass rounded-lg border border-white/5">
                  <p className="text-[11px] font-mono font-semibold text-slate-200">{a.txt}</p>
                  <p className="text-[9px] font-mono text-slate-600 mt-0.5">{a.id} · {a.data} · {a.local}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
