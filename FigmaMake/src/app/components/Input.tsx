import { Search } from 'lucide-react';

interface InputProps {
  placeholder: string;
  value?: string;
  onChange?: (value: string) => void;
  type?: 'text' | 'search';
  className?: string;
  autoFocus?: boolean;
}

export function Input({ placeholder, value, onChange, type = 'text', className = '', autoFocus = false }: InputProps) {
  return (
    <div className="relative">
      {type === 'search' && (
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" style={{ color: 'var(--app-text-secondary)' }} />
      )}
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        autoFocus={autoFocus}
        autoComplete="off"
        autoCorrect="off"
        spellCheck="false"
        className={`w-full px-4 py-3 rounded-xl border outline-none transition-colors ${
          type === 'search' ? 'pl-12' : ''
        } ${className}`}
        style={{ 
          backgroundColor: 'var(--app-surface)',
          borderColor: 'var(--app-border)',
          color: 'var(--app-text-primary)'
        }}
      />
    </div>
  );
}
