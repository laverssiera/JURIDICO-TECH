// Zustand store — estado global do Legal Control Center
import { create } from "zustand";

export type RiskLevel = "verde" | "amarelo" | "vermelho" | "preto";

export interface LiveEvent {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  ts: string;
}

export interface KpiState {
  twins: number;
  radarSignals: number;
  warRoomIncidents: number;
  legalOsBlocked: number;
  simulations: number;
  trustAvg: number;
}

interface LegalStore {
  kpis: KpiState;
  events: LiveEvent[];
  wsStatus: "connecting" | "connected" | "disconnected";
  apiStatus: "checking" | "online" | "offline";
  sidebarOpen: boolean;
  setKpis: (k: Partial<KpiState>) => void;
  pushEvent: (e: LiveEvent) => void;
  setWsStatus: (s: LegalStore["wsStatus"]) => void;
  setApiStatus: (s: LegalStore["apiStatus"]) => void;
  setSidebar: (v: boolean) => void;
}

export const useLegalStore = create<LegalStore>((set) => ({
  kpis: { twins: 0, radarSignals: 0, warRoomIncidents: 0, legalOsBlocked: 0, simulations: 0, trustAvg: 0 },
  events: [],
  wsStatus: "disconnected",
  apiStatus: "checking",
  sidebarOpen: true,
  setKpis: (k) => set((s) => ({ kpis: { ...s.kpis, ...k } })),
  pushEvent: (e) =>
    set((s) => ({
      events: [e, ...s.events].slice(0, 50),
    })),
  setWsStatus: (wsStatus) => set({ wsStatus }),
  setApiStatus: (apiStatus) => set({ apiStatus }),
  setSidebar: (sidebarOpen) => set({ sidebarOpen }),
}));
