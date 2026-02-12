import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plane, Mail, Lock, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { PageTransition, FadeIn, AnimatedButton } from '../components/animations';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signIn(email, password);
      navigate('/');
    } catch (err) {
      setError('Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageTransition>
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-12 px-4">
        <FadeIn className="max-w-md w-full">
          <div className="text-center mb-8">
            <Link to="/" className="inline-flex items-center space-x-2">
              <Plane className="h-10 w-10 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">VacanceAI</span>
            </Link>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Connexion
            </h2>
            <p className="mt-2 text-gray-600">
              Connectez-vous pour acceder a votre compte
            </p>
          </div>

          <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-8">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="votre@email.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Votre mot de passe"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input type="checkbox" className="h-4 w-4 text-blue-600 rounded" />
                  <span className="ml-2 text-sm text-gray-600">Se souvenir de moi</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-blue-600 hover:underline"
                >
                  Mot de passe oublie?
                </Link>
              </div>

              <AnimatedButton
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-blue-300 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    Connexion...
                  </>
                ) : (
                  'Se connecter'
                )}
              </AnimatedButton>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600">
                Pas encore de compte?{' '}
                <Link to="/signup" className="text-blue-600 hover:underline font-medium">
                  S'inscrire
                </Link>
              </p>
            </div>
          </div>
        </FadeIn>
      </div>
    </PageTransition>
  );
};

export default Login;
