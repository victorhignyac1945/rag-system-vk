import { BookOpen, FileText, Globe, Database } from 'lucide-react';

interface SourceItem {
  icon: typeof BookOpen;
  name: string;
  chunks: number;
  updated: string;
}

const SOURCES: SourceItem[] = [
  { icon: BookOpen, name: 'lua-5.4-manual', chunks: 8420, updated: '5 мин назад' },
  { icon: FileText, name: 'programming_in_lua.pdf', chunks: 6230, updated: '12 мин назад' },
  { icon: Globe, name: 'habr.com/lua', chunks: 3890, updated: '1 час назад' },
  { icon: Database, name: 'wiki.lua.org', chunks: 1644, updated: '2 часа назад' },
];

export default function SourcesTab() {
  return (
    <div className="chat-scroll">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '4px' }}>
        {SOURCES.map((source, idx) => {
          const Icon = source.icon;
          return (
            <div key={idx} className="chunk">
              <div className="chunk-header">
                <div className="chunk-source">
                  <Icon width={14} height={14} />
                  {source.name}
                </div>
                <div className="chunk-score">
                  {source.chunks.toLocaleString('ru')} чанков
                </div>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Обновлено: {source.updated}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
