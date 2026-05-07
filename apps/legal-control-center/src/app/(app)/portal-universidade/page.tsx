"use client";
import { motion } from "framer-motion";
import {
  GraduationCap, BookOpen, FlaskConical, Globe, Bot,
  FileText, Users, Award, TrendingUp, Zap, Database,
  BarChart2, Star, Play,
} from "lucide-react";
import { Card, KpiCard, Badge } from "@/components/ui";
import { cn } from "@/lib/utils";

const COURSES = [
  { id: "EDU-001", title: "Engenharia Legal & Construção",      area: "Jurídico",     enrolled: 342, rating: 4.9, level: "Avançado",    icon: "⚖️" },
  { id: "EDU-002", title: "Perícias de Engenharia Civil",       area: "Perícias",     enrolled: 218, rating: 4.8, level: "Especialização",icon: "🔬" },
  { id: "EDU-003", title: "Arbitragem em Contratos de Obra",    area: "Arbitragem",   enrolled: 154, rating: 4.7, level: "Avançado",    icon: "⚖️" },
  { id: "EDU-004", title: "Compliance ESG e SST para Obras",    area: "Compliance",   enrolled: 289, rating: 4.6, level: "Intermediário",icon: "🌱" },
  { id: "EDU-005", title: "Smart Contracts e ICP-Brasil",       area: "Tecnologia",   enrolled: 126, rating: 4.8, level: "Avançado",    icon: "🔐" },
  { id: "EDU-006", title: "Gestão de Risco Jurídico em SPEs",   area: "Societário",   enrolled: 97,  rating: 4.5, level: "Avançado",    icon: "🏛️" },
];

const PAPERS = [
  { title: "IA Forense em Patologias Construtivas",       authors: "Sousa, G.; Lima, P.", journal: "ABNT 2025", year: 2025 },
  { title: "Blockchain como Cadeia de Custódia Jurídica", authors: "Costa, M.; Alencar, R.", journal: "FGV Direito", year: 2025 },
  { title: "NR18 e Responsabilidade Objetiva",            authors: "Ferreira, A.",           journal: "TST Review", year: 2024 },
];

const LABS = [
  { name: "Sandbox Jurídico",   desc: "Simule sentenças com IA",         icon: FlaskConical, color: "text-purple-400" },
  { name: "Dataset Público",    desc: "Jurisprudência + contratos",       icon: Database,     color: "text-blue-400"   },
  { name: "IA Educacional",     desc: "Tutor jurídico personalizado",     icon: Bot,          color: "text-emerald-400" },
  { name: "P&D Labs",           desc: "Pesquisa aplicada",                icon: Zap,          color: "text-amber-400"  },
];

export default function PortalUniversidadePage() {
  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">PORTAL UNIVERSIDADES — JURIDICO.TECH ACADEMIA</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">P&D · Jurisprudência · Engenharia Legal · Sandbox IA</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-700 hover:bg-purple-800 text-white text-xs font-mono rounded-lg transition-colors">
          <GraduationCap className="w-3.5 h-3.5" />
          Acessar Academia
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Alunos Ativos"         value={1_284}  trend="up"     color="blue" />
        <KpiCard label="Cursos Disponíveis"    value={42}     trend="up"     color="green" />
        <KpiCard label="Pesquisas P&D"         value={18}     trend="up"     color="amber" />
        <KpiCard label="Parceiras"             value={7}      trend="stable" color="blue" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

        {/* Courses */}
        <div className="xl:col-span-2 space-y-3">
          <h2 className="text-sm font-mono font-semibold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-400" />
            CURSOS & ESPECIALIZAÇÕES
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {COURSES.map((c, i) => (
              <motion.div key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
                <Card className="h-full hover:border-blue-500/30 transition-colors cursor-pointer group">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-2xl">{c.icon}</span>
                    <Badge variant="blue">{c.level}</Badge>
                  </div>
                  <p className="text-[11px] font-mono font-semibold text-slate-200 leading-tight mb-1.5">{c.title}</p>
                  <p className="text-[9px] font-mono text-slate-600 mb-2">{c.area}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <Users className="w-2.5 h-2.5 text-slate-600" />
                      <span className="text-[9px] font-mono text-slate-600">{c.enrolled}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="w-2.5 h-2.5 text-amber-400" />
                      <span className="text-[9px] font-mono text-amber-400 font-bold">{c.rating}</span>
                    </div>
                    <button className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-[9px] font-mono text-blue-400">
                      <Play className="w-2.5 h-2.5" />
                      Acessar
                    </button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Labs */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <FlaskConical className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-mono font-semibold text-white">LABORATÓRIOS VIRTUAIS</span>
            </div>
            <div className="space-y-2">
              {LABS.map(l => (
                <button key={l.name} className="w-full flex items-center gap-3 p-2.5 glass rounded-lg border border-white/5 hover:border-purple-500/30 transition-all group text-left">
                  <l.icon className={cn("w-4 h-4 shrink-0", l.color)} />
                  <div>
                    <p className="text-[11px] font-mono font-semibold text-slate-200 group-hover:text-white transition-colors">{l.name}</p>
                    <p className="text-[9px] font-mono text-slate-600">{l.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* Papers */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-mono font-semibold text-white">ARTIGOS RECENTES</span>
            </div>
            <div className="space-y-2">
              {PAPERS.map(p => (
                <div key={p.title} className="p-2 glass rounded-lg border border-white/5">
                  <p className="text-[10px] font-mono font-semibold text-slate-200 leading-tight mb-0.5">{p.title}</p>
                  <p className="text-[9px] font-mono text-slate-600">{p.authors}</p>
                  <div className="flex items-center justify-between mt-0.5">
                    <span className="text-[9px] font-mono text-blue-400">{p.journal}</span>
                    <span className="text-[9px] font-mono text-slate-600">{p.year}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* P&D Stats */}
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <BarChart2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-semibold text-white">P&D EM NÚMEROS</span>
            </div>
            <div className="space-y-2 text-[11px] font-mono">
              {[
                { l: "Artigos publicados", v: "34", c: "text-blue-400" },
                { l: "Teses orientadas",  v: "12", c: "text-purple-400" },
                { l: "Patentes",          v: "3",  c: "text-amber-400" },
                { l: "Datasets públicos", v: "8",  c: "text-emerald-400" },
              ].map(({ l, v, c }) => (
                <div key={l} className="flex justify-between">
                  <span className="text-slate-500">{l}</span>
                  <span className={cn("font-bold", c)}>{v}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
