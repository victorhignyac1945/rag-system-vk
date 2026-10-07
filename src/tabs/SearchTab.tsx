import SearchBar from '../components/SearchBar';
import Metrics from '../components/Metrics';
import ChatArea from '../components/ChatArea';
import SourcesSpoiler from '../components/SourcesSpoiler';
import type { Message, Chunk, Metrics as MetricsType } from '../types';

interface SearchTabProps {
  query: string;
  onQueryChange: (v: string) => void;
  onSubmit: () => void;
  messages: Message[];
  chunks: Chunk[];
  metrics: MetricsType;
}

export default function SearchTab({
  query,
  onQueryChange,
  onSubmit,
  messages,
  chunks,
  metrics,
}: SearchTabProps) {
  return (
    <>
      <SearchBar value={query} onChange={onQueryChange} onSubmit={onSubmit} />
      <Metrics metrics={metrics} />
      <ChatArea messages={messages} />
      <SourcesSpoiler chunks={chunks} />
    </>
  );
}
