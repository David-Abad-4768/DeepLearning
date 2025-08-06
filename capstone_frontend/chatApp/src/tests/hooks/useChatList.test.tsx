import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useChatList } from '@/hooks/useChatList';
import { api, type Chat } from '@/lib/api';
import { useAuth } from '@/lib/authContext';

// 1) Mock useAuth
vi.mock('@/lib/authContext', () => ({
  useAuth: vi.fn(),
}));

// 2) Spy on API methods
const fetchChatsMock = vi.spyOn(api, 'fetchChats');
const createChatMock = vi.spyOn(api, 'createChat');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useChatList', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('returns empty list when not logged in', () => {
    // @ts-expect-error override
    (useAuth as any).mockReturnValue({ isLoggedIn: false });

    const { result } = renderHook(() => useChatList(), { wrapper: createWrapper() });

    expect(result.current.chats).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isError).toBe(false);
    expect(fetchChatsMock).not.toHaveBeenCalled();
  });

  it('fetches chats when logged in', async () => {
    const fakeChats: Chat[] = [{ chat_id: '1', title: 'Hello', created_at: 'now' }];
    // @ts-expect-error override
    (useAuth as any).mockReturnValue({ isLoggedIn: true });
    fetchChatsMock.mockResolvedValue(fakeChats);

    const { result } = renderHook(() => useChatList(), { wrapper: createWrapper() });

    // wait for loading to finish
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(fetchChatsMock).toHaveBeenCalled();
    expect(result.current.chats).toEqual(fakeChats);
    expect(result.current.isError).toBe(false);
  });

  it('createChat calls API and invalidates cache', async () => {
    // @ts-expect-error override
    (useAuth as any).mockReturnValue({ isLoggedIn: true });
    fetchChatsMock.mockResolvedValue([]);
    createChatMock.mockResolvedValue({ chat_id: '2', title: 'New', created_at: 'now' });

    const { result } = renderHook(() => useChatList(), { wrapper: createWrapper() });

    // wait for initial fetch to complete
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.createChat({ title: 'New' });
    });

    expect(createChatMock).toHaveBeenCalledWith('New');
    // should refetch after invalidate
    expect(fetchChatsMock).toHaveBeenCalledTimes(2);
  });
});
