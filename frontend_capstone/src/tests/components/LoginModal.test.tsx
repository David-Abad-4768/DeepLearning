import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mockLogin = vi.fn();
vi.mock('@/lib/authContext', () => ({
  useAuth: () => ({ login: mockLogin }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: any) => {
      if (key === 'login_success' && opts) return `Logged in as ${opts.user}`;
      return key;
    },
  }),
}));

import { LoginModal } from '@/components/LoginModal';

describe('LoginModal', () => {
  beforeEach(() => {
    mockLogin.mockReset();
  });

  it('renders the login trigger button', () => {
    render(<LoginModal />);
    expect(screen.getByRole('button', { name: /^login$/i })).toBeInTheDocument();
  });

  it('opens dialog when trigger clicked', () => {
    render(<LoginModal />);
    expect(screen.queryByLabelText('username')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));
    expect(screen.getByLabelText('username')).toBeInTheDocument();
    expect(screen.getByLabelText('password')).toBeInTheDocument();
  });

  it('shows success alert after successful login', async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<LoginModal />);
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));
    fireEvent.change(screen.getByLabelText('username'), { target: { value: 'alice' } });
    fireEvent.change(screen.getByLabelText('password'), { target: { value: 'secret' } });
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));

    await waitFor(() => {
      expect(screen.getByText('success')).toBeInTheDocument();
      expect(screen.getByText('Logged in as alice')).toBeInTheDocument();
    });
  });

  it('shows error alert when login throws', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Bad credentials'));
    render(<LoginModal />);
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));
    fireEvent.change(screen.getByLabelText('username'), { target: { value: 'bob' } });
    fireEvent.change(screen.getByLabelText('password'), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));

    await waitFor(() => {
      expect(screen.getByText('error')).toBeInTheDocument();
      expect(screen.getByText('Bad credentials')).toBeInTheDocument();
    });
  });

  it('clears alerts and form when dialog is closed', async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<LoginModal />);
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));
    fireEvent.change(screen.getByLabelText('username'), { target: { value: 'user1' } });
    fireEvent.change(screen.getByLabelText('password'), { target: { value: 'pass1' } });
    fireEvent.click(screen.getByRole('button', { name: /^login$/i }));

    await waitFor(() => screen.getByText('Logged in as user1'));

    fireEvent.click(screen.getByRole('button', { name: /^cancel$/i }));

    await waitFor(() => {
      expect(screen.queryByLabelText('username')).toBeNull();
      expect(screen.queryByText('Logged in as user1')).toBeNull();
      expect(screen.queryByText('error')).toBeNull();
    });
  });
});
