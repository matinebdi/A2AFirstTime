import { useState, useEffect, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { Link, useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Users, CreditCard, Loader2 } from 'lucide-react';
import { bookingsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useSetPageContext } from '../contexts/PageContext';
import { PageTransition, FadeIn, AnimatedLinkButton } from '../components/animations';
import type { Booking } from '../types';

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100'}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const PaymentBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    unpaid: 'bg-orange-100 text-orange-800',
    paid: 'bg-green-100 text-green-800',
    refunded: 'bg-purple-100 text-purple-800',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100'}`}>
      {status === 'unpaid' ? 'Non paye' : status === 'paid' ? 'Paye' : 'Rembourse'}
    </span>
  );
};

export const Bookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [payingBookingId, setPayingBookingId] = useState<string | null>(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const setPageContext = useSetPageContext();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchBookings();
  }, [user, navigate]);

  useEffect(() => {
    setPageContext({
      page: 'bookings',
      data: {
        count: bookings.length,
        bookings: bookings.map((b) => ({
          id: b.id,
          package_name: b.packages?.name,
          status: b.status,
          start_date: b.start_date,
          total_price: b.total_price,
          num_persons: b.num_persons,
        })),
      },
    });
  }, [bookings]);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const data = await bookingsApi.list();
      setBookings(data);
    } catch (error) {
      console.error('Error fetching bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePay = async (bookingId: string) => {
    setPayingBookingId(bookingId);
    try {
      // Paiement désactivé - contactez l'administrateur
      alert('Le paiement en ligne n\'est pas encore disponible. Contactez-nous pour finaliser votre réservation.');
    } finally {
      setPayingBookingId(null);
    }
  };

  const handleCancel = async (bookingId: string) => {
    if (!confirm('Etes-vous sur de vouloir annuler cette reservation?')) return;
    try {
      await bookingsApi.cancel(bookingId);
      fetchBookings();
    } catch (error) {
      console.error('Error cancelling booking:', error);
    }
  };

  const columnDefs = useMemo<ColDef[]>(() => [
    {
      headerName: 'Destination',
      field: 'packages.destinations.name',
      flex: 1,
      cellRenderer: (params: { data: Booking }) => (
        <div className="flex items-center h-full">
          <MapPin className="h-4 w-4 mr-2 text-gray-400" />
          <span>{params.data.packages?.destinations?.name}</span>
        </div>
      ),
    },
    {
      headerName: 'Package',
      field: 'packages.name',
      flex: 1,
    },
    {
      headerName: 'Dates',
      field: 'start_date',
      width: 180,
      cellRenderer: (params: { data: Booking }) => (
        <div className="flex items-center h-full">
          <Calendar className="h-4 w-4 mr-2 text-gray-400" />
          <span>{new Date(params.data.start_date).toLocaleDateString('fr-FR')}</span>
        </div>
      ),
    },
    {
      headerName: 'Voyageurs',
      field: 'num_persons',
      width: 120,
      cellRenderer: (params: { data: Booking }) => (
        <div className="flex items-center h-full">
          <Users className="h-4 w-4 mr-2 text-gray-400" />
          <span>{params.data.num_persons}</span>
        </div>
      ),
    },
    {
      headerName: 'Total',
      field: 'total_price',
      width: 120,
      cellRenderer: (params: { data: Booking }) => (
        <span className="font-semibold text-blue-600">
          {params.data.total_price.toFixed(0)} Euros
        </span>
      ),
    },
    {
      headerName: 'Statut',
      field: 'status',
      width: 120,
      cellRenderer: (params: { data: Booking }) => <StatusBadge status={params.data.status} />,
    },
    {
      headerName: 'Paiement',
      field: 'payment_status',
      width: 120,
      cellRenderer: (params: { data: Booking }) => <PaymentBadge status={params.data.payment_status} />,
    },
    {
      headerName: 'Actions',
      field: 'actions',
      width: 200,
      cellRenderer: (params: { data: Booking }) => {
        const booking = params.data;
        return (
          <div className="flex items-center gap-2 h-full">
            {booking.status === 'pending' && booking.payment_status === 'unpaid' && (
              <>
                <button
                  onClick={() => handlePay(booking.id)}
                  disabled={payingBookingId === booking.id}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-blue-300 flex items-center"
                >
                  {payingBookingId === booking.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      <CreditCard className="h-4 w-4 mr-1" />
                      Payer
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleCancel(booking.id)}
                  className="px-3 py-1 bg-red-100 text-red-600 text-sm rounded hover:bg-red-200"
                >
                  Annuler
                </button>
              </>
            )}
            {booking.status === 'confirmed' && (
              <Link
                to={`/bookings/${booking.id}`}
                className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
              >
                Details
              </Link>
            )}
          </div>
        );
      },
    },
  ], [payingBookingId]);

  const defaultColDef = useMemo(() => ({
    sortable: true,
    filter: true,
    resizable: true,
  }), []);

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
                <h1 className="text-3xl font-bold text-gray-900">Mes Reservations</h1>
                <p className="text-gray-600 mt-2">
                  Gerez vos voyages et suivez vos paiements
                </p>
              </div>
              <AnimatedLinkButton
                to="/search"
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Nouvelle reservation
              </AnimatedLinkButton>
            </div>
          </FadeIn>

          {bookings.length === 0 ? (
            <FadeIn delay={0.2}>
              <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow p-16 text-center">
                <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-700 mb-2">
                  Aucune reservation
                </h2>
                <p className="text-gray-500 mb-4">
                  Vous n'avez pas encore de reservation
                </p>
                <Link
                  to="/search"
                  className="text-blue-600 hover:underline font-medium"
                >
                  Rechercher un package
                </Link>
              </div>
            </FadeIn>
          ) : (
            <FadeIn delay={0.2}>
              <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow overflow-hidden">
                <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
                  <AgGridReact
                    rowData={bookings}
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    pagination={true}
                    paginationPageSize={10}
                    rowHeight={60}
                    animateRows={true}
                  />
                </div>
              </div>
            </FadeIn>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default Bookings;
