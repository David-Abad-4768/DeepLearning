import { api, type AuthResponse } from "@/lib/api";
import { useMutation, type UseMutationResult } from "@tanstack/react-query";

type Credentials = { username: string; password: string };

export function useLogin(): UseMutationResult<
  AuthResponse,
  Error,
  Credentials
> {
  return useMutation<AuthResponse, Error, Credentials>({
    mutationFn: ({ username, password }) => api.login(username, password),
  });
}

export function useSignup(): UseMutationResult<
  AuthResponse,
  Error,
  Credentials
> {
  return useMutation<AuthResponse, Error, Credentials>({
    mutationFn: ({ username, password }) => api.signup(username, password),
  });
}
