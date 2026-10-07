import { BookOpen, FileText, Globe } from 'lucide-react';
import type { Chunk } from '../types';

interface ChunkCardProps {
  chunk: Chunk;
}

const ICON_MAP: Record<Chunk['sourceIcon'], typeof BookOpen> = {
  'book-open': BookOpen,
  'file-text': FileText,
  'globe': Globe,
};

export default function ChunkCard({ chunk }: ChunkCardProps) {
  const Icon = ICON_MAP[chunk.sourceIcon];

  return (
    <div className="chunk">
      <div className="chunk-header">
        <div className="chunk-source">
          <Icon width={12} height={12} />
          {chunk.source}
        </div>
        <div className="chunk-score">
          {chunk.score}%
          <div className="score-bar">
            <div className="score-fill" style={{ width: `${chunk.score}%` }} />
          </div>
        </div>
      </div>
      <div
        className="chunk-text"
        dangerouslySetInnerHTML={{ __html: chunk.text }}
      />
    </div>
  );
}
