"use client";
import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";
import JohnCopilot from "@/components/JohnCopilot";
import { useBackendHealth } from "@/hooks/useBackendHealth";
import { useEventStream } from "@/hooks/useEventStream";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  useEventStream();
  useBackendHealth();
  const [johnOpen, setJohnOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden relative">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar onJohnOpen={() => setJohnOpen(true)} />
        <main className="flex-1 overflow-y-auto bg-[#080b12]">
          {children}
        </main>
      </div>
      <JohnCopilot open={johnOpen} onClose={() => setJohnOpen(false)} />
    </div>
  );
}
