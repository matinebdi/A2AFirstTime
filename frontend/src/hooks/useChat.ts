import { useState, useEffect, useCallback, useRef } from 'react';
import type { ChatMessage, UIAction } from '../types';
import { traceChat } from '../utils/telemetry';

interface UseChatOptions {
  conversationId: string;
  onUIAction?: (action: UIAction) => void;
}

const MAX_RETRIES = 5;
const BASE_DELAY_MS = 1000;

export const useChat = ({ conversationId, onUIAction }: UseChatOptions) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const isMountedRef = useRef(true);
  const retriesRef = useRef(0);
  const onUIActionRef = useRef(onUIAction);

  // Keep the ref in sync with the latest callback without triggering effect re-runs
  useEffect(() => {
    onUIActionRef.current = onUIAction;
  }, [onUIAction]);

  useEffect(() => {
    // Don't connect if conversationId is empty
    if (!conversationId) {
      return;
    }

    isMountedRef.current = true;
    retriesRef.current = 0;
    setConnectionError(false);

    // Connect to backend WebSocket (port 8080)
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss:' : 'ws:';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}//${wsHost}/api/conversations/ws/${conversationId}`;

    const connect = () => {
      if (!isMountedRef.current) return;

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!isMountedRef.current) {
          ws.close();
          return;
        }
        setIsConnected(true);
        setConnectionError(false);
        retriesRef.current = 0;
        traceChat('chat.connect', { conversationId });
        console.log('Chat connected');
      };

      ws.onclose = () => {
        setIsConnected(false);
        traceChat('chat.disconnect', { conversationId });
        console.log('Chat disconnected');

        // Only reconnect if still mounted and under retry limit
        if (!isMountedRef.current) return;

        if (retriesRef.current < MAX_RETRIES) {
          const delay = BASE_DELAY_MS * Math.pow(2, retriesRef.current);
          retriesRef.current += 1;
          setTimeout(connect, delay);
        } else {
          setConnectionError(true);
          traceChat('chat.error', { reason: 'max_retries_exceeded', conversationId });
          console.warn('Chat: max reconnection retries exceeded');
        }
      };

      ws.onerror = (error) => {
        traceChat('chat.error', { reason: 'websocket_error', conversationId });
        console.error('WebSocket error:', error);
      };

      ws.onmessage = (event) => {
        let data: Record<string, unknown>;
        try {
          data = JSON.parse(event.data);
        } catch (e) {
          traceChat('chat.error', { reason: 'invalid_json', conversationId });
          console.error('Failed to parse WebSocket message:', e);
          return;
        }

        setIsTyping(false);
        traceChat('chat.receive', { conversationId, hasError: !!data.error });

        if (data.error) {
          console.error('Chat error:', data.error);
          return;
        }

        // Add assistant message
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.response as string,
          timestamp: data.timestamp as string,
          ui_actions: data.ui_actions as UIAction[],
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Handle UI actions via ref (avoids stale closure)
        if (data.ui_actions && onUIActionRef.current) {
          (data.ui_actions as UIAction[]).forEach((action: UIAction) => {
            onUIActionRef.current!(action);
          });
        }
      };

      wsRef.current = ws;
    };

    connect();

    return () => {
      isMountedRef.current = false;
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [conversationId]);

  const sendMessage = useCallback((content: string, context?: Record<string, unknown>) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    traceChat('chat.send', { conversationId });

    // Send to server
    wsRef.current.send(JSON.stringify({ message: content, context }));
  }, [conversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isConnected,
    isTyping,
    connectionError,
    sendMessage,
    clearMessages,
  };
};

export default useChat;
