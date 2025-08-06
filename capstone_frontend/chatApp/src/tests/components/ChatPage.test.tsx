import { vi } from 'vitest';

if (!window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }));
}

import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

vi.mock('@/components/ChatSidebar', () => ({
  default: () => <div data-testid="mock-sidebar">ChatSidebar</div>,
}));
vi.mock('@/components/ChatWindow', () => ({
  default: ({ chatId }: { chatId: string }) => <div data-testid="mock-window">ChatWindow {chatId}</div>,
}));
vi.mock('@/components/Header', () => ({
  Header: () => <div data-testid="mock-header">Header</div>,
}));
vi.mock('@/components/Welcome', () => ({
  default: () => <div data-testid="mock-welcome">WelcomeSection</div>,
}));

vi.mock('@tanstack/react-router', async () => {
  const actual = (await vi.importActual('@tanstack/react-router')) as object;
  return {
    ...actual,
    useMatch: vi.fn(),
  };
});

import * as auth from '@/lib/authContext';
import * as router from '@tanstack/react-router';

import ChatPage from '@/components/ChatPage';

describe('ChatPage', () => {
  let useAuthSpy: ReturnType<typeof vi.spyOn>;
  const mockedUseMatch = router.useMatch as unknown as ReturnType<typeof vi.fn>;

  beforeEach(() => {
    useAuthSpy = vi.spyOn(auth, 'useAuth').mockReturnValue({ isLoggedIn: false } as any);

    mockedUseMatch.mockReturnValue(undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('when not logged in shows only <WelcomeSection/> and Header', () => {
    render(<ChatPage />);

    expect(screen.getByTestId('mock-header')).toBeInTheDocument();
    expect(screen.getByTestId('mock-welcome')).toBeInTheDocument();

    expect(screen.queryByTestId('mock-sidebar')).toBeNull();
    expect(screen.queryByTestId('mock-window')).toBeNull();
  });

  it('when logged in with no chatId shows sidebar + placeholder', () => {
    useAuthSpy.mockReturnValue({ isLoggedIn: true } as any);
    mockedUseMatch.mockReturnValue({ params: {} } as any);

    render(<ChatPage />);

    expect(screen.getByTestId('mock-sidebar')).toBeInTheDocument();
    expect(screen.getByText('Selecciona un chat a la izquierda…', { exact: false })).toBeInTheDocument();
    expect(screen.queryByTestId('mock-window')).toBeNull();
  });

  it('when logged in with a chatId renders <ChatWindow chatId="foo" />', () => {
    useAuthSpy.mockReturnValue({ isLoggedIn: true } as any);
    mockedUseMatch.mockReturnValue({ params: { chatId: 'foo' } } as any);

    render(<ChatPage />);

    expect(screen.getByTestId('mock-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('mock-window')).toHaveTextContent('ChatWindow foo');
  });
});
