import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface ChatBubbleProps {
  text?: string;
  imageUrl?: string;
  isUser?: boolean;
  isLoading?: boolean;
  timestamp?: Date;
}

export default function ChatBubble({ text, imageUrl, isUser = false, isLoading = false }: ChatBubbleProps) {
  return (
    <div className={cn('flex mb-2', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'relative max-w-[60%] px-4 py-2 rounded-lg',
          isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        )}>
        {isLoading ? (
          <Loader2
            role="status"
            className="animate-spin w-5 h-5"
          />
        ) : imageUrl ? (
          <img
            src={imageUrl}
            alt="Generated content"
            className="rounded"
          />
        ) : (
          <p>{text}</p>
        )}
      </div>
    </div>
  );
}
