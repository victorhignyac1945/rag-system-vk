import { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type HelpTab = 'user' | 'dev';

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
  const [activeTab, setActiveTab] = useState<HelpTab>('user');

  if (!isOpen) return null;

  return (
    <div
      className="help-overlay open"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="help-modal">
        <div className="help-header">
          <div className="help-title">
            <HelpCircle width={20} height={20} />
            Справка
          </div>
          <button className="help-close" onClick={onClose}>
            <X width={18} height={18} />
          </button>
        </div>

        <div className="help-tabs">
          <button
            className={`help-tab${activeTab === 'user' ? ' active' : ''}`}
            onClick={() => setActiveTab('user')}
          >
            Для пользователя
          </button>
          <button
            className={`help-tab${activeTab === 'dev' ? ' active' : ''}`}
            onClick={() => setActiveTab('dev')}
          >
            Для разработчика
          </button>
        </div>

        {activeTab === 'user' && (
          <div className="help-body">
            <h2>Что это за приложение</h2>
            <p>RAG-платформа — умный поиск и генерация ответов по вашим документам.</p>
            <h2>Как пользоваться</h2>
            <p>Загрузите файл, URL или посты из VK во вкладке «Источники», затем задайте вопрос в «Поиске» или «Чате».</p>
            <p><em>(полный текст будет позже)</em></p>
          </div>
        )}

        {activeTab === 'dev' && (
          <div className="help-body">
            <h2>Архитектура</h2>
            <p>FastAPI + React + Ollama + BM25 + FAISS + Reranker.</p>
            <h2>Компоненты</h2>
            <p><code>Backend/</code>, <code>Frontend/</code>, <code>Data/</code>.</p>
            <p><em>(полный текст будет позже)</em></p>
          </div>
        )}
      </div>
    </div>
  );
}
