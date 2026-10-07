import type { Chunk, Message, Metrics } from '../types';

const MOCK_CHUNKS: Chunk[] = [
  {
    id: '1',
    source: 'lua-5.4-manual · Раздел 3.3.1',
    sourceIcon: 'book-open',
    score: 94,
    text: 'Переменные в Lua могут быть <mark>глобальными</mark> или <mark>локальными</mark>. Локальные переменные создаются с помощью ключевого слова <mark>local</mark>: <code>local x = 10</code>. Область видимости локальной переменной начинается сразу после её объявления и продолжается до конца блока.',
  },
  {
    id: '2',
    source: 'programming_in_lua.pdf · Глава 4',
    sourceIcon: 'file-text',
    score: 87,
    text: 'Используйте <mark>local</mark> везде, где это возможно. Глобальные переменные создают нагрузку на виртуальную таблицу окружения и могут вызывать конфликты имён между модулями.',
  },
  {
    id: '3',
    source: 'habr.com/lua · Статья «Lua за 15 минут»',
    sourceIcon: 'globe',
    score: 79,
    text: 'В отличие от Python, в Lua нет явного объявления типа. Переменная появляется в момент присваивания. <mark>local x = 5</mark> — локальная, <mark>x = 5</mark> — глобальная.',
  },
];

const MOCK_MESSAGES: Message[] = [
  {
    id: '1',
    role: 'user',
    content: 'Как объявить переменную в Lua?',
  },
  {
    id: '2',
    role: 'ai',
    content: 'В Lua переменные бывают <strong>глобальными</strong> и <strong>локальными</strong>. Для создания локальной используйте ключевое слово <code>local</code>: <code>local x = 10</code>.<br/><br/>Локальные переменные имеют область видимости от точки объявления до конца блока. <strong>Рекомендуется</strong> использовать <code>local</code> везде — глобальные переменные засоряют окружение и создают конфликты имён между модулями.',
    sources: [
      { id: '1', icon: 'book-open', label: 'lua-5.4-manual §3.3.1' },
      { id: '2', icon: 'file-text', label: 'programming_in_lua.pdf гл.4' },
      { id: '3', icon: 'globe', label: 'habr.com/lua' },
    ],
  },
];

const MOCK_METRICS: Metrics = {
  searchTime: '487 мс',
  generationTime: '2.1 сек',
  tokens: '142',
  method: 'BM25 + FAISS + Rerank',
};

export async function fetchChunks(): Promise<Chunk[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(MOCK_CHUNKS), 100);
  });
}

export async function fetchMessages(): Promise<Message[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(MOCK_MESSAGES), 100);
  });
}

export async function fetchMetrics(): Promise<Metrics> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(MOCK_METRICS), 100);
  });
}
