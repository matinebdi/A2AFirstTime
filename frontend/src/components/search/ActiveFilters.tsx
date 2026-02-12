import { X } from 'lucide-react';

interface ActiveFilter {
  key: string;
  label: string;
  value: string;
}

interface ActiveFiltersProps {
  filters: ActiveFilter[];
  onRemove: (key: string) => void;
  onClearAll: () => void;
}

export const ActiveFilters: React.FC<ActiveFiltersProps> = ({ filters, onRemove, onClearAll }) => {
  if (filters.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 mb-4">
      {filters.map((filter) => (
        <span
          key={filter.key}
          className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
        >
          <span className="text-blue-400 font-medium">{filter.label}:</span>
          {filter.value}
          <button
            onClick={() => onRemove(filter.key)}
            className="ml-1 hover:text-blue-900 transition-colors"
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      {filters.length > 1 && (
        <button
          onClick={onClearAll}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Tout effacer
        </button>
      )}
    </div>
  );
};

export default ActiveFilters;
