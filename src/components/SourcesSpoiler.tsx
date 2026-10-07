import { useState } from 'react';
import { Library, ChevronDown } from 'lucide-react';
import ChunkCard from './ChunkCard';
import type { Chunk } from '../types';

interface SourcesSpoilerProps {
  chunks: Chunk[];
}

export default function SourcesSpoiler({ chunks }: SourcesSpoilerProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={`spoiler${isOpen ? ' open' : ''}`}>
      <div className="spoiler-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="spoiler-title">
          <Library width={15} height={15} />
          Показать источники
          <span className="spoiler-count">{chunks.length}</span>
        </div>
        <span className="spoiler-arrow">
          <ChevronDown width={16} height={16} />
        </span>
      </div>
      <div className="spoiler-body">
        {chunks.map((chunk) => (
          <ChunkCard key={chunk.id} chunk={chunk} />
        ))}
      </div>
    </div>
  );
}
