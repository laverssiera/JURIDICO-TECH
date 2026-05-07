"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot, X, Send, Sparkles, BookOpen, Scale, FileText,
  AlertTriangle, RefreshCw, ChevronDown, Mic,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "john";
  content: string;
  ts: string;
  type?: "recommendation" | "clause" | "alert" | "decision" | "jurisprudence" | "text";
}

const SEED_MESSAGES: Message[] = [
  {
    id: "1",
    role: "john",
    content: "Olá! Sou o **John Legal**, seu Copilot jurídico IA. Posso analisar contratos, identificar riscos, sugerir cláusulas e recomendar jurisprudência. Como posso ajudar?",
    ts: new Date().toLocaleTimeString("pt-BR"),
    type: "text",
  },
];

const QUICK_ACTIONS = [
  { label: "Analisar risco contrato",  icon: FileText,  query: "Analise o risco do contrato CTR-0441 — Obra SP-330" },
  { label: "Jurisprudência NR18",      icon: BookOpen,  query: "Mostre jurisprudência recente sobre NR18 e responsabilidade civil" },
  { label: "Cláusula arbitragem",      icon: Scale,     query: "Sugira uma cláusula compromissória CCI para contrato de obra" },
  { label: "Alerta OBRA-022",          icon: AlertTriangle, query: "Quais são os riscos jurídicos do embargo OBRA-022?" },
];

const JOHN_RESPONSES: Record<string, string> = {
  default: "Analisando sua solicitação com base na jurisprudência atual e no contexto do sistema LICEU...\n\n**Análise concluída.** Identifiquei 3 pontos críticos que requerem atenção imediata. Recomendo revisar as cláusulas de responsabilidade e notificação. Posso detalhar cada item.",
  risk: "**Análise de Risco — CTR-0441:**\n\n🔴 **Risco Alto:** Embargo ambiental ativo (OBRA-022) pode impactar contrato principal.\n\n🟡 **Risco Médio:** Cláusula 5.2 de rescisão unilateral com prazo abaixo do padrão.\n\n🟢 **Risco Baixo:** Foro de eleição e reajuste INCC aprovados.\n\n**Recomendação:** Protocolar medida cautelar preventiva e rever prazo cláusula 5.2.",
  nr18: "**Jurisprudência NR18 — Responsabilidade Civil:**\n\n📚 **TST — RR-1001-24.2019:** Condenação solidária por acidente - obra não regularizada NR18.\n\n📚 **STJ — REsp 1.234.567:** Dano moral autônomo por descumprimento EPIs.\n\n📚 **TJSP — 0001234-SP:** Responsabilidade construtora por terceirizado.\n\n**Tendência:** Tribunais têm ampliado responsabilização da contratante principal.",
  clausula: "**Cláusula Compromissória CCI — Recomendada:**\n\n`As partes elegem a arbitragem como método exclusivo de resolução de controvérsias, sob o Regulamento da Câmara de Comércio Internacional (CCI), com sede em São Paulo, no idioma português, com 3 árbitros.`\n\n**Score de Risco:** 9.2/10 ✅\n**Compatível com:** NCC Art. 851 + Lei 9.307/96",
  embargo: "**Risco Jurídico OBRA-022 — Embargo:**\n\n🔴 **CRÍTICO:** Auto de Infração IBAMA Nº 2249-SP — Supressão APP irregular.\n\n**Análise:** Identifico vícios formais no auto. TRF-3 precedente favorável (Agravo 5004321-SP).\n\n**Ações Recomendadas:**\n1. Mandado de Segurança preventivo (prazo: 6h)\n2. Recurso Administrativo paralelo\n3. Contratar perícia ambiental ANCHOR urgente\n\n**Probabilidade sucesso liminar:** ~67%",
};

function getJohnResponse(query: string): string {
  const q = query.toLowerCase();
  if (q.includes("ctr-0441") || q.includes("risco contrato")) return JOHN_RESPONSES.risk;
  if (q.includes("nr18") || q.includes("jurisprudência")) return JOHN_RESPONSES.nr18;
  if (q.includes("cláusula") || q.includes("arbitragem")) return JOHN_RESPONSES.clausula;
  if (q.includes("obra-022") || q.includes("embargo")) return JOHN_RESPONSES.embargo;
  return JOHN_RESPONSES.default;
}

