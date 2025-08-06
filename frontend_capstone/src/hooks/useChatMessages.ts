import { api, type Message } from '@/lib/api';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function useChatMessages(chatId: string) {
  const qc = useQueryClient();

  const {
    data: messages = [],
    isLoading,
    isError,
  } = useQuery<Message[]>({
    queryKey: ['messages', chatId],
    queryFn: () => api.getMessages(chatId, 20, 0),
    enabled: !!chatId,
  });

  const { mutate: sendMessage, isPending: isSending } = useMutation({
    mutationFn: (opts: { content: string; image: boolean; negativePrompt?: string }) =>
      api.postMessage(chatId, opts.content, opts.image, opts.negativePrompt),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages', chatId] }),
  });

  return { messages, isLoading, isError, sendMessage, isSending };
}
