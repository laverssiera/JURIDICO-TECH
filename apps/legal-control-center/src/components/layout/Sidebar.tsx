"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, FileText, Search, Siren, Leaf, ClipboardCheck,
  Kanban, Users, Building2, GraduationCap, Store, BarChart3,
  Shield, Settings, ChevronLeft, ChevronRight, Scale,
} from "lucide-react";
import { useLegalStore } from "@/store/legal";
import { cn } from "@/lib/utils";

const NAV = [
  { label: "Command Center",   href: "/dashboard",             icon: LayoutDashboard },
  { label: "Kanban Jurídico",  href: "/kanban",                icon: Kanban },
  { label: "Contratos",        href: "/contratos",             icon: FileText },
  { label: "Perícias",         href: "/pericias",              icon: Search },
  { label: "War Room",         href: "/war-room",              icon: Siren },
  { label: "ESG & Compliance", href: "/esg",                   icon: Leaf },
  { label: "Compliance",       href: "/compliance",            icon: ClipboardCheck },
  { label: "Arbitragem",       href: "/arbitragem",            icon: Scale },
  { label: "Marketplace",      href: "/marketplace",           icon: Store },
  { label: "Portal Cliente",   href: "/portal-cliente",        icon: Users },
  { label: "Portal Fornecedor",href: "/portal-fornecedor",     icon: Building2 },
  { label: "Investidores",     href: "/portal-investidor",     icon: BarChart3 },
  { label: "Universidade",     href: "/portal-universidade",   icon: GraduationCap },
  { label: "Configurações",    href: "/settings",              icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, setSidebar } = useLegalStore();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen shrink-0 border-r transition-all duration-300",
        "border-white/5 bg-[#0d1117]",
        sidebarOpen ? "w-56" : "w-14"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/5">
        <Shield className="w-6 h-6 text-blue-400 shrink-0" />
        {sidebarOpen && (
          <span className="font-mono text-sm font-bold text-white tracking-wider">
            JURÍDICO<span className="text-blue-400">.TECH</span>
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 space-y-0.5 px-2">
        {NAV.map(({ label, href, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-2 py-2 rounded-lg text-xs font-medium transition-all",
                active
                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              )}
              title={!sidebarOpen ? label : undefined}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {sidebarOpen && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setSidebar(!sidebarOpen)}
        className="m-3 flex items-center justify-center h-8 rounded-lg border border-white/5 text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-all"
      >
        {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
    </aside>
  );
}
