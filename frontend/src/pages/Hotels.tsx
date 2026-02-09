import { useEffect, useState } from 'react';
import { MapPin, Star, Filter, ChevronDown, ChevronUp } from 'lucide-react';
import { tripadvisorApi } from '../services/tripadvisor';
import type { TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview } from '../types';

interface HotelWithDetails extends TripAdvisorLocation {
  photos: TripAdvisorPhoto[];
  reviews: TripAdvisorReview[];
  averageRating: number;
}

export const Hotels: React.FC = () => {
  const [hotels, setHotels] = useState<HotelWithDetails[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [expandedHotel, setExpandedHotel] = useState<string | null>(null);

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const data = await tripadvisorApi.getCountries();
        setCountries(data);
      } catch (error) {
        console.error('Error fetching countries:', error);
      }
    };
    fetchCountries();
  }, []);

  useEffect(() => {
    const fetchHotels = async () => {
      setLoading(true);
      try {
        const locations = await tripadvisorApi.getLocations(selectedCountry || undefined);

        // Fetch photos and reviews for each hotel
        const hotelsWithDetails = await Promise.all(
          locations.map(async (location) => {
            const [photos, reviews] = await Promise.all([
              tripadvisorApi.getPhotos(location.location_id),
              tripadvisorApi.getReviews(location.location_id),
            ]);

            const averageRating = reviews.length > 0
              ? reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length
              : 0;

            return {
              ...location,
              photos,
              reviews,
              averageRating,
            };
          })
        );

        setHotels(hotelsWithDetails);
      } catch (error) {
        console.error('Error fetching hotels:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHotels();
  }, [selectedCountry]);

  const toggleHotelExpand = (locationId: string) => {
    setExpandedHotel(expandedHotel === locationId ? null : locationId);
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-gray-600">
          ({rating.toFixed(1)})
        </span>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Hotels TripAdvisor
        </h1>
        <p className="text-gray-600">
          {hotels.length} hotels disponibles
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-8">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous les pays</option>
            {countries.map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Hotels List */}
      {loading ? (
        <div className="grid grid-cols-1 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-gray-200 rounded-xl h-48 animate-pulse"
            />
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {hotels.map((hotel) => (
            <div
              key={hotel.id}
              className="bg-white rounded-xl shadow-lg overflow-hidden"
            >
              {/* Hotel Card */}
              <div className="flex flex-col md:flex-row">
                {/* Image */}
                <div className="md:w-72 h-48 md:h-auto bg-gray-200 flex-shrink-0">
                  {hotel.photos.length > 0 ? (
                    <img
                      src={tripadvisorApi.getPhotoUrl(hotel.photos[0])}
                      alt={hotel.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No image
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="flex-grow p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 mb-2">
                        {hotel.name}
                      </h2>
                      <div className="flex items-center text-gray-600 mb-2">
                        <MapPin className="h-4 w-4 mr-1" />
                        <span className="text-sm">
                          {hotel.address_obj?.address_string || hotel.search_country}
                        </span>
                      </div>
                      {hotel.averageRating > 0 && renderStars(hotel.averageRating)}
                    </div>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {hotel.search_country}
                    </span>
                  </div>

                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                    <span>{hotel.photos.length} photos</span>
                    <span>{hotel.reviews.length} avis</span>
                  </div>

                  {/* Expand Button */}
                  <button
                    onClick={() => toggleHotelExpand(hotel.location_id)}
                    className="mt-4 flex items-center text-blue-600 hover:text-blue-800"
                  >
                    {expandedHotel === hotel.location_id ? (
                      <>
                        <ChevronUp className="h-4 w-4 mr-1" />
                        Masquer les details
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4 mr-1" />
                        Voir photos et avis
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedHotel === hotel.location_id && (
                <div className="border-t">
                  {/* Photos Grid */}
                  {hotel.photos.length > 0 && (
                    <div className="p-6 border-b">
                      <h3 className="font-semibold text-gray-900 mb-4">Photos</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                        {hotel.photos.slice(0, 12).map((photo) => (
                          <img
                            key={photo.id}
                            src={tripadvisorApi.getPhotoUrl(photo)}
                            alt={photo.caption || hotel.name}
                            className="w-full h-24 object-cover rounded-lg"
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Reviews */}
                  {hotel.reviews.length > 0 && (
                    <div className="p-6">
                      <h3 className="font-semibold text-gray-900 mb-4">
                        Avis ({hotel.reviews.length})
                      </h3>
                      <div className="space-y-4">
                        {hotel.reviews.slice(0, 5).map((review) => (
                          <div
                            key={review.id}
                            className="bg-gray-50 rounded-lg p-4"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <span className="font-medium text-gray-900">
                                  {review.user_name || 'Anonymous'}
                                </span>
                                <span className="text-sm text-gray-500 ml-2">
                                  {review.published_date}
                                </span>
                              </div>
                              {review.rating && renderStars(review.rating)}
                            </div>
                            {review.title && (
                              <h4 className="font-medium text-gray-800 mb-1">
                                {review.title}
                              </h4>
                            )}
                            <p className="text-gray-600 text-sm line-clamp-3">
                              {review.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!loading && hotels.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Aucun hotel trouve</p>
        </div>
      )}
    </div>
  );
};

export default Hotels;
