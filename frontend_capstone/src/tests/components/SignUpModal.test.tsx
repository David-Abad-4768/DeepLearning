// src/tests/components/SignUpModal.test.tsx
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

// 1) Mock de Dialog para que el trigger abra el contenido:
vi.mock('@/components/ui/dialog', () => {
  const React = require('react');
  return {
    Dialog: ({ children }: any) => {
      const [open, setOpen] = React.useState(false);
      const triggerWrapper = React.Children.toArray(children)[0] as any;
      const triggerButton = triggerWrapper.props.children;
      return (
        <div>
          {React.cloneElement(triggerButton, {
            onClick: () => setOpen(true),
          })}
          {open && children[1]}
        </div>
      );
    },
    DialogTrigger: ({ children }: any) => <>{children}</>,
    DialogContent: ({ children }: any) => <div data-testid="content">{children}</div>,
    DialogHeader: ({ children }: any) => <div data-testid="header">{children}</div>,
    DialogTitle: ({ children }: any) => <h1>{children}</h1>,
    DialogDescription: ({ children }: any) => <p>{children}</p>,
  };
});

// 2) Resto de mocks de UI:
vi.mock('@/components/ui/button', () => ({ Button: (p: any) => <button {...p} /> }));
vi.mock('@/components/ui/alert', () => ({
  Alert: ({ variant, children }: any) => <div role={variant === 'destructive' ? 'alert' : 'status'}>{children}</div>,
  AlertTitle: (p: any) => <strong {...p} />,
  AlertDescription: (p: any) => <span {...p} />,
}));
vi.mock('@/components/ui/input', () => ({ Input: (p: any) => <input {...p} /> }));
vi.mock('@/components/ui/label', () => ({ Label: (p: any) => <label {...p} /> }));

// 3) Mock de useSignup:
const mutateMock = vi.fn();
vi.mock('@/hooks/useAuthMutation', () => ({ useSignup: () => ({ mutateAsync: mutateMock }) }));

// 4) Mock de traducciones, con opts por defecto:
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts: any = {}) => {
      switch (key) {
        case 'signup':
          return 'Sign up';
        case 'create_an_account':
          return 'Create an account';
        case 'username':
          return 'Username';
        case 'password':
          return 'Password';
        case 'cancel':
          return 'Cancel';
        case 'creating':
          return 'Creating...';
        case 'create_account':
          return 'Create account';
        case 'signup_success':
          return `User ${opts.user} created`;
        case 'error':
          return 'Error';
        default:
          return key;
      }
    },
  }),
}));

// 5) Importa el componente:
import { SignupModal } from '@/components/SignUpModal';

describe('SignupModal', () => {
  beforeEach(() => vi.resetAllMocks());

  it('renders trigger button', () => {
    render(<SignupModal />);
    expect(screen.getByRole('button', { name: 'Sign up' })).toBeInTheDocument();
  });

  it('opens dialog when trigger clicked', async () => {
    render(<SignupModal />);
    expect(screen.queryByTestId('content')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Sign up' }));
    await waitFor(() => expect(screen.getByTestId('content')).toBeInTheDocument());
  });

  it('shows success alert after successful signup', async () => {
    mutateMock.mockResolvedValue({});
    render(<SignupModal />);
    fireEvent.click(screen.getByRole('button', { name: 'Sign up' }));
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'john' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'pass' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('User john created'));
  });

  it('shows error alert when signup fails', async () => {
    mutateMock.mockRejectedValue(new Error('bad request'));
    render(<SignupModal />);
    fireEvent.click(screen.getByRole('button', { name: 'Sign up' }));
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'jane' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: '1234' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('bad request'));
  });
});
