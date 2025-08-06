// src/tests/components/ChatWindow.test.tsx
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

// 1) Stub out useChatMessages
vi.mock('@/hooks/useChatMessages', () => ({
  useChatMessages: vi.fn(),
}));

// 2) Stub out ChatBubble
vi.mock('@/components/ChatBubble', () => ({
  __esModule: true,
  default: ({ text, imageUrl, isUser, isLoading }: any) => {
    if (isLoading) return <div data-testid="mock-loading">loading…</div>;
    if (imageUrl) return <div data-testid="mock-image">{imageUrl}</div>;
    return (
      <div
        data-testid="mock-text"
        data-user={isUser}>
        {text}
      </div>
    );
  },
}));

// 3) Stub out MessageInput
vi.mock('@/components/MessageInput', () => ({
  __esModule: true,
  default: ({ onSend, disabled }: any) => (
    <button
      data-testid="mock-input"
      disabled={disabled}
      onClick={() => onSend({ content: 'foo', image: false })}>
      send
    </button>
  ),
}));

import ChatWindow from '@/components/ChatWindow';
import { useChatMessages } from '@/hooks/useChatMessages';

describe('ChatWindow', () => {
  const mockedHook = useChatMessages as unknown as ReturnType<typeof vi.fn>;

  it('shows loading state', () => {
    mockedHook.mockReturnValue({
      messages: [],
      isLoading: true,
      isError: false,
      sendMessage: vi.fn(),
      isSending: false,
    });
    render(<ChatWindow chatId="abc" />);
    expect(screen.getByText('Loading…')).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockedHook.mockReturnValue({
      messages: [],
      isLoading: false,
      isError: true,
      sendMessage: vi.fn(),
      isSending: false,
    });
    render(<ChatWindow chatId="abc" />);
    expect(screen.getByText('Error loading messages')).toBeInTheDocument();
  });

  it('renders messages and input, and calls onSend', () => {
    const fakeMessages = [
      { message_id: '1', content: 'Hi', created_at: '', type: 'client', image: false },
      { message_id: '2', content: 'ImgURL', created_at: '', type: 'system', image: true },
    ];
    const sendSpy = vi.fn();

    mockedHook.mockReturnValue({
      messages: fakeMessages,
      isLoading: false,
      isError: false,
      sendMessage: sendSpy,
      isSending: false,
    });

    render(<ChatWindow chatId="abc" />);

    // The two stubbed ChatBubble outputs:
    const texts = screen.getAllByTestId('mock-text');
    expect(texts.map(el => el.textContent)).toEqual(['Hi']);
    expect(texts[0].getAttribute('data-user')).toBe('true');

    const images = screen.getByTestId('mock-image');
    expect(images.textContent).toBe('ImgURL');

    // Input button enabled
    const btn = screen.getByTestId('mock-input');
    expect(btn).toBeEnabled();

    // simulate click
    fireEvent.click(btn);
    expect(sendSpy).toHaveBeenCalledWith({ content: 'foo', image: false });
  });

  it('disables input when isSending=true', () => {
    mockedHook.mockReturnValue({
      messages: [],
      isLoading: false,
      isError: false,
      sendMessage: vi.fn(),
      isSending: true,
    });
    render(<ChatWindow chatId="abc" />);
    expect(screen.getByTestId('mock-input')).toBeDisabled();
  });
});
