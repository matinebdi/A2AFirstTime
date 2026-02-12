import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search as SearchIcon, Filter, SlidersHorizontal, X } from 'lucide-react';
import { packagesApi, destinationsApi } from '../services/api';
import { PackageCard } from '../components/packages/PackageCard';
import { DualRangeSlider } from '../components/search/DualRangeSlider';
import { TagFilter } from '../components/search/TagFilter';
import { ActiveFilters } from '../components/search/ActiveFilters';
import { Pagination } from '../components/search/Pagination';
import { useSetPageContext } from '../contexts/PageContext';
import { PageTransition, FadeIn, StaggerContainer, StaggerItem, AnimatedButton } from '../components/animations';
import type { Package, Destination } from '../types';

const ITEMS_PER_PAGE = 12;
const PRICE_MIN = 0;
const PRICE_MAX = 3000;
const PRICE_STEP = 50;
const DURATION_MIN = 1;
const DURATION_MAX = 21;

const ALL_TAGS = [
  'beach', 'culture', 'adventure', 'nature', 'cuisine',
  'history', 'relaxation', 'wildlife', 'mountains', 'islands',
  'desert', 'tropical', 'urban', 'romantic', 'family',
];

const TAG_LABELS: Record<string, string> = {
  beach: 'Plage',
  culture: 'Culture',
  adventure: 'Aventure',
  nature: 'Nature',
  cuisine: 'Cuisine',
  history: 'Histoire',
  relaxation: 'Detente',
  wildlife: 'Faune',
  mountains: 'Montagne',
  islands: 'Iles',
  desert: 'Desert',
  tropical: 'Tropical',
  urban: 'Urbain',
  romantic: 'Romantique',
  family: 'Famille',
};

const SORT_OPTIONS = [
  { value: 'price_asc', label: 'Prix croissant' },
  { value: 'price_desc', label: 'Prix decroissant' },
  { value: 'duration_asc', label: 'Duree croissante' },
  { value: 'duration_desc', label: 'Duree decroissante' },
  { value: 'name_asc', label: 'Nom A-Z' },
];

