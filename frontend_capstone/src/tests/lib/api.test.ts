import { api, type AuthResponse, type Chat } from '@/lib/api';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const API_BASE = import.meta.env.VITE_API_BASE || 'https://localhost:8443/v1';

describe('api client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  function mockFetch(responseInit: Partial<ResponseInit>, body: any) {
    return vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), {
        status: responseInit.status ?? 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );
  }

  it('login() calls correct endpoint and returns token', async () => {
    const fake: AuthResponse = { access_token: 'tok' };
    global.fetch = mockFetch({ status: 200 }, fake);

    const res = await api.login('u', 'p');
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/auth/login`,
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ username: 'u', password: 'p' }),
      })
    );
    expect(res).toEqual(fake);
  });

  it('signup() calls /user/ and returns token', async () => {
    const fake: AuthResponse = { access_token: 't2' };
    global.fetch = mockFetch({ status: 200 }, fake);

    const res = await api.signup('x', 'y');
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/user/`,
      expect.objectContaining({ method: 'POST', credentials: 'include' })
    );
    expect(res).toEqual(fake);
  });

  it('fetchChats() returns array of chats', async () => {
    const chats: Chat[] = [{ chat_id: '1', title: 'A', created_at: 't1' }];
    global.fetch = mockFetch({ status: 200 }, { error: false, data: { chats } });

    const res = await api.fetchChats();
    expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/chat/`, expect.objectContaining({ credentials: 'include' }));
    expect(res).toEqual(chats);
  });

  it('createChat() posts title and returns created Chat', async () => {
    const c: Chat = { chat_id: '2', title: 'B', created_at: 'now' };
    global.fetch = mockFetch({ status: 200 }, c);

    const res = await api.createChat('B');
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/chat/`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ title: 'B' }),
      })
    );
    expect(res).toEqual(c);
  });

  it('editChat() patches title', async () => {
    const updated: Chat = { chat_id: '2', title: 'BB', created_at: 'now' };
    global.fetch = mockFetch({ status: 200 }, updated);

    const res = await api.editChat('2', 'BB');
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/chat/title`,
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify({ chat_id: '2', title: 'BB' }),
      })
    );
    expect(res).toEqual(updated);
  });

  it('deleteChat() deletes and returns JSON', async () => {
    const ok = { success: true };
    global.fetch = mockFetch({ status: 200 }, ok);

    const res = await api.deleteChat('3');
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/chat/`,
      expect.objectContaining({ method: 'DELETE', body: JSON.stringify({ chat_id: '3' }) })
    );
    expect(res).toEqual(ok);
  });

  it('handleResponse throws generic on non-json or missing detail', async () => {
    global.fetch = vi.fn().mockResolvedValue(new Response('oops', { status: 500 }));
    await expect(api.login('u', 'p')).rejects.toThrow('Error');
  });
});
