import { Clock, Zap, Hash, Layers } from 'lucide-react';
import type { Metrics as MetricsType } from '../types';

interface MetricsProps {
  metrics: MetricsType;
}

export default function Metrics({ metrics }: MetricsProps) {
  return (
    <div className="metrics">
      <div className="metric">
        <Clock width={12} height={12} />
        Поиск: <span className="metric-value">{metrics.searchTime}</span>
      </div>
      <div className="metric">
        <Zap width={12} height={12} />
        Генерация: <span className="metric-value">{metrics.generationTime}</span>
      </div>
      <div className="metric">
        <Hash width={12} height={12} />
        Токены: <span className="metric-value">{metrics.tokens}</span>
      </div>
      <div className="metric">
        <Layers width={12} height={12} />
        {metrics.method}
      </div>
    </div>
  );
}
