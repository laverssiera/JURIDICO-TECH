"use client";
import { useEffect } from "react";
import { useLegalStore } from "@/store/legal";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/events/ws";

let ws: WebSocket | null = null;

export function useEventStream() {
  const { pushEvent, setWsStatus } = useLegalStore();

  useEffect(() => {
    if (ws && ws.readyState < 2) return;

    setWsStatus("connecting");
    ws = new WebSocket(WS_URL);

    ws.onopen = () => setWsStatus("connected");

    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        pushEvent({
          id: crypto.randomUUID(),
          type: data.type ?? "unknown",
          payload: data.payload ?? {},
          ts: new Date().toISOString(),
        });
      } catch {
        // ignore malformed messages
      }
    };

    ws.onerror = () => setWsStatus("disconnected");
    ws.onclose = () => {
      setWsStatus("disconnected");
      // reconnect after 3s
      setTimeout(() => { ws = null; }, 3000);
    };

    return () => {
      // intentionally keep WS alive across component mounts
    };
  }, [pushEvent, setWsStatus]);
}
