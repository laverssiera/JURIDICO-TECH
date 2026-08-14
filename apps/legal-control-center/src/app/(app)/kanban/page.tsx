"use client";
import { useState } from "react";
import { motion, Reorder } from "framer-motion";
import {
  Plus, Filter, Bot, Clock, AlertTriangle, CheckCircle,
  FileText, Building2, Gavel, Search, Shield, Store,
  ChevronDown, MoreHorizontal, Zap, TrendingUp,
} from "lucide-react";
import { Badge, RiskBadge, Card } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

type CardType = "obra" | "processo" | "contrato" | "fornecedor" | "arbitragem" | "pericia" | "compliance";
type ColId = "novo" | "analise" | "compliance" | "aprovacao" | "execucao" | "monitoramento" | "concluido";

interface KanbanCard {
  id: string;
  title: string;
  tipo: CardType;
  risk: RiskLevel;
  sla: string;
  responsible: string;
  aiScore: number;
  tags: string[];
  daysOpen: number;
}

const COLS: { id: ColId; label: string; color: string }[] = [
  { id: "novo",          label: "NOVO",           color: "border-slate-600" },
  { id: "analise",       label: "ANÁLISE",        color: "border-blue-500/40" },
  { id: "compliance",    label: "COMPLIANCE",     color: "border-amber-500/40" },
  { id: "aprovacao",     label: "APROVAÇÃO",      color: "border-purple-500/40" },
  { id: "execucao",      label: "EXECUÇÃO",       color: "border-cyan-500/40" },
  { id: "monitoramento", label: "MONITORAMENTO",  color: "border-teal-500/40" },
  { id: "concluido",     label: "CONCLUÍDO",      color: "border-emerald-500/40" },
];

const TIPO_ICON: Record<CardType, React.ElementType> = {
  obra:       Building2,
  processo:   Gavel,
  contrato:   FileText,
  fornecedor: Store,
  arbitragem: Gavel,
  pericia:    Search,
  compliance: Shield,
};

const TIPO_COLOR: Record<CardType, string> = {
  obra:       "text-cyan-400",
  processo:   "text-red-400",
  contrato:   "text-blue-400",
  fornecedor: "text-emerald-400",
  arbitragem: "text-amber-400",
  pericia:    "text-purple-400",
  compliance: "text-teal-400",
};

const INIT_CARDS: Record<ColId, KanbanCard[]> = {
  novo: [
    { id: "c1", title: "Contrato Obra SP-330", tipo: "contrato", risk: "vermelho", sla: "3d", responsible: "Dr. Alencar", aiScore: 42, tags: ["NR18","Ambiental"], daysOpen: 1 },
    { id: "c2", title: "Homologação FORN-88",  tipo: "fornecedor", risk: "amarelo", sla: "5d", responsible: "Compliance", aiScore: 67, tags: ["SST"], daysOpen: 2 },
  ],
  analise: [
    { id: "c3", title: "Processo Trabalhista #1842", tipo: "processo", risk: "vermelho", sla: "2d", responsible: "Dra. Lima", aiScore: 28, tags: ["Litígio","NR18"], daysOpen: 5 },
    { id: "c4", title: "Perícia ANCHOR #09",         tipo: "pericia",  risk: "verde",    sla: "7d", responsible: "Eng. Sousa", aiScore: 88, tags: ["Estrutural"], daysOpen: 3 },
    { id: "c5", title: "SPE-44 Due Diligence",       tipo: "obra",     risk: "amarelo",  sla: "4d", responsible: "Dr. Costa", aiScore: 71, tags: ["SPE","M&A"], daysOpen: 4 },
  ],
  compliance: [
    { id: "c6", title: "Auditoria ESG Meridian",  tipo: "compliance", risk: "amarelo", sla: "10d", responsible: "ESG Team", aiScore: 59, tags: ["ESG","SST"], daysOpen: 8 },
    { id: "c7", title: "Revisão NR35 Torre Norte",tipo: "obra",       risk: "verde",   sla: "6d",  responsible: "SST",      aiScore: 82, tags: ["NR35"], daysOpen: 2 },
  ],
  aprovacao: [
    { id: "c8", title: "Arbitragem CEA-2024",     tipo: "arbitragem", risk: "vermelho", sla: "1d", responsible: "Dr. Alencar", aiScore: 35, tags: ["Câmara","Urgente"], daysOpen: 12 },
    { id: "c9", title: "Addendum Contrato Parque",tipo: "contrato",   risk: "amarelo",  sla: "3d", responsible: "Jurídico",    aiScore: 74, tags: ["Revisão"], daysOpen: 6 },
  ],
  execucao: [
    { id: "c10", title: "Obra Edifício Arco",       tipo: "obra",     risk: "verde",   sla: "30d", responsible: "Eng. Marques", aiScore: 91, tags: ["ativa"], daysOpen: 20 },
    { id: "c11", title: "Contrato Fornec. Engepavi",tipo: "fornecedor",risk: "verde",   sla: "60d", responsible: "Contratos",   aiScore: 85, tags: ["vigente"], daysOpen: 45 },
  ],
  monitoramento: [
    { id: "c12", title: "Processo Ambiental #114",  tipo: "processo",  risk: "amarelo", sla: "Contínuo", responsible: "Dra. Lima",  aiScore: 62, tags: ["IBAMA"], daysOpen: 30 },
  ],
  concluido: [
    { id: "c13", title: "Laudo ANCHOR #07",         tipo: "pericia",   risk: "verde",   sla: "—", responsible: "Eng. Sousa",  aiScore: 95, tags: ["concluído"], daysOpen: 0 },
    { id: "c14", title: "Contrato FORN-12 Encerrado",tipo: "fornecedor",risk: "verde",  sla: "—", responsible: "Contratos",   aiScore: 90, tags: ["encerrado"], daysOpen: 0 },
  ],
};

