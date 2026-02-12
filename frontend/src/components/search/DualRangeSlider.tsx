import { useCallback } from 'react';

interface DualRangeSliderProps {
  min: number;
  max: number;
  valueMin: number;
  valueMax: number;
  step?: number;
  onChange: (min: number, max: number) => void;
  formatLabel?: (value: number) => string;
  label: string;
}

export const DualRangeSlider: React.FC<DualRangeSliderProps> = ({
  min,
  max,
  valueMin,
  valueMax,
  step = 1,
  onChange,
  formatLabel = (v) => String(v),
  label,
}) => {
  const getPercent = useCallback(
    (value: number) => ((value - min) / (max - min)) * 100,
    [min, max]
  );

  const minPercent = getPercent(valueMin);
  const maxPercent = getPercent(valueMax);

  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Math.min(Number(e.target.value), valueMax - step);
    onChange(value, valueMax);
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Math.max(Number(e.target.value), valueMin + step);
    onChange(valueMin, value);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>{formatLabel(valueMin)}</span>
        <span>{formatLabel(valueMax)}</span>
      </div>
      <div className="dual-range-slider">
        <div className="slider-track" />
        <div
          className="slider-range"
          style={{ left: `${minPercent}%`, width: `${maxPercent - minPercent}%` }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={valueMin}
          onChange={handleMinChange}
          className="slider-thumb slider-thumb--left"
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={valueMax}
          onChange={handleMaxChange}
          className="slider-thumb slider-thumb--right"
        />
      </div>
    </div>
  );
};

export default DualRangeSlider;
