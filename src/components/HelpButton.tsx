import { HelpCircle } from 'lucide-react';

interface HelpButtonProps {
  onClick: () => void;
}

export default function HelpButton({ onClick }: HelpButtonProps) {
  return (
    <button className="btn btn-ghost" onClick={onClick}>
      <HelpCircle width={14} height={14} />
      Справка
    </button>
  );
}
