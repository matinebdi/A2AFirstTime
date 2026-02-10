import { Link, useNavigate } from 'react-router-dom';
import { Plane, Search, Heart, User, LogOut, Menu, X, Building2, Home, RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export const Header: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await signOut();
    navigate('/');
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Plane className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">VacanceAI</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className="flex items-center text-gray-600 hover:text-blue-600 transition"
            >
              <Home className="h-5 w-5 mr-1" />
              Accueil
            </Link>
            <Link
              to="/search"
              className="flex items-center text-gray-600 hover:text-blue-600 transition"
            >
              <Search className="h-5 w-5 mr-1" />
              Rechercher
            </Link>
            <Link
              to="/hotels"
              className="flex items-center text-gray-600 hover:text-blue-600 transition"
            >
              <Building2 className="h-5 w-5 mr-1" />
              Hotels
            </Link>

            {user ? (
              <>
                <Link
                  to="/bookings"
                  className="text-gray-600 hover:text-blue-600 transition"
                >
                  Mes Voyages
                </Link>
                <Link
                  to="/favorites"
                  className="flex items-center text-gray-600 hover:text-blue-600 transition"
                >
                  <Heart className="h-5 w-5 mr-1" />
                  Favoris
                </Link>
                <div className="relative group">
                  <button className="flex items-center text-gray-600 hover:text-blue-600 transition">
                    <User className="h-5 w-5 mr-1" />
                    {user.first_name || 'Mon Compte'}
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                    >
                      Profil
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Deconnexion
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-blue-600 transition"
                >
                  Connexion
                </Link>
                <Link
                  to="/signup"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Inscription
                </Link>
              </div>
            )}
          </nav>

          {/* Refresh + Mobile menu button */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => window.location.reload()}
              className="p-2 text-gray-500 hover:text-blue-600 transition"
              title="Rafraichir la page"
            >
              <RefreshCw className="h-5 w-5" />
            </button>
          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <nav className="flex flex-col space-y-4">
              <Link
                to="/"
                className="text-gray-600 hover:text-blue-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Accueil
              </Link>
              <Link
                to="/search"
                className="text-gray-600 hover:text-blue-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Rechercher
              </Link>
              <Link
                to="/hotels"
                className="text-gray-600 hover:text-blue-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Hotels
              </Link>
              {user ? (
                <>
                  <Link
                    to="/bookings"
                    className="text-gray-600 hover:text-blue-600"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Mes Voyages
                  </Link>
                  <Link
                    to="/favorites"
                    className="text-gray-600 hover:text-blue-600"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Favoris
                  </Link>
                  <Link
                    to="/profile"
                    className="text-gray-600 hover:text-blue-600"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Profil
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="text-left text-gray-600 hover:text-blue-600"
                  >
                    Deconnexion
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-gray-600 hover:text-blue-600"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Connexion
                  </Link>
                  <Link
                    to="/signup"
                    className="text-blue-600 font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Inscription
                  </Link>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
