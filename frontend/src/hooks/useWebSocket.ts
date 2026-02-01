import { useEffect, useRef, useState } from 'react';
import { BinDisplayData, AlertLog, WSMessage } from '../types';

type MessageHandler = (data: BinDisplayData | AlertLog) => void;

interface UseWebSocketOptions {
  onBinUpdate?: MessageHandler;
  onAlert?: MessageHandler;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectInterval?: number;
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    reconnectInterval = 5000,
  } = options;

  // Store callbacks in refs to avoid re-renders
  const optionsRef = useRef(options);
  optionsRef.current = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    mountedRef.current = true;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
        return;
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!mountedRef.current) return;
          console.log('WebSocket connected');
          setIsConnected(true);
          optionsRef.current.onConnect?.();
        };

        ws.onclose = () => {
          if (!mountedRef.current) return;
          console.log('WebSocket disconnected');
          setIsConnected(false);
          optionsRef.current.onDisconnect?.();

          // Schedule reconnection only if still mounted
          if (mountedRef.current) {
            reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        ws.onmessage = (event) => {
          if (!mountedRef.current) return;
          try {
            const message: WSMessage = JSON.parse(event.data);

            switch (message.type) {
              case 'bin_update':
                optionsRef.current.onBinUpdate?.(message.payload as BinDisplayData);
                break;
              case 'alert':
                optionsRef.current.onAlert?.(message.payload as AlertLog);
                break;
              case 'connection':
                console.log('Connection confirmed:', message.payload);
                break;
              case 'heartbeat':
                // Heartbeat received
                break;
              default:
                console.log('Unknown message type:', message.type);
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        if (mountedRef.current) {
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      }
    };

    connect();

    // Set up ping interval
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => {
      mountedRef.current = false;
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [reconnectInterval]);

  const sendMessage = (message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  const reconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  return {
    isConnected,
    sendMessage,
    reconnect,
  };
}
