import { useChatMessages } from '@/hooks/useChatMessages';
import ChatBubble from './ChatBubble';
import MessageInput from './MessageInput';

export default function ChatWindow({ chatId }: { chatId: string }) {
  const { messages, isLoading, isError, sendMessage, isSending } = useChatMessages(chatId);

  if (isLoading) return <div>Loading…</div>;
  if (isError) return <div>Error loading messages</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto">
        <div className="mx-auto max-w-7xl px-8 mt-4 space-y-6 dark:bg-gray-900">
          {[...messages].reverse().map(m => (
            <ChatBubble
              key={m.message_id}
              isUser={m.type === 'client'}
              timestamp={new Date(m.created_at)}
              {...(m.image ? { imageUrl: m.content } : { text: m.content })}
            />
          ))}
          {isSending && (
            <ChatBubble
              isLoading
              isUser
            />
          )}
        </div>
      </div>

      <div className="border-t px-8 py-3 dark:border-gray-700 flex items-center space-x-4">
        <div className="flex-1">
          <MessageInput
            onSend={sendMessage}
            disabled={isSending}
          />
        </div>
      </div>
    </div>
  );
}
