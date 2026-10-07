export interface Chunk {
  id: string;
  source: string;
  sourceIcon: 'book-open' | 'file-text' | 'globe';
  score: number;
  text: string;
}

export interface Source {
  id: string;
  icon: 'book-open' | 'file-text' | 'globe';
  label: string;
}

export interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  sources?: Source[];
}

export interface Metrics {
  searchTime: string;
  generationTime: string;
  tokens: string;
  method: string;
}

export interface Model {
  id: string;
  name: string;
  size: string;
}

export type TabId = 'search' | 'chat' | 'sources';
