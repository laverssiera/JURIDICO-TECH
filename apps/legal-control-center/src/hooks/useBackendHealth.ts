"use client";

import { useEffect } from "react";
import { api } from "@/lib/api";
import { useLegalStore } from "@/store/legal";

export function useBackendHealth() {
  const { setApiStatus } = useLegalStore();

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        await api.get<{ status: string }>("/health");
        if (!cancelled) setApiStatus("online");
      } catch {
        if (!cancelled) setApiStatus("offline");
      }
    };

    check();
    const id = setInterval(check, 8000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [setApiStatus]);
}
