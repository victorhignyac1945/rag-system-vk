import ChatMessage from './ChatMessage';
import type { Message } from '../types';

interface ChatAreaProps {
  messages: Message[];
  isStreaming?: boolean;
}

export default function ChatArea({ messages, isStreaming }: ChatAreaProps) {
  return (
    <div className="chat-scroll">
      <div className="chat">
        {messages.map((msg, idx) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            isStreaming={isStreaming && idx === messages.length - 1}
          />
        ))}
      </div>
    </div>
  );
}
