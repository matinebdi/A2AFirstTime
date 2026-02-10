import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, X, Send, Loader2, WifiOff, MapPin } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { useAuth } from '../../contexts/AuthContext';
import { usePageContext } from '../../contexts/PageContext';
import { generateUUID } from '../../utils/uuid';
import { ChatErrorBoundary } from './ChatErrorBoundary';
import { favoritesApi } from '../../services/api';
import type { UIAction, ChatMessage } from '../../types';

interface PackageData {
  id: string;
  name: string;
  price_per_person?: number;
  duration_days?: number;
  images?: string[];
  image_url?: string;
  destination_name?: string;
  destinations?: { name?: string; country?: string; image_url?: string };
}

const MiniPackageCard: React.FC<{ pkg: PackageData; onClick: () => void }> = ({ pkg, onClick }) => {
  const imageUrl = pkg.images?.[0] || pkg.image_url || pkg.destinations?.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e';
  const destinationLabel = pkg.destination_name || (pkg.destinations ? `${pkg.destinations.name || ''}${pkg.destinations.country ? ', ' + pkg.destinations.country : ''}` : '');

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 bg-white border rounded-lg p-2 hover:shadow-md transition-shadow w-full text-left"
    >
      <img
        src={imageUrl}
        alt={pkg.name}
        className="w-14 h-14 rounded-md object-cover flex-shrink-0"
      />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900 truncate">{pkg.name}</p>
        {destinationLabel && (
          <p className="text-xs text-gray-500 flex items-center gap-0.5 truncate">
            <MapPin className="h-3 w-3 flex-shrink-0" />
            {destinationLabel}
          </p>
        )}
        <div className="flex items-center gap-2 mt-0.5">
          {pkg.price_per_person != null && (
            <span className="text-xs font-semibold text-blue-600">{pkg.price_per_person.toFixed(0)}/pers</span>
          )}
          {pkg.duration_days != null && (
            <span className="text-xs text-gray-400">{pkg.duration_days}j</span>
          )}
        </div>
      </div>
    </button>
  );
};


const PackageCards: React.FC<{ packages: PackageData[]; onSelect: (id: string) => void }> = ({ packages, onSelect }) => {
  if (!packages || packages.length === 0) return null;
  return (
    <div className="flex flex-col gap-1.5 mt-2">
      {packages.slice(0, 5).map((pkg) => (
        <MiniPackageCard key={pkg.id} pkg={pkg} onClick={() => onSelect(pkg.id)} />
      ))}
    </div>
  );
};

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string>('');
  const [notification, setNotification] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  const pageContext = usePageContext();
  const navigate = useNavigate();

  useEffect(() => {
    const storedId = sessionStorage.getItem('chat_conversation_id');
    if (storedId) {
      setConversationId(storedId);
    } else {
      const newId = generateUUID();
      sessionStorage.setItem('chat_conversation_id', newId);
      setConversationId(newId);
    }
  }, []);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleUIAction = useCallback((action: UIAction) => {
    console.log('UI Action:', action);
    switch (action.action) {
      case 'navigate':
        navigate(`/${action.page}`);
        break;
      case 'show_search_results':
        navigate('/search');
        break;
      case 'show_package_modal':
        if (action.package && (action.package as PackageData).id) {
          navigate(`/packages/${(action.package as PackageData).id}`);
        }
        break;
      case 'open_booking_form':
        if (action.package && (action.package as PackageData).id) {
          navigate(`/packages/${(action.package as PackageData).id}`);
        }
        break;
      case 'show_recommendations':
        // Packages are rendered inline via cards - no navigation needed
        break;
      case 'booking_confirmed':
        navigate('/bookings');
        break;
      case 'add_favorite':
        if (action.package_id && user) {
          favoritesApi.add(action.package_id as string)
            .then(() => setNotification(action.message as string || 'Ajout aux favoris!'))
            .catch(() => setNotification('Erreur lors de l\'ajout aux favoris'));
        } else if (!user) {
          navigate('/login');
        }
        break;
      case 'show_error':
      case 'show_message':
        // These are shown inline via the assistant text - no extra handling needed
        break;
      default:
        console.log('Unhandled action:', action);
    }
  }, [navigate, user]);

  const { messages, isConnected, isTyping, connectionError, sendMessage } = useChat({
    conversationId,
    onUIAction: handleUIAction,
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    sendMessage(input, {
      user: user ? { id: user.id, name: user.first_name } : undefined,
      page: pageContext,
    });
    setInput('');
  };

  const getPackagesFromActions = (msg: ChatMessage): PackageData[] => {
    if (!msg.ui_actions) return [];
    const packages: PackageData[] = [];
    for (const action of msg.ui_actions) {
      if (
        (action.action === 'show_search_results' || action.action === 'show_recommendations') &&
        Array.isArray(action.packages)
      ) {
        packages.push(...(action.packages as PackageData[]));
      }
    }
    return packages;
  };


  const handlePackageSelect = (packageId: string) => {
    navigate(`/packages/${packageId}`);
  };

  return (
    <>
      {/* Notification toast */}
      {notification && (
        <div className="fixed bottom-24 right-6 z-[60] bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm animate-fade-in">
          {notification}
        </div>
      )}

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

              {messages.map((msg, index) => {
                const packages = msg.role === 'assistant' ? getPackagesFromActions(msg) : [];
                return (
                  <div key={index}>
                    <div
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
                    {packages.length > 0 && (
                      <div className="mt-2 ml-1">
                        <PackageCards packages={packages} onSelect={handlePackageSelect} />
                      </div>
                    )}
                  </div>
                );
              })}

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
