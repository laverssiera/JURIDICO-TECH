"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { BadgeCheck, CircleAlert, Clock3, RefreshCw, ShieldCheck, TimerReset } from "lucide-react";

import { api } from "@/lib/api";
import { Card, KpiCard } from "@/components/ui";

interface OutboxEvent {
  id: string;
  subject: string;
  payload_json: string;
  status: string;
  attempts: number;
  created_at: string;
  published_at: string | null;
  last_error: string | null;
}

const STATUS_OPTIONS = ["all", "pending", "published", "retry"] as const;
type StatusFilter = (typeof STATUS_OPTIONS)[number];

export default function AuditoriaPage() {
  const [status, setStatus] = useState<StatusFilter>("all");
  const [loading, setLoading] = useState(false);
  const [flushing, setFlushing] = useState(false);
  const [events, setEvents] = useState<OutboxEvent[]>([]);

  const load = async () => {
    try {
      setLoading(true);
      const qs = status === "all" ? "" : `?status=${status}`;
      const data = await api.get<{ items: OutboxEvent[]; total: number }>(`/events/outbox${qs}`);
      setEvents(data.items ?? []);
    } catch {
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const flush = async () => {
    try {
      setFlushing(true);
      await api.post("/events/outbox/flush", { limit: 200 });
      await load();
    } finally {
      setFlushing(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 12000);
    return () => clearInterval(id);
  }, [status]);

  const metrics = useMemo(() => {
    const pending = events.filter((e) => e.status === "pending").length;
    const published = events.filter((e) => e.status === "published").length;
    const retry = events.filter((e) => e.status === "retry").length;
    return { total: events.length, pending, published, retry };
  }, [events]);

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-mono font-bold text-white tracking-wider">AUDITORIA DE EVENTOS</h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">Outbox transacional · War Room · John Legal</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 text-xs font-mono rounded-lg border border-white/10 text-slate-300 hover:bg-white/5 disabled:opacity-40"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Atualizar
          </button>
          <button
            onClick={flush}
            disabled={flushing}
            className="flex items-center gap-2 px-3 py-2 text-xs font-mono rounded-lg border border-amber-600/40 text-amber-300 hover:bg-amber-900/20 disabled:opacity-40"
          >
            <TimerReset className="w-3.5 h-3.5" />
            Flush Outbox
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard label="Total Eventos" value={metrics.total} trend="stable" color="blue" />
        <KpiCard label="Pendentes" value={metrics.pending} trend="stable" color="amber" />
        <KpiCard label="Publicados" value={metrics.published} trend="up" color="green" />
        <KpiCard label="Retry" value={metrics.retry} trend="down" color="red" />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt}
            onClick={() => setStatus(opt)}
            className={`px-3 py-1.5 rounded-full text-xs font-mono border transition-colors ${
              status === opt
                ? "bg-blue-900/30 border-blue-500/40 text-blue-300"
                : "bg-white/0 border-white/10 text-slate-400 hover:text-slate-200"
            }`}
          >
            {opt.toUpperCase()}
          </button>
        ))}
      </div>

      <Card>
        <div className="overflow-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="text-slate-500 border-b border-white/10">
                <th className="py-2 pr-3">Status</th>
                <th className="py-2 pr-3">Subject</th>
                <th className="py-2 pr-3">Payload</th>
                <th className="py-2 pr-3">Tentativas</th>
                <th className="py-2 pr-3">Criado em</th>
                <th className="py-2 pr-3">Publicado em</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event, idx) => (
                <motion.tr
                  key={event.id}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.02 }}
                  className="border-b border-white/5 align-top"
                >
                  <td className="py-2 pr-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border ${
                        event.status === "published"
                          ? "border-emerald-500/40 text-emerald-400"
                          : event.status === "pending"
                            ? "border-amber-500/40 text-amber-400"
                            : "border-red-500/40 text-red-400"
                      }`}
                    >
                      {event.status === "published" ? <BadgeCheck className="w-3 h-3" /> : <CircleAlert className="w-3 h-3" />}
                      {event.status}
                    </span>
                  </td>
                  <td className="py-2 pr-3 text-slate-200">{event.subject}</td>
                  <td className="py-2 pr-3 text-slate-400 max-w-[420px]">
                    <div className="line-clamp-2 break-all">{event.payload_json}</div>
                    {event.last_error && <div className="text-red-400 mt-1">erro: {event.last_error}</div>}
                  </td>
                  <td className="py-2 pr-3 text-slate-300">{event.attempts}</td>
                  <td className="py-2 pr-3 text-slate-500">{new Date(event.created_at).toLocaleString("pt-BR")}</td>
                  <td className="py-2 pr-3 text-slate-500">{event.published_at ? new Date(event.published_at).toLocaleString("pt-BR") : "-"}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
          {!events.length && (
            <div className="py-8 text-center text-slate-500 font-mono text-xs">Nenhum evento encontrado para o filtro atual.</div>
          )}
        </div>
      </Card>

      <div className="text-[11px] font-mono text-slate-500 flex items-center gap-2">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        Trilha auditável de ações operacionais e interações do Copilot.
        <Clock3 className="w-3.5 h-3.5 text-blue-400 ml-2" />
        Atualização automática a cada 12s.
      </div>
    </div>
  );
}
