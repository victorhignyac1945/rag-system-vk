import { useState } from 'react';
import { RefreshCw, Sparkles } from 'lucide-react';
import FloatingShapes from './components/FloatingShapes';
import ModelSelect from './components/ModelSelect';
import HelpButton from './components/HelpButton';
import HelpModal from './components/HelpModal';
import StatusBar from './components/StatusBar';
import Tabs from './components/Tabs';
import SideStats from './components/SideStats';
import SearchTab from './tabs/SearchTab';
import ChatTab from './tabs/ChatTab';
import SourcesTab from './tabs/SourcesTab';
import { useHelpModal } from './hooks/useHelpModal';
import type { TabId, Model, Message, Chunk, Metrics } from './types';

const MODELS: Model[] = [
  { id: '1', name: 'qwen3.5:9b', size: '6.6 GB' },
  { id: '2', name: 'gemma4:12b', size: '7.6 GB' },
  { id: '3', name: 'deepseek-r1:8b', size: '5.2 GB' },
  { id: '4', name: 'qwen2.5-coder:7b', size: '4.7 GB' },
  { id: '5', name: 'gpt-oss:20b', size: '13 GB' },
  { id: '6', name: 'codellama:7b', size: '3.8 GB' },
];

const INITIAL_MESSAGES: Message[] = [
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

const INITIAL_CHUNKS: Chunk[] = [
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

const INITIAL_METRICS: Metrics = {
  searchTime: '487 мс',
  generationTime: '2.1 сек',
  tokens: '142',
  method: 'BM25 + FAISS + Rerank',
};

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('search');
  const [selectedModel, setSelectedModel] = useState('qwen3.5:9b');
  const [query, setQuery] = useState('Как объявить переменную в Lua?');
  const [messages] = useState<Message[]>(INITIAL_MESSAGES);
  const [chunks] = useState<Chunk[]>(INITIAL_CHUNKS);
  const [metrics] = useState<Metrics>(INITIAL_METRICS);
  const helpModal = useHelpModal();

  return (
    <>
      <div className="bg" />
      <FloatingShapes />

      <div className="app">
        <header className="header">
          <div className="logo">
            <div className="logo-mark">
              <Sparkles width={20} height={20} />
            </div>
            <div className="logo-text">
              <h1>RAG-платформа</h1>
              <p>Умный поиск и ответы по любым источникам</p>
            </div>
          </div>
          <div className="header-right">
            <ModelSelect
              models={MODELS}
              selectedModel={selectedModel}
              onSelect={setSelectedModel}
            />
            <HelpButton onClick={helpModal.open} />
            <StatusBar />
            <button className="btn btn-ghost">
              <RefreshCw width={14} height={14} />
              Переиндексировать
            </button>
          </div>
        </header>

        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

        <div className="content">
          <div className="main-col">
            {activeTab === 'search' && (
              <SearchTab
                query={query}
                onQueryChange={setQuery}
                onSubmit={() => {}}
                messages={messages}
                chunks={chunks}
                metrics={metrics}
              />
            )}
            {activeTab === 'chat' && (
              <ChatTab messages={messages} />
            )}
            {activeTab === 'sources' && (
              <SourcesTab />
            )}
          </div>
          <SideStats />
        </div>
      </div>

      <HelpModal isOpen={helpModal.isOpen} onClose={helpModal.close} />
    </>
  );
}
