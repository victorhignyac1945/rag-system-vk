import { Search, Sparkles } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export default function SearchBar({ value, onChange, onSubmit }: SearchBarProps) {
  return (
    <div className="search-wrap">
      <Search className="search-icon" width={18} height={18} />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter') onSubmit(); }}
        placeholder="Введите вопрос..."
      />
      <button className="btn btn-primary" onClick={onSubmit}>
        <Sparkles width={15} height={15} />
        Спросить
      </button>
    </div>
  );
}
