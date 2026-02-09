import { useState, useEffect, useRef, useCallback } from 'react';
import { MessageCircle, X, Send, Loader2, WifiOff } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { useAuth } from '../../contexts/AuthContext';
import { generateUUID } from '../../utils/uuid';
import { ChatErrorBoundary } from './ChatErrorBoundary';
import type { UIAction } from '../../types';

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  useEffect(() => {
    // Generate or retrieve conversation ID
    const storedId = sessionStorage.getItem('chat_conversation_id');
    if (storedId) {
      setConversationId(storedId);
    } else {
      const newId = generateUUID();
      sessionStorage.setItem('chat_conversation_id', newId);
      setConversationId(newId);
    }
  }, []);

  const handleUIAction = useCallback((action: UIAction) => {
    console.log('UI Action:', action);
    // Handle different UI actions here
    switch (action.action) {
      case 'navigate':
        window.location.href = `/${action.page}`;
        break;
      case 'show_search_results':
        // Could dispatch to a global state or emit an event
        break;
      default:
        console.log('Unhandled action:', action);
    }
  }, []);

  const { messages, isConnected, isTyping, connectionError, sendMessage } = useChat({
    conversationId,
    onUIAction: handleUIAction,
  });

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    sendMessage(input, { user: user ? { id: user.id, name: user.first_name } : undefined });
    setInput('');
  };

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all z-50 ${
          isOpen ? 'bg-gray-600' : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {isOpen ? (
          <X className="h-6 w-6 text-white" />
        ) : (
          <MessageCircle className="h-6 w-6 text-white" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <ChatErrorBoundary>
          <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-lg shadow-xl flex flex-col z-50 overflow-hidden">
            {/* Header */}
            <div className="bg-blue-600 text-white px-4 py-3 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Assistant VacanceAI</h3>
                <p className="text-xs text-blue-200">
                  {connectionError
                    ? 'Impossible de se connecter'
                    : isConnected
                      ? 'En ligne'
                      : 'Connexion...'}
                </p>
              </div>
              <div
                className={`w-2 h-2 rounded-full ${
                  connectionError
                    ? 'bg-red-400'
                    : isConnected
                      ? 'bg-green-400'
                      : 'bg-yellow-400'
                }`}
              />
            </div>

            {/* Messages */}
            <div className="flex-grow overflow-y-auto p-4 space-y-4">
              {connectionError && (
                <div className="text-center text-red-500 mt-4">
                  <WifiOff className="h-10 w-10 mx-auto mb-2 text-red-300" />
                  <p className="text-sm font-medium">Connexion au serveur impossible</p>
                  <p className="text-xs text-red-400 mt-1">Veuillez rafraichir la page pour r&eacute;essayer.</p>
                </div>
              )}

              {!connectionError && messages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium">Bonjour!</p>
                  <p className="text-sm">
                    Je suis votre assistant vacances. Comment puis-je vous aider
                    aujourd'hui?
                  </p>
                </div>
              )}

              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-2">
                    <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Tapez votre message..."
                  className="flex-grow px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={!isConnected}
                />
                <button
                  type="submit"
                  disabled={!isConnected || !input.trim()}
                  className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </form>
          </div>
        </ChatErrorBoundary>
      )}
    </>
  );
};

export default ChatWidget;
