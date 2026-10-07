import { Bot, BookOpen, FileText, Globe } from 'lucide-react';
import type { Message, Source } from '../types';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
}

const ICON_MAP: Record<Source['icon'], typeof BookOpen> = {
  'book-open': BookOpen,
  'file-text': FileText,
  'globe': Globe,
};

export default function ChatMessage({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`msg${isUser ? ' user' : ''}`}>
      {isUser ? (
        <>
          <div className="bubble user">{message.content}</div>
          <div className="avatar user">Я</div>
        </>
      ) : (
        <>
          <div className="avatar ai">
            <Bot width={16} height={16} />
          </div>
          <div className="bubble ai">
            <span dangerouslySetInnerHTML={{ __html: message.content }} />
            {isStreaming && <span className="cursor" />}
            {message.sources && message.sources.length > 0 && (
              <div className="src-badges">
                {message.sources.map((source) => {
                  const Icon = ICON_MAP[source.icon];
                  return (
                    <span key={source.id} className="src-badge">
                      <Icon width={11} height={11} />
                      {source.label}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