export const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [destinations, setDestinations] = useState<Destination[]>([]);

  const setPageContext = useSetPageContext();

  // Read state from URL params
  const destinationId = searchParams.get('destination_id') || '';
  const selectedTags = searchParams.get('tags') ? searchParams.get('tags')!.split(',') : [];
  const priceMin = Number(searchParams.get('min_price')) || PRICE_MIN;
  const priceMax = Number(searchParams.get('max_price')) || PRICE_MAX;
  const durationMin = Number(searchParams.get('min_duration')) || DURATION_MIN;
  const durationMax = Number(searchParams.get('max_duration')) || DURATION_MAX;
  const startDate = searchParams.get('start_date') || '';
  const sortBy = searchParams.get('sort_by') || 'price_asc';
  const currentPage = Number(searchParams.get('page')) || 1;

  // Fetch destinations on mount
  useEffect(() => {
    destinationsApi.list({ limit: 100 }).then(setDestinations).catch(console.error);
  }, []);

  // Helper to update URL params
  const updateParams = useCallback((updates: Record<string, string | undefined>) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === '') {
          next.delete(key);
        } else {
          next.set(key, value);
        }
      }
      return next;
    });
  }, [setSearchParams]);

  // Fetch packages when URL params change
  const fetchPackages = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {};
      if (destinationId) params.destination_id = destinationId;
      if (priceMin > PRICE_MIN) params.min_price = priceMin;
      if (priceMax < PRICE_MAX) params.max_price = priceMax;
      if (durationMin > DURATION_MIN) params.min_duration = durationMin;
      if (durationMax < DURATION_MAX) params.max_duration = durationMax;
      if (selectedTags.length > 0) params.tags = selectedTags.join(',');
      if (startDate) params.start_date = startDate;
      if (sortBy) params.sort_by = sortBy;
      params.limit = ITEMS_PER_PAGE;
      params.offset = (currentPage - 1) * ITEMS_PER_PAGE;

      const result = await packagesApi.list(params);
      setPackages(result.packages);
      setTotal(result.total);
    } catch (error) {
      console.error('Error fetching packages:', error);
    } finally {
      setLoading(false);
    }
  }, [destinationId, priceMin, priceMax, durationMin, durationMax, selectedTags.join(','), startDate, sortBy, currentPage]);

  useEffect(() => {
    fetchPackages();
  }, [fetchPackages]);

  // Page context for AI agent
  useEffect(() => {
    const destName = destinations.find((d) => d.id === destinationId)?.name;
    setPageContext({
      page: 'search',
      data: {
        filters: {
          destination: destName || undefined,
          min_price: priceMin > PRICE_MIN ? priceMin : undefined,
          max_price: priceMax < PRICE_MAX ? priceMax : undefined,
          min_duration: durationMin > DURATION_MIN ? durationMin : undefined,
          max_duration: durationMax < DURATION_MAX ? durationMax : undefined,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          start_date: startDate || undefined,
          sort_by: sortBy !== 'price_asc' ? sortBy : undefined,
        },
        results_count: total,
        results: packages.map((p) => ({
          id: p.id,
          name: p.name,
          price_per_person: p.price_per_person,
        })),
      },
    });
  }, [packages, total, destinationId, destinations, priceMin, priceMax, durationMin, durationMax, selectedTags.join(','), startDate, sortBy]);

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  // Build active filters list
  const activeFilters = useMemo(() => {
    const filters: { key: string; label: string; value: string }[] = [];
    if (destinationId) {
      const dest = destinations.find((d) => d.id === destinationId);
      filters.push({ key: 'destination_id', label: 'Destination', value: dest?.name || destinationId });
    }
    if (priceMin > PRICE_MIN || priceMax < PRICE_MAX) {
      filters.push({ key: 'price', label: 'Budget', value: `${priceMin} - ${priceMax} EUR` });
    }
    if (durationMin > DURATION_MIN || durationMax < DURATION_MAX) {
      filters.push({ key: 'duration', label: 'Duree', value: `${durationMin} - ${durationMax} jours` });
    }
    for (const tag of selectedTags) {
      filters.push({ key: `tag_${tag}`, label: 'Tag', value: TAG_LABELS[tag] || tag });
    }
    if (startDate) {
      filters.push({ key: 'start_date', label: 'Date', value: startDate });
    }
    return filters;
  }, [destinationId, destinations, priceMin, priceMax, durationMin, durationMax, selectedTags.join(','), startDate]);

  const handleRemoveFilter = (key: string) => {
    if (key === 'destination_id') {
      updateParams({ destination_id: undefined, page: undefined });
    } else if (key === 'price') {
      updateParams({ min_price: undefined, max_price: undefined, page: undefined });
    } else if (key === 'duration') {
      updateParams({ min_duration: undefined, max_duration: undefined, page: undefined });
    } else if (key.startsWith('tag_')) {
      const tag = key.replace('tag_', '');
      const newTags = selectedTags.filter((t) => t !== tag);
      updateParams({ tags: newTags.length > 0 ? newTags.join(',') : undefined, page: undefined });
    } else if (key === 'start_date') {
      updateParams({ start_date: undefined, page: undefined });
    }
  };

  const clearFilters = () => {
    setSearchParams(new URLSearchParams());
  };

  const hasActiveFilters = activeFilters.length > 0;

  return (
    <PageTransition>
      <div className="min-h-screen">
        {/* Header */}
        <FadeIn direction="down">
          <div className="bg-blue-600 py-8">
            <div className="max-w-7xl mx-auto px-4">
              <h1 className="text-3xl font-bold text-white mb-6">
                Rechercher un package
              </h1>
              <div className="flex flex-col md:flex-row gap-4">
                {/* Destination dropdown */}
                <div className="flex-grow">
                  <select
                    value={destinationId}
                    onChange={(e) => updateParams({ destination_id: e.target.value || undefined, page: undefined })}
                    className="w-full px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white text-gray-800"
                  >
                    <option value="">Toutes les destinations</option>
                    {destinations.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}, {d.country}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="md:hidden bg-blue-500 text-white px-4 py-3 rounded-lg flex items-center justify-center"
                >
                  <Filter className="h-5 w-5 mr-2" />
                  Filtres
                </button>
                <AnimatedButton
                  onClick={() => updateParams({ page: undefined })}
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center justify-center"
                >
                  <SearchIcon className="h-5 w-5 mr-2" />
                  Rechercher
                </AnimatedButton>
              </div>
            </div>
          </div>
        </FadeIn>

        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Filters Sidebar */}
            <div
              className={`${
                showFilters ? 'block' : 'hidden'
              } md:block w-full md:w-72 flex-shrink-0`}
            >
              <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow p-6 sticky top-24">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-2">
                    <SlidersHorizontal className="h-5 w-5 text-gray-600" />
                    <h2 className="font-semibold text-lg">Filtres</h2>
                  </div>
                  {hasActiveFilters && (
                    <button
                      onClick={clearFilters}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Effacer
                    </button>
                  )}
                  {/* Mobile close */}
                  <button
                    onClick={() => setShowFilters(false)}
                    className="md:hidden p-1 hover:bg-gray-100 rounded"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Destination (mobile) */}
                  <div className="md:hidden">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Destination
                    </label>
                    <select
                      value={destinationId}
                      onChange={(e) => updateParams({ destination_id: e.target.value || undefined, page: undefined })}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Toutes</option>
                      {destinations.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}, {d.country}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Tags */}
                  <TagFilter
                    tags={ALL_TAGS}
                    selectedTags={selectedTags}
                    onChange={(tags) => updateParams({ tags: tags.length > 0 ? tags.join(',') : undefined, page: undefined })}
                  />

                  {/* Price Range Slider */}
                  <DualRangeSlider
                    label="Budget (EUR/pers)"
                    min={PRICE_MIN}
                    max={PRICE_MAX}
                    step={PRICE_STEP}
                    valueMin={priceMin}
                    valueMax={priceMax}
                    formatLabel={(v) => `${v} EUR`}
                    onChange={(min, max) => updateParams({
                      min_price: min > PRICE_MIN ? String(min) : undefined,
                      max_price: max < PRICE_MAX ? String(max) : undefined,
                      page: undefined,
                    })}
                  />

                  {/* Duration Range Slider */}
                  <DualRangeSlider
                    label="Duree (jours)"
                    min={DURATION_MIN}
                    max={DURATION_MAX}
                    step={1}
                    valueMin={durationMin}
                    valueMax={durationMax}
                    formatLabel={(v) => `${v}j`}
                    onChange={(min, max) => updateParams({
                      min_duration: min > DURATION_MIN ? String(min) : undefined,
                      max_duration: max < DURATION_MAX ? String(max) : undefined,
                      page: undefined,
                    })}
                  />

                  {/* Date Picker */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date de depart
                    </label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => updateParams({ start_date: e.target.value || undefined, page: undefined })}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Apply button (mobile) */}
                  <button
                    onClick={() => setShowFilters(false)}
                    className="md:hidden w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                  >
                    Voir les resultats
                  </button>
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="flex-grow">
              {/* Results header */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
                <p className="text-gray-600">
                  {loading ? 'Recherche en cours...' : `${total} package${total !== 1 ? 's' : ''} trouve${total !== 1 ? 's' : ''}`}
                </p>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-500">Trier par</label>
                  <select
                    value={sortBy}
                    onChange={(e) => updateParams({ sort_by: e.target.value, page: undefined })}
                    className="px-3 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    {SORT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Active Filters */}
              <ActiveFilters
                filters={activeFilters}
                onRemove={handleRemoveFilter}
                onClearAll={clearFilters}
              />

              {/* Grid */}
              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Array.from({ length: 6 }, (_, i) => (
                    <div
                      key={i}
                      className="bg-gray-200 rounded-xl h-80 animate-pulse"
                    />
                  ))}
                </div>
              ) : packages.length > 0 ? (
                <>
                  <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {packages.map((pkg) => (
                      <StaggerItem key={pkg.id}>
                        <PackageCard pkg={pkg} />
                      </StaggerItem>
                    ))}
                  </StaggerContainer>
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={(page) => updateParams({ page: page > 1 ? String(page) : undefined })}
                  />
                </>
              ) : (
                <FadeIn>
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
                </FadeIn>
              )}
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Search;
