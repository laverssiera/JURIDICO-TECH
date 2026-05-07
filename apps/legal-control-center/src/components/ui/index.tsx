// UI atoms reutilizáveis
import { cn } from "@/lib/utils";
import { type ReactNode } from "react";

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("glass rounded-xl p-5", className)}>
      {children}
    </div>
  );
}

export function Badge({ children, variant = "default" }: { children: ReactNode; variant?: "default"|"green"|"amber"|"red"|"blue" }) {
  const v = {
    default: "bg-white/5 text-slate-400 border-white/10",
    green:   "bg-emerald-900/30 text-emerald-400 border-emerald-700/30",
    amber:   "bg-yellow-900/30 text-yellow-400 border-yellow-700/30",
    red:     "bg-red-900/30 text-red-400 border-red-700/30",
    blue:    "bg-blue-900/30 text-blue-400 border-blue-700/30",
  }[variant];
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-mono border", v)}>
      {children}
    </span>
  );
}

export function KpiCard({
  label, value, sub, trend, color = "blue"
}: {
  label: string; value: string | number; sub?: string; trend?: "up"|"down"|"stable"; color?: "blue"|"green"|"amber"|"red";
}) {
  const colors = {
    blue:  "text-blue-400 border-blue-500/20 bg-blue-500/5",
    green: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5",
    amber: "text-amber-400 border-amber-500/20 bg-amber-500/5",
    red:   "text-red-400 border-red-500/20 bg-red-500/5",
  }[color];
  const trendIcon = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";
  const trendColor = trend === "up" ? "text-emerald-400" : trend === "down" ? "text-red-400" : "text-slate-500";

  return (
    <div className={cn("glass rounded-xl p-5 border", colors.split(" ").slice(1).join(" "))}>
      <p className="text-xs font-mono text-slate-500 uppercase tracking-wider mb-2">{label}</p>
      <div className="flex items-end justify-between">
        <span className={cn("text-3xl font-bold font-mono", colors.split(" ")[0])}>{value}</span>
        {trend && <span className={cn("text-lg font-mono", trendColor)}>{trendIcon}</span>}
      </div>
      {sub && <p className="text-xs text-slate-500 mt-1.5">{sub}</p>}
    </div>
  );
}

export function SectionHeader({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-lg font-mono font-bold text-white tracking-wide">{title}</h1>
      {sub && <p className="text-sm text-slate-500 mt-1">{sub}</p>}
    </div>
  );
}

export type RiskLevel = "verde" | "amarelo" | "vermelho" | "preto";

export function RiskBadge({ level }: { level: RiskLevel }) {
  const cfg: Record<RiskLevel, { label: string; cls: string }> = {
    verde:    { label: "VERDE",    cls: "bg-emerald-900/40 text-emerald-400 border-emerald-700/40" },
    amarelo:  { label: "AMARELO",  cls: "bg-yellow-900/40 text-yellow-400 border-yellow-700/40" },
    vermelho: { label: "CRÍTICO",  cls: "bg-red-900/40 text-red-400 border-red-700/40" },
    preto:    { label: "⚠ PRETO",  cls: "bg-gray-950 text-red-300 border-red-900 animate-pulse" },
  };
  const { label, cls } = cfg[level];
  return <span className={cn("px-2 py-0.5 rounded text-xs font-mono font-bold border", cls)}>{label}</span>;
}

export function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span className={cn("inline-block w-2 h-2 rounded-full", ok ? "bg-emerald-400" : "bg-red-400")} />
  );
}

export function Spinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
    </div>
  );
}
