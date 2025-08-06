// AuthProvider.tsx
import { useLogin, useSignup } from "@/hooks/useAuthMutation";
import { useNavigate } from "@tanstack/react-router";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

interface AuthContextType {
  isLoggedIn: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const loginMut = useLogin();
  const signupMut = useSignup();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Comprobar al montar si la sesión existe en backend
  useEffect(() => {
    fetch("/auth/verify", {
      method: "GET",
      credentials: "include", // <- envía la cookie HttpOnly
    })
      .then((res) => {
        setIsLoggedIn(res.ok);
      })
      .catch(() => {
        setIsLoggedIn(false);
      });
  }, []);

  const login = async (username: string, password: string) => {
    // El backend deja la cookie HttpOnly en /auth/login
    await loginMut.mutateAsync({ username, password });
    setIsLoggedIn(true);
    navigate({ to: "/" });
  };

  const signup = async (username: string, password: string) => {
    // El backend deja la cookie HttpOnly en /auth/signup
    await signupMut.mutateAsync({ username, password });
    setIsLoggedIn(true);
    navigate({ to: "/" });
  };

  const logout = useCallback(async () => {
    await fetch("/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    setIsLoggedIn(false);
    navigate({ to: "/" });
  }, [navigate]);

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
