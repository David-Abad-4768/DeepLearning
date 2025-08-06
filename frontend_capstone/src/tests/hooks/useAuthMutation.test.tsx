import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useLogin, useSignup } from '@/hooks/useAuthMutation';
import { api, type AuthResponse } from '@/lib/api';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useLogin & useSignup hooks', () => {
  const fakeResponse: AuthResponse = { access_token: 'tok_123' };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('useLogin: successful login via mutateAsync', async () => {
    const loginMock = vi.spyOn(api, 'login').mockResolvedValue(fakeResponse);

    const { result } = renderHook(() => useLogin(), { wrapper: createWrapper() });

    let returned: AuthResponse | undefined;
    await act(async () => {
      returned = await result.current.mutateAsync({ username: 'u', password: 'p' });
    });

    expect(loginMock).toHaveBeenCalledWith('u', 'p');
    expect(returned).toEqual(fakeResponse);
  });

  it('useLogin: mutation error is surfaced', async () => {
    const error = new Error('login failed');
    vi.spyOn(api, 'login').mockRejectedValue(error);

    const { result } = renderHook(() => useLogin(), { wrapper: createWrapper() });

    let caught: unknown;
    await act(async () => {
      try {
        await result.current.mutateAsync({ username: 'bad', password: 'creds' });
      } catch (e) {
        caught = e;
      }
    });

    expect(caught).toBe(error);
  });

  it('useSignup: successful signup via mutateAsync', async () => {
    const signupMock = vi.spyOn(api, 'signup').mockResolvedValue(fakeResponse);

    const { result } = renderHook(() => useSignup(), { wrapper: createWrapper() });

    let returned: AuthResponse | undefined;
    await act(async () => {
      returned = await result.current.mutateAsync({ username: 'newu', password: 'newp' });
    });

    expect(signupMock).toHaveBeenCalledWith('newu', 'newp');
    expect(returned).toEqual(fakeResponse);
  });

  it('useSignup: mutation error is surfaced', async () => {
    const error = new Error('signup failed');
    vi.spyOn(api, 'signup').mockRejectedValue(error);

    const { result } = renderHook(() => useSignup(), { wrapper: createWrapper() });

    let caught: unknown;
    await act(async () => {
      try {
        await result.current.mutateAsync({ username: 'nouser', password: 'nopass' });
      } catch (e) {
        caught = e;
      }
    });

    expect(caught).toBe(error);
  });
});
