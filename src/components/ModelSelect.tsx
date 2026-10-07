import { useState, useRef, useEffect } from 'react';
import { Cpu, ChevronDown, Check } from 'lucide-react';
import type { Model } from '../types';

interface ModelSelectProps {
  models: Model[];
  selectedModel: string;
  onSelect: (name: string) => void;
}

export default function ModelSelect({ models, selectedModel, onSelect }: ModelSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  return (
    <div className="model-select" ref={ref}>
      <button className="model-btn" onClick={() => setIsOpen(!isOpen)}>
        <Cpu width={14} height={14} />
        <span>{selectedModel}</span>
        <ChevronDown className="chevron" width={14} height={14} />
      </button>
      {isOpen && (
        <div className="model-menu">
          {models.map((model) => (
            <div
              key={model.id}
              className={`model-item${model.name === selectedModel ? ' active' : ''}`}
              onClick={() => {
                onSelect(model.name);
                setIsOpen(false);
              }}
            >
              <span>{model.name}</span>
              <span className="size">{model.size}</span>
              {model.name === selectedModel && <Check width={12} height={12} />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
