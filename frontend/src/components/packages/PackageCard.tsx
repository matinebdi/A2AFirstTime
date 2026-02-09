import { Heart, MapPin, Calendar, Users, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Package } from '../../types';
import { useState } from 'react';
import { favoritesApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface PackageCardProps {
  pkg: Package;
  onFavoriteToggle?: (packageId: string, isFavorite: boolean) => void;
}

export const PackageCard: React.FC<PackageCardProps> = ({ pkg, onFavoriteToggle }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  const handleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!user) {
      window.location.href = '/login';
      return;
    }

    setIsLoading(true);
    try {
      if (isFavorite) {
        await favoritesApi.remove(pkg.id);
      } else {
        await favoritesApi.add(pkg.id);
      }
      setIsFavorite(!isFavorite);
      onFavoriteToggle?.(pkg.id, !isFavorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const destination = pkg.destinations;
  const imageUrl = pkg.images?.[0] || destination?.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e';

  return (
    <Link to={`/packages/${pkg.id}`} className="block">
      <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        {/* Image */}
        <div className="relative h-48">
          <img
            src={imageUrl}
            alt={pkg.name}
            className="w-full h-full object-cover"
          />
          <button
            onClick={handleFavorite}
            disabled={isLoading}
            className={`absolute top-3 right-3 p-2 rounded-full ${
              isFavorite ? 'bg-red-500 text-white' : 'bg-white/80 text-gray-600'
            } hover:scale-110 transition-transform`}
          >
            <Heart className={`h-5 w-5 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
          {destination?.average_rating && (
            <div className="absolute bottom-3 left-3 bg-white/90 px-2 py-1 rounded-full flex items-center text-sm">
              <Star className="h-4 w-4 text-yellow-500 fill-current mr-1" />
              {destination.average_rating.toFixed(1)}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-lg text-gray-900">{pkg.name}</h3>
              {destination && (
                <div className="flex items-center text-gray-500 text-sm mt-1">
                  <MapPin className="h-4 w-4 mr-1" />
                  {destination.name}, {destination.country}
                </div>
              )}
            </div>
          </div>

          <p className="text-gray-600 text-sm mt-2 line-clamp-2">
            {pkg.description}
          </p>

          {/* Details */}
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              {pkg.duration_days} jours
            </div>
            <div className="flex items-center">
              <Users className="h-4 w-4 mr-1" />
              Max {pkg.max_persons}
            </div>
          </div>

          {/* Price */}
          <div className="mt-4 flex items-end justify-between">
            <div>
              <span className="text-2xl font-bold text-blue-600">
                {pkg.price_per_person.toFixed(0)}
              </span>
              <span className="text-gray-500 text-sm">/pers</span>
            </div>
            <span className="text-blue-600 font-medium hover:underline">
              Voir details
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default PackageCard;
