import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Heart, Loader2 } from 'lucide-react';
import { favoritesApi } from '../services/api';
import { PackageCard } from '../components/packages/PackageCard';
import { useAuth } from '../contexts/AuthContext';
import { useSetPageContext } from '../contexts/PageContext';
import { PageTransition, FadeIn, StaggerContainer, StaggerItem, AnimatedLinkButton } from '../components/animations';
import type { Package } from '../types';

export const Favorites: React.FC = () => {
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();
  const setPageContext = useSetPageContext();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchFavorites();
  }, [user, navigate]);

  useEffect(() => {
    setPageContext({
      page: 'favorites',
      data: {
        count: packages.length,
        favorites: packages.map((p) => ({
          id: p.id,
          name: p.name,
          price_per_person: p.price_per_person,
        })),
      },
    });
  }, [packages]);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const favorites = await favoritesApi.list();
      const pkgs = favorites
        .map((f) => f.packages)
        .filter((p): p is Package => p != null);
      setPackages(pkgs);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFavoriteToggle = (packageId: string, isFavorite: boolean) => {
    if (!isFavorite) {
      setPackages((prev) => prev.filter((p) => p.id !== packageId));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4">
          <FadeIn>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Mes Favoris</h1>
                <p className="text-gray-600 mt-2">
                  {packages.length > 0
                    ? `${packages.length} package${packages.length > 1 ? 's' : ''} sauvegarde${packages.length > 1 ? 's' : ''}`
                    : 'Retrouvez ici vos packages preferes'}
                </p>
              </div>
              <AnimatedLinkButton
                to="/search"
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Rechercher
              </AnimatedLinkButton>
            </div>
          </FadeIn>

          {packages.length === 0 ? (
            <FadeIn>
              <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow p-16 text-center">
                <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-700 mb-2">
                  Pas encore de favoris
                </h2>
                <p className="text-gray-500 mb-4">
                  Explorez nos packages et ajoutez vos coups de coeur
                </p>
                <Link
                  to="/search"
                  className="text-blue-600 hover:underline font-medium"
                >
                  Decouvrir les packages
                </Link>
              </div>
            </FadeIn>
          ) : (
            <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {packages.map((pkg) => (
                <StaggerItem key={pkg.id}>
                  <PackageCard
                    pkg={pkg}
                    initialFavorite={true}
                    onFavoriteToggle={handleFavoriteToggle}
                  />
                </StaggerItem>
              ))}
            </StaggerContainer>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default Favorites;
