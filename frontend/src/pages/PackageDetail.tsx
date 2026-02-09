import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  MapPin, Calendar, Users, Star, Plane, Hotel,
  UtensilsCrossed, Activity, ArrowLeft, Check
} from 'lucide-react';
import { packagesApi, bookingsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useSetPageContext } from '../contexts/PageContext';
import type { Package } from '../types';

export const PackageDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const setPageContext = useSetPageContext();

  const [pkg, setPkg] = useState<Package | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedImage, setSelectedImage] = useState(0);

  // Booking form
  const [startDate, setStartDate] = useState('');
  const [numPersons, setNumPersons] = useState(1);
  const [booking, setBooking] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [bookingError, setBookingError] = useState('');

  useEffect(() => {
    const fetchPackage = async () => {
      if (!id) return;
      setLoading(true);
      try {
        const data = await packagesApi.get(id);
        setPkg(data);
      } catch {
        setError('Package introuvable');
      } finally {
        setLoading(false);
      }
    };
    fetchPackage();
  }, [id]);

  useEffect(() => {
    if (pkg) {
      setPageContext({
        page: 'packageDetail',
        data: {
          package_id: pkg.id,
          package_name: pkg.name,
          destination: pkg.destinations?.name,
          price_per_person: pkg.price_per_person,
          duration_days: pkg.duration_days,
          max_persons: pkg.max_persons,
        },
      });
    }
  }, [pkg]);

  const handleBook = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (!id || !startDate) return;

    setBooking(true);
    setBookingError('');
    try {
      await bookingsApi.create({
        package_id: id,
        start_date: startDate,
        num_persons: numPersons,
      });
      setBookingSuccess(true);
    } catch {
      setBookingError('Erreur lors de la reservation. Veuillez reessayer.');
    } finally {
      setBooking(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !pkg) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <p className="text-xl text-gray-600 mb-4">{error || 'Package introuvable'}</p>
        <button
          onClick={() => navigate('/search')}
          className="text-blue-600 hover:underline flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Retour aux packages
        </button>
      </div>
    );
  }

  const destination = pkg.destinations;
  const images = pkg.images?.length
    ? pkg.images
    : [destination?.image_url || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e'];
  const included = pkg.included;

  return (
    <div className="min-h-screen bg-gray-50">
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Images + Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Image gallery */}
            <div className="bg-white rounded-xl shadow overflow-hidden">
              <img
                src={images[selectedImage]}
                alt={pkg.name}
                className="w-full h-[400px] object-cover"
              />
              {images.length > 1 && (
                <div className="flex gap-2 p-3 overflow-x-auto">
                  {images.map((img, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedImage(i)}
                      className={`flex-shrink-0 w-20 h-14 rounded-lg overflow-hidden border-2 ${
                        i === selectedImage ? 'border-blue-600' : 'border-transparent'
                      }`}
                    >
                      <img src={img} alt="" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Package info */}
            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{pkg.name}</h1>
                  {destination && (
                    <div className="flex items-center text-gray-500 mt-1">
                      <MapPin className="h-4 w-4 mr-1" />
                      {destination.name}, {destination.country}
                    </div>
                  )}
                </div>
                {destination?.average_rating ? (
                  <div className="flex items-center bg-blue-50 px-3 py-1 rounded-full">
                    <Star className="h-4 w-4 text-yellow-500 fill-current mr-1" />
                    <span className="font-semibold">{destination.average_rating.toFixed(1)}</span>
                  </div>
                ) : null}
              </div>

              <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-6">
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {pkg.duration_days} jours
                </div>
                <div className="flex items-center">
                  <Users className="h-4 w-4 mr-1" />
                  Max {pkg.max_persons} personnes
                </div>
              </div>

              <p className="text-gray-700 leading-relaxed">{pkg.description}</p>
            </div>

            {/* Includes */}
            {included && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Ce qui est inclus</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {included.transport && (
                    <div className="flex items-start gap-3">
                      <Plane className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Transport</p>
                        <p className="text-sm text-gray-600">{included.transport}</p>
                      </div>
                    </div>
                  )}
                  {included.hotel && (
                    <div className="flex items-start gap-3">
                      <Hotel className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Hebergement</p>
                        <p className="text-sm text-gray-600">{included.hotel}</p>
                      </div>
                    </div>
                  )}
                  {included.meals && (
                    <div className="flex items-start gap-3">
                      <UtensilsCrossed className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Repas</p>
                        <p className="text-sm text-gray-600">{included.meals}</p>
                      </div>
                    </div>
                  )}
                  {included.transfers && (
                    <div className="flex items-start gap-3">
                      <ArrowLeft className="h-5 w-5 text-blue-600 mt-0.5 rotate-180" />
                      <div>
                        <p className="font-medium">Transferts</p>
                        <p className="text-sm text-gray-600">{included.transfers}</p>
                      </div>
                    </div>
                  )}
                  {included.activities?.length > 0 && (
                    <div className="flex items-start gap-3 md:col-span-2">
                      <Activity className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Activites</p>
                        <ul className="text-sm text-gray-600 list-disc list-inside">
                          {included.activities.map((a, i) => (
                            <li key={i}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Highlights */}
            {pkg.highlights && pkg.highlights.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Points forts</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {pkg.highlights.map((h, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                      <span className="text-gray-700">{h}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Not included */}
            {pkg.not_included && pkg.not_included.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Non inclus</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {pkg.not_included.map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-gray-600">
                      <span className="text-red-400">-</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Reviews */}
            {pkg.reviews && pkg.reviews.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Avis ({pkg.reviews.length})
                </h2>
                <div className="space-y-4">
                  {pkg.reviews.map((review) => (
                    <div key={review.id} className="border-b last:border-b-0 pb-4 last:pb-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-800">
                          {review.users?.first_name || 'Anonyme'}{' '}
                          {review.users?.last_name?.[0] ? `${review.users.last_name[0]}.` : ''}
                        </span>
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`h-4 w-4 ${
                                i < review.rating
                                  ? 'text-yellow-500 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      {review.comment && (
                        <p className="text-gray-600 text-sm">{review.comment}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: Booking card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow p-6 sticky top-24">
              <div className="text-center mb-6">
                <span className="text-3xl font-bold text-blue-600">
                  {pkg.price_per_person.toFixed(0)} EUR
                </span>
                <span className="text-gray-500"> / personne</span>
              </div>

              {bookingSuccess ? (
                <div className="text-center py-4">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Check className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-lg text-gray-900 mb-2">
                    Reservation confirmee!
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Vous pouvez suivre votre reservation dans votre espace.
                  </p>
                  <button
                    onClick={() => navigate('/bookings')}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                  >
                    Voir mes reservations
                  </button>
                </div>
              ) : (
                <>
                  <div className="space-y-4 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Date de depart
                      </label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        min={pkg.available_from?.split('T')[0]}
                        max={pkg.available_to?.split('T')[0]}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre de personnes
                      </label>
                      <select
                        value={numPersons}
                        onChange={(e) => setNumPersons(parseInt(e.target.value))}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {[...Array(pkg.max_persons)].map((_, i) => (
                          <option key={i + 1} value={i + 1}>
                            {i + 1} personne{i > 0 ? 's' : ''}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="border-t pt-4 mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>{pkg.price_per_person.toFixed(0)} EUR x {numPersons} pers.</span>
                      <span>{(pkg.price_per_person * numPersons).toFixed(0)} EUR</span>
                    </div>
                    <div className="flex justify-between font-semibold text-lg">
                      <span>Total</span>
                      <span className="text-blue-600">
                        {(pkg.price_per_person * numPersons).toFixed(0)} EUR
                      </span>
                    </div>
                  </div>

                  {bookingError && (
                    <p className="text-red-500 text-sm mb-4">{bookingError}</p>
                  )}

                  <button
                    onClick={handleBook}
                    disabled={booking || !startDate}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {booking ? 'Reservation en cours...' : 'Reserver maintenant'}
                  </button>

                  {!user && (
                    <p className="text-xs text-gray-500 text-center mt-2">
                      Vous devez etre connecte pour reserver
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PackageDetail;
