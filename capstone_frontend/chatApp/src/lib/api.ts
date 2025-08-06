const API_BASE = import.meta.env.VITE_API_BASE || "https://0.0.0.0:8443/api/v1";

export interface Chat {
  chat_id: string;
  title: string;
  created_at: string;
}

export interface Message {
  message_id: string;
  chat_id: string;
  content: string;
  created_at: string;
  type: "client" | "system";
  image: boolean;
}

export interface AuthResponse {
  access_token: string;
}

interface ErrorResponse {
  detail?: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as ErrorResponse).detail || res.statusText || "Error");
  }
  return res.json();
}

export const api = {
  login: (username: string, password: string) =>
    fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ username, password }),
    }).then<AuthResponse>(handleResponse),

  // SIGNUP endpoint is /user/, server should set same cookie
  signup: (username: string, password: string) =>
    fetch(`${API_BASE}/user/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ username, password }),
    }).then<AuthResponse>(handleResponse),

  // LOGOUT: server will clear the HttpOnly cookie
  logout: () =>
    fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
      },
    }).then((res) => {
      if (!res.ok) throw new Error("Logout failed");
    }),

  // From here on out we rely purely on credentials: 'include'
  fetchChats: () =>
    fetch(`${API_BASE}/chat/`, {
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then<{ error: boolean; data: { chats: Chat[] } }>(handleResponse)
      .then((r) => r.data.chats),

  createChat: (title: string) =>
    fetch(`${API_BASE}/chat/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ title }),
    }).then<Chat>(handleResponse),

  editChat: (chat_id: string, title: string) =>
    fetch(`${API_BASE}/chat/title`, {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ chat_id, title }),
    }).then<Chat>(handleResponse),

  deleteChat: (chat_id: string) =>
    fetch(`${API_BASE}/chat/`, {
      method: "DELETE",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ chat_id }),
    }).then((res) => {
      if (!res.ok) throw new Error("Delete chat failed");
      return res.json();
    }),

  getMessages: (chat_id: string, limit = 20, offset = 0) =>
    fetch(
      `${API_BASE}/message/chats/${chat_id}/messages?limit=${limit}&offset=${offset}`,
      {
        credentials: "include",
        headers: { Accept: "application/json" },
      },
    )
      .then<{ data: Message[] }>(handleResponse)
      .then((r) => r.data),

  postMessage: (
    chat_id: string,
    content: string,
    image = false,
    negativePrompt?: string,
  ) =>
    fetch(`${API_BASE}/message/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(
        image
          ? { chat_id, content, image, negative_prompt: negativePrompt }
          : { chat_id, content, image },
      ),
    }).then<Message>(handleResponse),
};

// alias
export const getChats = api.fetchChats;
