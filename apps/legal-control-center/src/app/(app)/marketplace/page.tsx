"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Store, Search, Star, Bot, FileText, Shield, Scale,
  ClipboardCheck, Gavel, MapPin, TrendingUp, CheckCircle,
  Clock, ArrowRight, Filter, Plus,
} from "lucide-react";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/components/ui";

type ServiceType = "pericia" | "compliance" | "arbitragem" | "laudo" | "due_diligence" | "engenharia_legal";

interface Service {
  id: string;
  title: string;
  type: ServiceType;
  provider: string;
  score: number;
  price: string;
  delivery: string;
  tags: string[];
  risk: RiskLevel;
  status: "disponivel" | "em_execucao" | "concluido";
}

const TYPE_CFG: Record<ServiceType, { label: string; color: string; icon: React.ElementType }> = {
  pericia:         { label: "Perícia",          color: "text-purple-400", icon: Search },
  compliance:      { label: "Compliance",       color: "text-teal-400",   icon: ClipboardCheck },
  arbitragem:      { label: "Arbitragem",       color: "text-amber-400",  icon: Scale },
  laudo:           { label: "Laudo",            color: "text-blue-400",   icon: FileText },
  due_diligence:   { label: "Due Diligence",    color: "text-emerald-400",icon: Shield },
  engenharia_legal:{ label: "Eng. Legal",       color: "text-red-400",    icon: Gavel },
};

const SERVICES: Service[] = [
  { id: "MKT-001", title: "Perícia Estrutural — Laudo ABNT",         type: "pericia",         provider: "ANCHOR Engenharia", score: 9.4, price: "R$ 12.000",  delivery: "15 dias", tags: ["Estrutural","ABNT"], risk: "verde",    status: "disponivel" },
  { id: "MKT-002", title: "Auditoria Compliance NR18/35",            type: "compliance",      provider: "JurisCompliance",  score: 8.8, price: "R$ 8.500",   delivery: "10 dias", tags: ["SST","NR18"],       risk: "verde",    status: "disponivel" },
  { id: "MKT-003", title: "Câmara Arbitral — Obras e Contratos",     type: "arbitragem",      provider: "CCI Brasil",       score: 9.7, price: "R$ 25.000+", delivery: "60-90d",  tags: ["CCI","Urgente"],    risk: "amarelo",  status: "disponivel" },
  { id: "MKT-004", title: "Due Diligence Imobiliária Full",          type: "due_diligence",   provider: "Deloitte Legal",   score: 9.1, price: "R$ 45.000",  delivery: "30 dias", tags: ["M&A","SPE"],        risk: "verde",    status: "em_execucao" },
  { id: "MKT-005", title: "Laudo Patologia Edificações",             type: "laudo",           provider: "LabForense SP",    score: 8.5, price: "R$ 5.000",   delivery: "7 dias",  tags: ["Patologia","SP"],   risk: "verde",    status: "disponivel" },
  { id: "MKT-006", title: "Engenharia Legal — Revisão Contratual",   type: "engenharia_legal",provider: "TechLegal Assoc.", score: 8.9, price: "R$ 18.000",  delivery: "20 dias", tags: ["Contratos","IA"],   risk: "verde",    status: "concluido" },
];

const JOURNEY = [
  { step: "Cliente", icon: Store,          desc: "Solicita serviço" },
  { step: "John qualifica", icon: Bot,     desc: "IA avalia e recomenda" },
  { step: "Proposta", icon: FileText,      desc: "Fornecedor responde" },
  { step: "Contrato", icon: Shield,        desc: "Smart Contract ICP" },
  { step: "Execução", icon: CheckCircle,   desc: "Acompanhamento RT" },
  { step: "Pagamento", icon: TrendingUp,   desc: "Escrow blockchain" },
  { step: "Relatório", icon: Star,         desc: "Score e avaliação" },
];

