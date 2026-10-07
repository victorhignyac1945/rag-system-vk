import { Search, MessageSquare, FolderOpen } from 'lucide-react';
import type { TabId } from '../types';

interface TabsProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const TABS: { id: TabId; label: string; icon: typeof Search }[] = [
  { id: 'search', label: 'Поиск', icon: Search },
  { id: 'chat', label: 'Чат', icon: MessageSquare },
  { id: 'sources', label: 'Источники', icon: FolderOpen },
];

export default function Tabs({ activeTab, onTabChange }: TabsProps) {
  return (
    <div className="tabs-wrap">
      <div className="tabs">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`tab${activeTab === tab.id ? ' active' : ''}`}
              onClick={() => onTabChange(tab.id)}
            >
              <Icon width={15} height={15} />
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
