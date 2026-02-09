import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search as SearchIcon, Filter } from 'lucide-react';
import { packagesApi } from '../services/api';
import { PackageCard } from '../components/packages/PackageCard';
import { useSetPageContext } from '../contexts/PageContext';
import type { Package } from '../types';

export const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  const setPageContext = useSetPageContext();

  // Filter states
  const [destination, setDestination] = useState(searchParams.get('destination') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [minDuration, setMinDuration] = useState(searchParams.get('min_duration') || '');
  const [maxDuration, setMaxDuration] = useState(searchParams.get('max_duration') || '');

  const fetchPackages = async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {};
      if (destination) params.destination = destination;
      if (minPrice) params.min_price = parseInt(minPrice);
      if (maxPrice) params.max_price = parseInt(maxPrice);
      if (minDuration) params.min_duration = parseInt(minDuration);
      if (maxDuration) params.max_duration = parseInt(maxDuration);

      const result = await packagesApi.list(params);
      setPackages(result.packages);
      setTotal(result.total);
    } catch (error) {
      console.error('Error fetching packages:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPackages();
  }, [searchParams]);

  useEffect(() => {
    setPageContext({
      page: 'search',
      data: {
        filters: {
          destination: destination || undefined,
          min_price: minPrice || undefined,
          max_price: maxPrice || undefined,
          min_duration: minDuration || undefined,
          max_duration: maxDuration || undefined,
        },
        results_count: total,
        results: packages.map((p) => ({
          id: p.id,
          name: p.name,
          price_per_person: p.price_per_person,
        })),
      },
    });
  }, [packages, total, destination, minPrice, maxPrice, minDuration, maxDuration]);

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (destination) params.set('destination', destination);
    if (minPrice) params.set('min_price', minPrice);
    if (maxPrice) params.set('max_price', maxPrice);
    if (minDuration) params.set('min_duration', minDuration);
    if (maxDuration) params.set('max_duration', maxDuration);
    setSearchParams(params);
    setShowFilters(false);
  };

  const clearFilters = () => {
    setDestination('');
    setMinPrice('');
    setMaxPrice('');
    setMinDuration('');
    setMaxDuration('');
    setSearchParams(new URLSearchParams());
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Search Header */}
      <div className="bg-blue-600 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-white mb-6">
            Rechercher un package
          </h1>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-grow">
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Destination, pays ou ville..."
                className="w-full px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="md:hidden bg-blue-500 text-white px-4 py-3 rounded-lg flex items-center justify-center"
            >
              <Filter className="h-5 w-5 mr-2" />
              Filtres
            </button>
            <button
              onClick={handleSearch}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center justify-center"
            >
              <SearchIcon className="h-5 w-5 mr-2" />
              Rechercher
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Filters Sidebar */}
          <div
            className={`${
              showFilters ? 'block' : 'hidden'
            } md:block w-full md:w-64 flex-shrink-0`}
          >
            <div className="bg-white rounded-lg shadow p-6 sticky top-24">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold text-lg">Filtres</h2>
                {(minPrice || maxPrice || minDuration || maxDuration) && (
                  <button
                    onClick={clearFilters}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Effacer
                  </button>
                )}
              </div>

              <div className="space-y-6">
                {/* Price Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget (Euros/pers)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={minPrice}
                      onChange={(e) => setMinPrice(e.target.value)}
                      placeholder="Min"
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(e.target.value)}
                      placeholder="Max"
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duree (jours)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={minDuration}
                      onChange={(e) => setMinDuration(e.target.value)}
                      placeholder="Min"
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      value={maxDuration}
                      onChange={(e) => setMaxDuration(e.target.value)}
                      placeholder="Max"
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <button
                  onClick={handleSearch}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Appliquer
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="flex-grow">
            <div className="flex justify-between items-center mb-6">
              <p className="text-gray-600">
                {loading ? 'Recherche en cours...' : `${total} packages trouves`}
              </p>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div
                    key={i}
                    className="bg-gray-200 rounded-xl h-80 animate-pulse"
                  />
                ))}
              </div>
            ) : packages.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {packages.map((pkg) => (
                  <PackageCard key={pkg.id} pkg={pkg} />
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <SearchIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Aucun package trouve
                </h3>
                <p className="text-gray-500 mb-4">
                  Essayez de modifier vos criteres de recherche
                </p>
                <button
                  onClick={clearFilters}
                  className="text-blue-600 hover:underline"
                >
                  Effacer les filtres
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Search;
