/**
 * WebSocket hook for real-time job progress updates
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import type { ProgressUpdate } from '../types/api';

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

interface UseWebSocketOptions {
  onConnected?: () => void;
  onProgress?: (update: ProgressUpdate) => void;
  onShotComplete?: (update: ProgressUpdate) => void;
  onJobComplete?: (update: ProgressUpdate) => void;
  onError?: (error: string) => void;
}

export const useWebSocket = (jobId: string | null, options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<ProgressUpdate | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const connect = useCallback(() => {
    if (!jobId) return;

    const ws = new WebSocket(`${WS_BASE_URL}/ws/jobs/${jobId}`);

    ws.onopen = () => {
      console.log(`WebSocket connected for job ${jobId}`);
      setIsConnected(true);
      options.onConnected?.();
    };

    ws.onmessage = (event) => {
      try {
        const update: ProgressUpdate = JSON.parse(event.data);
        setLastUpdate(update);

        switch (update.type) {
          case 'connected':
            break;
          case 'progress':
            options.onProgress?.(update);
            break;
          case 'shot_complete':
            options.onShotComplete?.(update);
            break;
          case 'job_complete':
            options.onJobComplete?.(update);
            break;
          case 'error':
            options.onError?.(update.error || 'Unknown error');
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);

      // Attempt to reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        connect();
      }, 3000);
    };

    wsRef.current = ws;
  }, [jobId, options]);

  useEffect(() => {
    if (jobId) {
      connect();
    }

    // Cleanup
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [jobId, connect]);

  // Send ping to keep connection alive
  useEffect(() => {
    if (!isConnected || !wsRef.current) return;

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(pingInterval);
  }, [isConnected]);

  return {
    isConnected,
    lastUpdate,
  };
};
