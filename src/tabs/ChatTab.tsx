import ChatArea from '../components/ChatArea';
import type { Message } from '../types';

interface ChatTabProps {
  messages: Message[];
}

export default function ChatTab({ messages }: ChatTabProps) {
  return <ChatArea messages={messages} />;
}