function KCard({ card, colColor }: { card: KanbanCard; colColor: string }) {
  const Icon = TIPO_ICON[card.tipo];
  const typeColor = TIPO_COLOR[card.tipo];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-3 border border-white/5 hover:border-white/10 cursor-grab active:cursor-grabbing group transition-all hover:shadow-lg"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          <Icon className={cn("w-3.5 h-3.5 shrink-0", typeColor)} />
          <span className="text-[11px] font-mono font-semibold text-slate-200 leading-tight line-clamp-2">{card.title}</span>
        </div>
        <button className="opacity-0 group-hover:opacity-100 transition-opacity">
          <MoreHorizontal className="w-3.5 h-3.5 text-slate-500" />
        </button>
      </div>

      <div className="flex flex-wrap gap-1 mb-2">
        {card.tags.map(t => (
          <span key={t} className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-white/5 text-slate-500 border border-white/5">{t}</span>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <RiskBadge level={card.risk} />
        <div className="flex items-center gap-2">
          {/* AI Score */}
          <div className="flex items-center gap-1">
            <Bot className="w-3 h-3 text-blue-400" />
            <span className={`text-[10px] font-mono font-bold ${
              card.aiScore >= 80 ? "text-emerald-400" : card.aiScore >= 60 ? "text-amber-400" : "text-red-400"
            }`}>{card.aiScore}</span>
          </div>
          {/* SLA */}
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-600" />
            <span className="text-[10px] font-mono text-slate-500">{card.sla}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
        <span className="text-[9px] font-mono text-slate-600">{card.responsible}</span>
        {card.daysOpen > 0 && (
          <span className={`text-[9px] font-mono ${card.daysOpen > 10 ? "text-amber-400" : "text-slate-600"}`}>
            {card.daysOpen}d aberto
          </span>
        )}
      </div>
    </motion.div>
  );
}

export default function KanbanPage() {
  const [cards, setCards] = useState(INIT_CARDS);
  const [filter, setFilter] = useState<CardType | "all">("all");

  const total = Object.values(cards).flat().length;
  const critical = Object.values(cards).flat().filter(c => c.risk === "vermelho" || c.risk === "preto").length;

  return (
    <div className="p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">KANBAN JURÍDICO GLOBAL</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">
            {total} demandas · <span className="text-red-400">{critical} críticas</span> · IA ativa
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter tabs */}
          <div className="flex items-center gap-1 p-1 glass rounded-lg border border-white/5">
            {(["all","obra","processo","contrato","pericia","arbitragem","compliance"] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  "px-2 py-1 rounded text-[10px] font-mono transition-all",
                  filter === f ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-300"
                )}
              >
                {f === "all" ? "TODOS" : f.toUpperCase()}
              </button>
            ))}
          </div>

          <button className="flex items-center gap-1.5 px-3 py-1.5 glass rounded-lg border border-white/5 text-xs font-mono text-slate-400 hover:text-slate-200 transition-colors">
            <Plus className="w-3.5 h-3.5" />
            Nova Demanda
          </button>
        </div>
      </div>

      {/* Board */}
      <div className="flex-1 overflow-x-auto">
        <div className="flex gap-4 h-full min-w-max pb-4">
          {COLS.map(col => {
            const colCards = cards[col.id].filter(c => filter === "all" || c.tipo === filter);
            return (
              <div key={col.id} className="w-[220px] flex flex-col">
                {/* Column header */}
                <div className={cn("flex items-center justify-between px-3 py-2 rounded-t-lg border-t-2 bg-white/3", col.color)}>
                  <span className="text-[10px] font-mono font-bold text-slate-300 tracking-wider">{col.label}</span>
                  <span className="text-[10px] font-mono text-slate-600 bg-white/5 px-1.5 py-0.5 rounded">
                    {colCards.length}
                  </span>
                </div>

                {/* Cards */}
                <div className="flex-1 overflow-y-auto space-y-2 p-2 bg-white/2 rounded-b-lg border border-t-0 border-white/5 min-h-[400px]">
                  {colCards.map(c => (
                    <KCard key={c.id} card={c} colColor={col.color} />
                  ))}
                  {colCards.length === 0 && (
                    <div className="flex items-center justify-center h-20 text-[10px] font-mono text-slate-700 border-2 border-dashed border-white/5 rounded-lg">
                      vazio
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom stats */}
      <div className="mt-4 flex items-center gap-6 pt-3 border-t border-white/5">
        {[
          { label: "SLA Vencendo", val: "4", color: "text-amber-400", icon: Clock },
          { label: "AI Insights",  val: "12", color: "text-blue-400",  icon: Bot },
          { label: "Urgentes",     val: String(critical), color: "text-red-400", icon: AlertTriangle },
          { label: "Concluídos",   val: String(cards.concluido.length), color: "text-emerald-400", icon: CheckCircle },
        ].map(({ label, val, color, icon: Icon }) => (
          <div key={label} className="flex items-center gap-1.5">
            <Icon className={cn("w-3.5 h-3.5", color)} />
            <span className={cn("text-sm font-mono font-bold", color)}>{val}</span>
            <span className="text-[10px] font-mono text-slate-600">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
