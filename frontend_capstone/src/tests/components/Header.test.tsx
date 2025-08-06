import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@/components/ui/sidebar', () => ({
  useSidebar: () => ({ toggleSidebar: vi.fn() }),
}));

vi.mock('@/lib/authContext', () => ({
  useAuth: vi.fn(() => ({ isLoggedIn: false, logout: vi.fn() })),
}));

vi.mock('next-themes', () => ({
  useTheme: vi.fn(() => ({ theme: 'light', setTheme: vi.fn() })),
}));

vi.mock('@/lib/i18n', () => ({
  __esModule: true,
  default: {
    language: 'en',
    changeLanguage: vi.fn(),
  },
}));

vi.mock('@/components/LoginModal', () => ({
  LoginModal: () => <button data-testid="login-btn">Log in</button>,
}));
vi.mock('@/components/SignUpModal', () => ({
  SignupModal: () => <button data-testid="signup-btn">Sign up</button>,
}));

import { Header } from '@/components/Header';
import * as authModule from '@/lib/authContext';
import i18n from '@/lib/i18n';
import * as themeModule from 'next-themes';

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all buttons when logged out', () => {
    render(<Header />);

    const langBtn = screen.getByRole('button', { name: /language_selector_aria/i });
    expect(langBtn).toHaveTextContent('EN');

    expect(screen.getByLabelText(/switch_to_dark/i)).toBeInTheDocument();

    expect(screen.getByTestId('login-btn')).toBeInTheDocument();
    expect(screen.getByTestId('signup-btn')).toBeInTheDocument();
  });

  it('calls changeLanguage on language toggle', () => {
    render(<Header />);
    const langBtn = screen.getByRole('button', { name: /language_selector_aria/i });
    fireEvent.click(langBtn);
    expect(i18n.changeLanguage).toHaveBeenCalledWith('es');
  });

  it('calls setTheme on theme toggle', () => {
    const setTheme = vi.fn();
    (themeModule.useTheme as ReturnType<typeof vi.fn>).mockReturnValue({
      theme: 'light',
      setTheme,
    });

    render(<Header />);
    const themeBtn = screen.getByLabelText(/switch_to_dark/i);
    fireEvent.click(themeBtn);
    expect(setTheme).toHaveBeenCalledWith('dark');
  });

  it('shows logout button when logged in and fires logout', () => {
    const logoutSpy = vi.fn();
    (authModule.useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
      isLoggedIn: true,
      logout: logoutSpy,
    });

    render(<Header />);
    const logoutBtn = screen.getByRole('button', { name: /^logout$/i });
    expect(logoutBtn).toBeInTheDocument();

    fireEvent.click(logoutBtn);
    expect(logoutSpy).toHaveBeenCalled();
  });
});
