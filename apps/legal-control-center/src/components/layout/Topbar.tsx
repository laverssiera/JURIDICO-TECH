"use client";
import { Bell, Wifi, WifiOff, Bot } from "lucide-react";
import { useLegalStore } from "@/store/legal";

export default function Topbar({ title, onJohnOpen }: { title?: string; onJohnOpen?: () => void }) {
  const { wsStatus, events } = useLegalStore();

  return (
    <header className="h-12 flex items-center justify-between px-5 border-b border-white/5 bg-[#0d1117] shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-sm font-mono font-semibold text-slate-200 tracking-wide">
          {title ?? "LEGAL COMMAND CENTER"}
        </span>
        <span className="text-xs text-slate-600 font-mono">LICEU 6.x</span>
      </div>

      <div className="flex items-center gap-4">
        {/* WS status */}
        <div className="flex items-center gap-1.5">
          {wsStatus === "connected" ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-mono text-emerald-400">LIVE</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-red-400" />
              <span className="text-xs font-mono text-red-400 blink">OFFLINE</span>
            </>
          )}
        </div>

        {/* Recent alerts */}
        <button className="relative text-slate-400 hover:text-slate-100 transition-colors">
          <Bell className="w-4 h-4" />
          {events.length > 0 && (
            <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500" />
          )}
        </button>

        {/* John Legal */}
        <button onClick={onJohnOpen} className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono hover:bg-blue-500/20 transition-all">
          <Bot className="w-3.5 h-3.5" />
          John Legal
        </button>
      </div>
    </header>
  );
}