export default function MarketplacePage() {
  const [filter, setFilter] = useState<ServiceType | "all">("all");
  const [query, setQuery] = useState("");

  const filtered = SERVICES.filter(s =>
    (filter === "all" || s.type === filter) &&
    (query === "" || s.title.toLowerCase().includes(query.toLowerCase()) || s.provider.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">MARKETPLACE JURÍDICO</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Perícias · Compliance · Arbitragem · Due Diligence · Laudos</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-mono rounded-lg transition-colors">
          <Plus className="w-3.5 h-3.5" />
          Publicar Serviço
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Serviços Ativos"    value={124}    trend="up"     color="blue" />
        <KpiCard label="Transações (30d)"   value="R$ 2,8M" trend="up"   color="green" />
        <KpiCard label="Prestadores"        value={47}     trend="up"     color="amber" />
        <KpiCard label="Score Médio"        value="9.1"    trend="up"     color="green" />
      </div>

      {/* Journey */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <ArrowRight className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-mono font-semibold text-white">JORNADA DO SERVIÇO</span>
        </div>
        <div className="flex items-center gap-1 overflow-x-auto">
          {JOURNEY.map((j, i) => (
            <div key={j.step} className="flex items-center shrink-0">
              <div className="flex flex-col items-center gap-1 px-3 py-2 glass rounded-lg border border-white/5 min-w-[90px]">
                <j.icon className="w-4 h-4 text-blue-400" />
                <span className="text-[9px] font-mono font-bold text-slate-300 text-center">{j.step}</span>
                <span className="text-[8px] font-mono text-slate-600 text-center">{j.desc}</span>
              </div>
              {i < JOURNEY.length - 1 && <ArrowRight className="w-3 h-3 text-slate-700 mx-1 shrink-0" />}
            </div>
          ))}
        </div>
      </Card>

      {/* Search + Filters */}
      <div className="flex gap-3 items-center">
        <div className="flex-1 flex items-center gap-2 glass rounded-lg border border-white/5 px-3 py-2">
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Buscar serviços jurídicos..."
            className="flex-1 bg-transparent text-xs font-mono text-slate-300 placeholder-slate-600 outline-none"
          />
        </div>
        <div className="flex gap-1 p-1 glass rounded-lg border border-white/5">
          <button onClick={() => setFilter("all")} className={cn("px-2 py-1 rounded text-[10px] font-mono transition-all", filter === "all" ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-300")}>
            TODOS
          </button>
          {(Object.keys(TYPE_CFG) as ServiceType[]).map(t => (
            <button key={t} onClick={() => setFilter(t)} className={cn("px-2 py-1 rounded text-[10px] font-mono transition-all", filter === t ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-300")}>
              {TYPE_CFG[t].label.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Service cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((s, i) => {
          const TypeIcon = TYPE_CFG[s.type].icon;
          return (
            <motion.div key={s.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Card className="h-full flex flex-col gap-3 hover:border-blue-500/20 transition-colors cursor-pointer group">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <TypeIcon className={cn("w-4 h-4 shrink-0", TYPE_CFG[s.type].color)} />
                    <span className={cn("text-[10px] font-mono font-bold", TYPE_CFG[s.type].color)}>{TYPE_CFG[s.type].label}</span>
                  </div>
                  <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded border",
                    s.status === "disponivel" ? "bg-emerald-900/30 text-emerald-400 border-emerald-700/30" :
                    s.status === "em_execucao" ? "bg-amber-900/30 text-amber-400 border-amber-700/30" :
                    "bg-slate-900/30 text-slate-500 border-slate-700/30"
                  )}>
                    {s.status === "disponivel" ? "DISPONÍVEL" : s.status === "em_execucao" ? "EM EXECUÇÃO" : "CONCLUÍDO"}
                  </span>
                </div>

                <div className="flex-1">
                  <p className="text-[12px] font-mono font-semibold text-slate-200 leading-tight mb-1">{s.title}</p>
                  <p className="text-[10px] font-mono text-slate-500 mb-2">{s.provider}</p>
                  <div className="flex flex-wrap gap-1">
                    {s.tags.map(t => (
                      <span key={t} className="px-1.5 py-0.5 rounded text-[8px] font-mono bg-white/5 text-slate-500 border border-white/5">{t}</span>
                    ))}
                  </div>
                </div>

                <div className="flex items-end justify-between pt-2 border-t border-white/5">
                  <div>
                    <div className="text-sm font-bold font-mono text-emerald-400">{s.price}</div>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Clock className="w-2.5 h-2.5 text-slate-600" />
                      <span className="text-[9px] font-mono text-slate-600">{s.delivery}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-1">
                      <Star className="w-2.5 h-2.5 text-amber-400" />
                      <span className="text-[11px] font-mono font-bold text-amber-400">{s.score}</span>
                    </div>
                    {s.status === "disponivel" && (
                      <button className="px-2.5 py-1 bg-blue-600/80 hover:bg-blue-600 text-white text-[9px] font-mono rounded transition-colors">
                        Contratar
                      </button>
                    )}
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
