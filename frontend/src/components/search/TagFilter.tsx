interface TagFilterProps {
  tags: string[];
  selectedTags: string[];
  onChange: (tags: string[]) => void;
}

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

export const TagFilter: React.FC<TagFilterProps> = ({ tags, selectedTags, onChange }) => {
  const toggle = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onChange(selectedTags.filter((t) => t !== tag));
    } else {
      onChange([...selectedTags, tag]);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Categories
      </label>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const isSelected = selectedTags.includes(tag);
          return (
            <button
              key={tag}
              onClick={() => toggle(tag)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                isSelected
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {TAG_LABELS[tag] || tag}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default TagFilter;
