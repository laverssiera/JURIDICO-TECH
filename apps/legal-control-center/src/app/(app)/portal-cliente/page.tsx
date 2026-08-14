"use client";
import { motion } from "framer-motion";
import {
  Building2, FileText, Gavel, HardHat, Shield, Download,
  CheckCircle, Clock, AlertTriangle, TrendingUp, MapPin,
  Camera, Star,
} from "lucide-react";
import { Card, KpiCard, Badge, RiskBadge } from "@/components/ui";
import { cn } from "@/lib/utils";

const OBRAS = [
  { id: "OBRA-022", nome: "Ponte SP-330",          status: "Embargada",   prog: 45, risk: "preto"    as const, loc: "Itatiba, SP" },
  { id: "OBRA-031", nome: "Edifício Arco",          status: "Em Execução", prog: 67, risk: "verde"    as const, loc: "Brasília, DF" },
  { id: "OBRA-067", nome: "Torre Norte",            status: "Em Execução", prog: 82, risk: "amarelo"  as const, loc: "São Carlos, SP" },
  { id: "SPE-044",  nome: "Parque Industrial PR",   status: "Em Análise",  prog: 12, risk: "verde"    as const, loc: "Londrina, PR" },
];

const CONTRATOS = [
  { id: "CTR-0441", nome: "Obra SP-330",          value: "R$ 48,2M", expires: "Dez/26", ok: false },
  { id: "CTR-0412", nome: "SPE Parque Industrial", value: "R$ 120M",  expires: "Jan/30", ok: true },
  { id: "CTR-0102", nome: "Torre Norte",           value: "R$ 2,4M",  expires: "Mar/27", ok: true },
];

const DOCS = [
  { nome: "Memorial Descritivo OBRA-031",    tipo: "PDF",  data: "03/05",  ok: true },
  { nome: "Laudo Perícia ANCH-09",           tipo: "PDF",  data: "02/05",  ok: true },
  { nome: "Termo de Garantia Edifício Arco", tipo: "PDF",  data: "01/05",  ok: true },
  { nome: "Contrato CTR-0441",               tipo: "PDF",  data: "15/04",  ok: false },
];

export default function PortalClientePage() {
  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-lg font-bold font-mono text-blue-400">
              JT
            </div>
            <div>
              <h1 className="text-lg font-mono font-bold text-white">PORTAL CLIENTE</h1>
              <p className="text-xs font-mono text-slate-500">JT Construtora · Código: CLI-0012</p>
            </div>
          </div>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass border border-white/10 text-slate-300 text-xs font-mono rounded-lg hover:bg-white/5 transition-colors">
          <Download className="w-3.5 h-3.5" />
          Exportar Relatório
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Obras Ativas"       value={4}       trend="stable" color="blue" />
        <KpiCard label="Contratos"          value={7}       trend="up"     color="green" />
        <KpiCard label="Garantias Vigentes" value={3}       trend="stable" color="amber" />
        <KpiCard label="Processos"          value={2}       trend="down"   color="red" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Obras */}
        <div className="xl:col-span-2 space-y-3">
          <div className="flex items-center gap-2 mb-1">
            <Building2 className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-mono font-semibold text-white">OBRAS MONITORADAS</h2>
          </div>
          {OBRAS.map(o => (
            <motion.div key={o.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Card>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[10px] font-mono text-slate-500">{o.id}</span>
                      <Badge variant={o.risk === "verde" ? "green" : o.risk === "amarelo" ? "amber" : "red"}>
                        {o.status}
                      </Badge>
                    </div>
                    <p className="text-sm font-semibold text-slate-200">{o.nome}</p>
                    <div className="flex items-center gap-1 mt-0.5">
                      <MapPin className="w-2.5 h-2.5 text-slate-600" />
                      <span className="text-[9px] font-mono text-slate-600">{o.loc}</span>
                    </div>
                  </div>
                  <RiskBadge level={o.risk} />
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full bg-white/5 rounded-full h-2">
                      <div className={cn("h-2 rounded-full transition-all", o.risk === "verde" ? "bg-emerald-400" : o.risk === "amarelo" ? "bg-amber-400" : "bg-red-400")}
                        style={{ width: `${o.prog}%` }} />
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold text-slate-400">{o.prog}%</span>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-semibold text-white">CONTRATOS VIGENTES</span>
            </div>
            <div className="space-y-2">
              {CONTRATOS.map(c => (
                <div key={c.id} className="flex items-center gap-2 p-2 glass rounded-lg border border-white/5">
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] font-mono font-semibold text-slate-200 truncate">{c.nome}</p>
                    <p className="text-[9px] font-mono text-slate-600">{c.id} · {c.value} · {c.expires}</p>
                  </div>
                  {c.ok ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />}
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Download className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-mono font-semibold text-white">DOCUMENTOS</span>
            </div>
            <div className="space-y-2">
              {DOCS.map(d => (
                <button key={d.nome} className="w-full flex items-center gap-2 p-2 glass rounded-lg border border-white/5 hover:border-white/10 transition-all text-left group">
                  <FileText className="w-3.5 h-3.5 text-slate-600 group-hover:text-blue-400 shrink-0 transition-colors" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] font-mono text-slate-300 leading-tight truncate">{d.nome}</p>
                    <p className="text-[9px] font-mono text-slate-600">{d.tipo} · {d.data}</p>
                  </div>
                  <Download className="w-3 h-3 text-slate-700 group-hover:text-blue-400 opacity-0 group-hover:opacity-100 shrink-0 transition-all" />
                </button>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Star className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">PATRIMÔNIO DIGITAL</span>
            </div>
            <div className="space-y-2 text-[11px] font-mono">
              {[
                { label: "Valor Total Obras",    val: "R$ 173M",  color: "text-emerald-400" },
                { label: "Garantias",            val: "R$ 24M",   color: "text-blue-400" },
                { label: "Em Disputa",           val: "R$ 17M",   color: "text-red-400" },
                { label: "Provisão Jurídica",    val: "R$ 5,2M",  color: "text-amber-400" },
              ].map(({ label, val, color }) => (
                <div key={label} className="flex items-center justify-between">
                  <span className="text-slate-500">{label}</span>
                  <span className={cn("font-bold", color)}>{val}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
