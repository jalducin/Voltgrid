'use client';

import { useEffect, useRef, useState } from 'react';
import { API_BASE_URL } from './api';
import { getAccessToken } from './store';
import type { StationStatusMessage } from './types';

export type WsState = 'connecting' | 'open' | 'closed';

// Convierte la URL http(s) de la API en ws(s).
function toWsUrl(stationId: string, token: string): string {
  const base = API_BASE_URL.replace(/^http/, 'ws');
  return `${base}/ws/stations/${stationId}/status?token=${encodeURIComponent(token)}`;
}

/**
 * Abre un WebSocket para una estación y entrega los mensajes de cambio de estado.
 * Reintenta la conexión automáticamente. El consumidor puede usar el estado de
 * conexión para decidir si activa el fallback a polling.
 */
export function useWebSocket(
  stationId: string | null,
  onMessage: (msg: StationStatusMessage) => void,
): WsState {
  const [state, setState] = useState<WsState>('connecting');
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!stationId || typeof window === 'undefined') {
      setState('closed');
      return;
    }

    const token = getAccessToken();
    if (!token) {
      setState('closed');
      return;
    }

    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let closedByCleanup = false;

    const connect = () => {
      setState('connecting');
      ws = new WebSocket(toWsUrl(stationId, token));

      ws.onopen = () => setState('open');

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as StationStatusMessage;
          onMessageRef.current(data);
        } catch {
          // Ignoramos mensajes que no sean JSON válido.
        }
      };

      ws.onclose = () => {
        setState('closed');
        if (!closedByCleanup) {
          // Reintento con un pequeño retraso.
          reconnectTimer = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        ws?.close();
      };
    };

    connect();

    return () => {
      closedByCleanup = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [stationId]);

  return state;
}
