// src/tests/components/ChatSidebar.test.tsx
import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

// 0) Stub out your '@/main' so it never actually mounts anything in tests
vi.mock('@/main', () => ({
  // We only need chatRoute.id in ChatSidebar
  chatRoute: { id: 'chatRouteId' },
}));

// 1) Partial‐mock the router so createRootRoute/createRoute/etc stay intact,
//    but override useNavigate (and useMatch if you need it in other tests):
vi.mock('@tanstack/react-router', async importOriginal => {
  const actual = await importOriginal<typeof import('@tanstack/react-router')>();
  return {
    ...actual,
    useNavigate: () => () => {},
  };
});

// 2) Mock useAuth
vi.mock('@/lib/authContext', () => ({
  useAuth: vi.fn(() => ({ isLoggedIn: false })),
}));

// 3) Mock useChatList
vi.mock('@/hooks/useChatList', () => ({
  useChatList: () => ({
    chats: [
      { chat_id: '1', title: 'A', created_at: '' },
      { chat_id: '2', title: 'B', created_at: '' },
    ],
    isLoading: false,
    isError: false,
    createChat: vi.fn(),
    createLoading: false,
    editChat: vi.fn(),
    deleteChat: vi.fn(),
  }),
}));

import ChatSidebar from '@/components/ChatSidebar';
import { SidebarProvider } from '@/components/ui/sidebar';
import { useAuth } from '@/lib/authContext';

describe('ChatSidebar', () => {
  beforeEach(() => {
    // reset login state before each test
    (useAuth as unknown as ReturnType<typeof vi.fn>).mockReturnValue({ isLoggedIn: false });
  });

  it('renders nothing when not logged in', () => {
    render(
      <SidebarProvider>
        <ChatSidebar />
      </SidebarProvider>
    );

    expect(screen.queryByText('A')).toBeNull();
    expect(screen.queryByText('B')).toBeNull();
  });

  it('renders chat titles when logged in', () => {
    (useAuth as unknown as ReturnType<typeof vi.fn>).mockReturnValue({ isLoggedIn: true });

    render(
      <SidebarProvider>
        <ChatSidebar />
      </SidebarProvider>
    );

    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });
});