function formatMarkdown(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
    .replace(/`(.*?)`/g, '<code class="bg-white/10 px-1 rounded text-blue-300 text-[10px]">$1</code>')
    .replace(/📚|🔴|🟡|🟢|⚠️|✅/g, (m) => `<span>${m}</span>`)
    .split("\n")
    .map(line => `<p class="mb-1 leading-relaxed">${line || "&nbsp;"}</p>`)
    .join("");
}

interface JohnCopilotProps {
  open: boolean;
  onClose: () => void;
}

export default function JohnCopilot({ open, onClose }: JohnCopilotProps) {
  const [messages, setMessages] = useState<Message[]>(SEED_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function send(query?: string) {
    const text = query ?? input.trim();
    if (!text || loading) return;
    setInput("");

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      ts: new Date().toLocaleTimeString("pt-BR"),
    };

    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    setTimeout(() => {
      const johnMsg: Message = {
        id: crypto.randomUUID(),
        role: "john",
        content: getJohnResponse(text),
        ts: new Date().toLocaleTimeString("pt-BR"),
        type: "recommendation",
      };
      setMessages(prev => [...prev, johnMsg]);
      setLoading(false);
    }, 1200);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 400, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="fixed right-0 top-0 h-full w-[360px] z-50 flex flex-col border-l border-white/5 bg-[#090d16] shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-[#0d1117]">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                <Bot className="w-3.5 h-3.5 text-blue-400" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-mono font-bold text-white">JOHN LEGAL</span>
                  <Sparkles className="w-3 h-3 text-blue-400" />
                </div>
                <p className="text-[9px] font-mono text-slate-500">Copilot Jurídico IA · LICEU 6.x</p>
              </div>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick actions */}
          <div className="px-3 py-2 border-b border-white/5 flex gap-1.5 overflow-x-auto">
            {QUICK_ACTIONS.map(a => (
              <button
                key={a.label}
                onClick={() => send(a.query)}
                className="flex items-center gap-1 px-2 py-1 glass rounded-full border border-white/5 text-[9px] font-mono text-slate-400 hover:text-slate-200 hover:border-blue-500/30 whitespace-nowrap transition-all shrink-0"
              >
                <a.icon className="w-2.5 h-2.5" />
                {a.label}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
            {messages.map(msg => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn("flex gap-2", msg.role === "user" ? "flex-row-reverse" : "flex-row")}
              >
                {msg.role === "john" && (
                  <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-3 h-3 text-blue-400" />
                  </div>
                )}
                <div className={cn(
                  "max-w-[85%] rounded-xl px-3 py-2.5 text-[11px] font-mono",
                  msg.role === "user"
                    ? "bg-blue-600/80 text-white rounded-tr-none"
                    : "glass border border-white/5 text-slate-300 rounded-tl-none"
                )}>
                  {msg.role === "john" ? (
                    <div
                      className="leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.content) }}
                    />
                  ) : (
                    <p>{msg.content}</p>
                  )}
                  <div className="text-[8px] font-mono mt-1.5 opacity-50">{msg.ts}</div>
                </div>
              </motion.div>
            ))}

            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2">
                <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center shrink-0">
                  <Bot className="w-3 h-3 text-blue-400" />
                </div>
                <div className="glass border border-white/5 rounded-xl rounded-tl-none px-3 py-2.5 flex items-center gap-2">
                  <RefreshCw className="w-3 h-3 text-blue-400 animate-spin" />
                  <span className="text-[11px] font-mono text-slate-500">Analisando...</span>
                </div>
              </motion.div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-3 py-3 border-t border-white/5 bg-[#0d1117]">
            <div className="flex gap-2">
              <div className="flex-1 flex items-center gap-2 glass border border-white/5 rounded-xl px-3 py-2 focus-within:border-blue-500/30 transition-colors">
                <Bot className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
                  placeholder="Pergunte ao John Legal..."
                  className="flex-1 bg-transparent text-xs font-mono text-slate-300 placeholder-slate-600 outline-none"
                />
                <button className="text-slate-600 hover:text-slate-400 transition-colors">
                  <Mic className="w-3.5 h-3.5" />
                </button>
              </div>
              <button
                onClick={() => send()}
                disabled={!input.trim() || loading}
                className="w-9 h-9 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-xl flex items-center justify-center transition-colors"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
            <p className="text-[8px] font-mono text-slate-700 mt-1.5 text-center">
              John Legal IA · Baseado em jurisprudência e legislação brasileira
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
