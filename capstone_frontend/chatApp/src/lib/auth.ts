import * as jwtLib from "jwt-decode";

const jwt_decode = (jwtLib as any).default ?? jwtLib;

export interface JWTPayload {
  sub: string;
  username?: string;
}

export function getUserFromCookie(): {
  user_id: string;
  username: string;
} | null {
  const match = document.cookie.match(/(?:^|; )access_token=([^;]+)/);
  if (!match) return null;
  const token = decodeURIComponent(match[1]);
  try {
    const payload = jwt_decode(token) as JWTPayload;
    return {
      user_id: payload.sub,
      username: payload.username ?? payload.sub,
    };
  } catch {
    return null;
  }
}

export function clearAuthCookie() {
  document.cookie =
    "access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT;";
}
