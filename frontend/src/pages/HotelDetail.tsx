import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, Star, ArrowLeft } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { tripadvisorApi } from '../services/api';
import { useSetPageContext } from '../contexts/PageContext';
import { PageTransition, FadeIn } from '../components/animations';
import type { TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview } from '../types';

export const HotelDetail: React.FC = () => {
  const { locationId } = useParams<{ locationId: string }>();
  const navigate = useNavigate();
  const setPageContext = useSetPageContext();

  const [hotel, setHotel] = useState<TripAdvisorLocation | null>(null);
  const [photos, setPhotos] = useState<TripAdvisorPhoto[]>([]);
  const [reviews, setReviews] = useState<TripAdvisorReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPhoto, setSelectedPhoto] = useState(0);
  const [visibleReviews, setVisibleReviews] = useState(0);
  const reviewsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchHotel = async () => {
      if (!locationId) return;
      setLoading(true);
      try {
        const data = await tripadvisorApi.getLocationDetails(locationId);
        if (!data.location) {
          setError('Hotel introuvable');
          return;
        }
        setHotel(data.location);
        setPhotos(data.photos);
        setReviews(data.reviews);
      } catch {
        setError('Hotel introuvable');
      } finally {
        setLoading(false);
      }
    };
    fetchHotel();
  }, [locationId]);

  const averageRating = reviews.length > 0
    ? reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length
    : 0;

  // Progressive reveal: add one review every 300ms when section is in view
  useEffect(() => {
    if (reviews.length === 0) return;
    const el = reviewsRef.current;
    if (!el) return;

    let timer: ReturnType<typeof setInterval>;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          timer = setInterval(() => {
            setVisibleReviews((prev) => {
              if (prev >= reviews.length) {
                clearInterval(timer);
                return prev;
              }
              return prev + 1;
            });
          }, 300);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => {
      observer.disconnect();
      clearInterval(timer);
    };
  }, [reviews]);

  useEffect(() => {
    if (hotel) {
      setPageContext({
        page: 'hotelDetail',
        data: {
          location_id: hotel.location_id,
          hotel_name: hotel.name,
          country: hotel.search_country,
          address: hotel.address_obj?.address_string,
          rating: averageRating,
          reviews_count: reviews.length,
          photos_count: photos.length,
        },
      });
    }
  }, [hotel, reviews, photos]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !hotel) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-xl text-gray-600 mb-4">{error || 'Hotel introuvable'}</p>
        <button
          onClick={() => navigate('/hotels')}
          className="text-blue-600 hover:underline flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Retour aux hotels
        </button>
      </div>
    );
  }

  const photoUrls = photos.map((p) => tripadvisorApi.getPhotoUrl(p));

  return (
    <PageTransition>
      <div className="min-h-screen">
        {/* Back button */}
        <div className="max-w-7xl mx-auto px-4 pt-6">
          <button
            onClick={() => navigate(-1)}
            className="text-gray-600 hover:text-blue-600 flex items-center text-sm"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Retour
          </button>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Hero image */}
          {photoUrls.length > 0 && (
            <FadeIn>
              <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow overflow-hidden mb-6">
                <img
                  src={photoUrls[selectedPhoto]}
                  alt={hotel.name}
                  className="w-full h-[400px] object-cover"
                />
                {photoUrls.length > 1 && (
                  <div className="flex gap-2 p-3 overflow-x-auto">
                    {photoUrls.map((url, i) => (
                      <button
                        key={i}
                        onClick={() => setSelectedPhoto(i)}
                        className={`flex-shrink-0 w-20 h-14 rounded-lg overflow-hidden border-2 ${
                          i === selectedPhoto ? 'border-blue-600' : 'border-transparent'
                        }`}
                      >
                        <img src={url} alt="" className="w-full h-full object-cover" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </FadeIn>
          )}

          {/* Hotel info */}
          <FadeIn delay={0.1}>
            <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow p-6 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{hotel.name}</h1>
                  <div className="flex items-center text-gray-500 mt-1">
                    <MapPin className="h-4 w-4 mr-1" />
                    {hotel.address_obj?.address_string || hotel.search_country}
                  </div>
                </div>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {hotel.search_country}
                </span>
              </div>

              {averageRating > 0 && (
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`h-5 w-5 ${
                          star <= averageRating
                            ? 'text-yellow-400 fill-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-gray-600">
                    {averageRating.toFixed(1)} ({reviews.length} avis)
                  </span>
                </div>
              )}

              <div className="flex gap-4 text-sm text-gray-500">
                <span>{photos.length} photos</span>
                <span>{reviews.length} avis</span>
              </div>
            </div>
          </FadeIn>

          {/* Reviews */}
          {reviews.length > 0 && (
            <div ref={reviewsRef} className="bg-white/90 backdrop-blur-sm rounded-xl shadow p-6">
              <FadeIn>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Avis ({reviews.length})
                </h2>
              </FadeIn>
              <div className="space-y-4">
                <AnimatePresence>
                  {reviews.slice(0, visibleReviews).map((review) => (
                    <motion.div
                      key={review.id}
                      initial={{ opacity: 0, y: 30, height: 0 }}
                      animate={{ opacity: 1, y: 0, height: 'auto' }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                    >
                      <div className="bg-gray-50/80 backdrop-blur-sm rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="font-medium text-gray-900">
                              {review.user_name || 'Anonymous'}
                            </span>
                            {review.published_date && (
                              <span className="text-sm text-gray-500 ml-2">
                                {new Date(review.published_date).toLocaleDateString('fr-FR')}
                              </span>
                            )}
                          </div>
                          {review.rating > 0 && (
                            <div className="flex items-center gap-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`h-4 w-4 ${
                                    star <= review.rating
                                      ? 'text-yellow-400 fill-yellow-400'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                          )}
                        </div>
                        {review.title && (
                          <h4 className="font-medium text-gray-800 mb-1">{review.title}</h4>
                        )}
                        <p className="text-gray-600 text-sm">{review.text}</p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default HotelDetail;
