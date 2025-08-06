import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useChatMessages } from '@/hooks/useChatMessages';
import { api, type Message } from '@/lib/api';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useChatMessages', () => {
  const fakeMessages: Message[] = [
    { message_id: 'm1', chat_id: 'c1', content: 'hello', created_at: 'now', type: 'client', image: false },
    { message_id: 'm2', chat_id: 'c1', content: 'world', created_at: 'now', type: 'system', image: false },
  ];

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('returns empty list and does not fetch when chatId is empty', () => {
    const getMessagesSpy = vi.spyOn(api, 'getMessages');
    const { result } = renderHook(() => useChatMessages(''), { wrapper: createWrapper() });

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isError).toBe(false);
    expect(getMessagesSpy).not.toHaveBeenCalled();
  });

  it('fetches messages when chatId is provided', async () => {
    const getMessagesSpy = vi.spyOn(api, 'getMessages').mockResolvedValue(fakeMessages);

    const { result } = renderHook(() => useChatMessages('c1'), { wrapper: createWrapper() });

    // initially loading = true
    expect(result.current.isLoading).toBe(true);

    // wait for fetch to finish
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(getMessagesSpy).toHaveBeenCalledWith('c1', 20, 0);
    expect(result.current.messages).toEqual(fakeMessages);
    expect(result.current.isError).toBe(false);
  });

  it('sendMessage calls api.postMessage and invalidates messages query', async () => {
    const getMessagesSpy = vi.spyOn(api, 'getMessages').mockResolvedValue(fakeMessages);
    const postMessageSpy = vi.spyOn(api, 'postMessage').mockResolvedValue({
      message_id: 'm3',
      chat_id: 'c1',
      content: 'new msg',
      created_at: 'now',
      type: 'client',
      image: false,
    });

    const { result } = renderHook(() => useChatMessages('c1'), { wrapper: createWrapper() });

    // wait for initial load
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      result.current.sendMessage({ content: 'new msg', image: false });
    });

    expect(postMessageSpy).toHaveBeenCalledWith('c1', 'new msg', false, undefined);

    // after success it should refetch messages
    await waitFor(() => expect(getMessagesSpy).toHaveBeenCalledTimes(2));
  });
});
