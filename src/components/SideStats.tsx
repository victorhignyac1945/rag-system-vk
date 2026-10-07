import { BarChart3 } from 'lucide-react';

export default function SideStats() {
  return (
    <aside className="side-note">
      <h4>
        <BarChart3 width={12} height={12} />
        Статистика индекса
      </h4>
      <div className="stat-row">
        <span className="stat-label">Всего чанков</span>
        <span className="stat-value">20 184</span>
      </div>
      <div className="stat-row">
        <span className="stat-label">Источников</span>
        <span className="stat-value">4</span>
      </div>
      <div className="stat-row">
        <span className="stat-label">Документов</span>
        <span className="stat-value">12 847</span>
      </div>
      <div className="stat-row">
        <span className="stat-label">Обновлено</span>
        <span className="stat-value">5 мин</span>
      </div>
    </aside>
  );
}
