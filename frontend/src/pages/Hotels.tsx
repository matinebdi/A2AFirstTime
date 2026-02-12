import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Star, Filter } from 'lucide-react';
import Tilt from 'react-parallax-tilt';
import { tripadvisorApi } from '../services/api';
import { useSetPageContext } from '../contexts/PageContext';
import { PageTransition, FadeIn, StaggerContainer, StaggerItem } from '../components/animations';
import type { TripAdvisorPhoto, TripAdvisorReview } from '../types';

interface HotelWithDetails {
  [key: string]: unknown;
  id: string;
  location_id: string;
  name: string;
  address_obj?: { address_string?: string };
  search_country: string;
  photos: TripAdvisorPhoto[];
  reviews: TripAdvisorReview[];
  average_rating: number;
}

export const Hotels: React.FC = () => {
  const [hotels, setHotels] = useState<HotelWithDetails[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const setPageContext = useSetPageContext();

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
        const data = await tripadvisorApi.getLocationsWithDetails(selectedCountry || undefined);
        setHotels(data as unknown as HotelWithDetails[]);
      } catch (error) {
        console.error('Error fetching hotels:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHotels();
  }, [selectedCountry]);

  useEffect(() => {
    setPageContext({
      page: 'hotels',
      data: {
        filter_country: selectedCountry || undefined,
        count: hotels.length,
        hotels: hotels.map((h) => ({
          location_id: h.location_id,
          name: h.name,
          country: h.search_country,
          rating: h.average_rating,
        })),
      },
    });
  }, [hotels, selectedCountry]);

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
    <PageTransition>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <FadeIn>
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Hotels TripAdvisor
            </h1>
            <p className="text-gray-600">
              {hotels.length} hotels disponibles
            </p>
          </div>
        </FadeIn>

        {/* Filters */}
        <FadeIn delay={0.1}>
          <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow p-4 mb-8">
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
        </FadeIn>

        {/* Hotels Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="bg-gray-200 rounded-xl h-80 animate-pulse"
              />
            ))}
          </div>
        ) : (
          <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {hotels.map((hotel) => (
              <StaggerItem key={hotel.id} className="h-full">
                <Tilt
                  tiltMaxAngleX={8}
                  tiltMaxAngleY={8}
                  glareEnable={true}
                  glareMaxOpacity={0.15}
                  glareColor="#ffffff"
                  glarePosition="all"
                  glareBorderRadius="12px"
                  scale={1.02}
                  transitionSpeed={400}
                  className="rounded-xl h-full"
                >
                <Link
                  to={`/hotels/${hotel.location_id}`}
                  className="block h-full"
                >
                  <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow h-full flex flex-col">
                    {/* Image */}
                    <div className="relative h-48 flex-shrink-0">
                      {hotel.photos.length > 0 ? (
                        <img
                          src={tripadvisorApi.getPhotoUrl(hotel.photos[0])}
                          alt={hotel.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400">
                          No image
                        </div>
                      )}
                      <span className="absolute top-3 right-3 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                        {hotel.search_country}
                      </span>
                      {hotel.average_rating > 0 && (
                        <div className="absolute bottom-3 left-3 bg-white/90 px-2 py-1 rounded-full flex items-center text-sm">
                          <Star className="h-4 w-4 text-yellow-500 fill-current mr-1" />
                          {hotel.average_rating.toFixed(1)}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="p-4 flex flex-col flex-grow">
                      <h3 className="font-semibold text-lg text-gray-900 line-clamp-1">{hotel.name}</h3>
                      <div className="flex items-center text-gray-500 text-sm mt-1 line-clamp-1">
                        <MapPin className="h-4 w-4 mr-1 flex-shrink-0" />
                        <span className="truncate">{hotel.address_obj?.address_string || hotel.search_country}</span>
                      </div>

                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        <span>{hotel.photos.length} photos</span>
                        <span>{hotel.reviews.length} avis</span>
                      </div>

                      <div className="mt-auto pt-4 flex items-end justify-between">
                        {hotel.average_rating > 0 && renderStars(hotel.average_rating)}
                        <span className="text-blue-600 font-medium hover:underline">
                          Voir details
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
                </Tilt>
              </StaggerItem>
            ))}
          </StaggerContainer>
        )}

        {!loading && hotels.length === 0 && (
          <FadeIn>
            <div className="text-center py-12">
              <p className="text-gray-500">Aucun hotel trouve</p>
            </div>
          </FadeIn>
        )}
      </div>
    </PageTransition>
  );
};

export default Hotels;
