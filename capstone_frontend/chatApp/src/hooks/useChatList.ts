import { api, type Chat } from '@/lib/api';
import { useAuth } from '@/lib/authContext';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function useChatList() {
  const qc = useQueryClient();
  const { isLoggedIn } = useAuth();

  const {
    data: raw = [],
    isLoading,
    isError,
  } = useQuery<Chat[]>({
    queryKey: ['chats'],
    queryFn: async () => {
      const chats = await api.fetchChats();
      return chats;
    },
    enabled: isLoggedIn,
    staleTime: 5 * 60 * 1000,
  });

  const chats = Array.isArray(raw) ? raw : [];

  const createChat = useMutation({
    mutationFn: ({ title }: { title: string }) => api.createChat(title),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['chats'] }),
  });

  const editChat = useMutation({
    mutationFn: ({ chat_id, title }: { chat_id: string; title: string }) => api.editChat(chat_id, title),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['chats'] }),
  });

  const deleteChat = useMutation({
    mutationFn: ({ chat_id }: { chat_id: string }) => api.deleteChat(chat_id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['chats'] }),
  });

  return {
    chats,
    isLoading,
    isError,
    createChat: createChat.mutateAsync,
    createLoading: createChat.isPending,
    editChat: editChat.mutateAsync,
    deleteChat: deleteChat.mutateAsync,
  };
}
