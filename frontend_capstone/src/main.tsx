import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Outlet, RouterProvider, createRootRoute, createRoute, createRouter } from '@tanstack/react-router';
import { ThemeProvider } from 'next-themes';
import React from 'react';
import ReactDOM from 'react-dom/client';
import ChatPage from './components/ChatPage';
import './index.css';
import { AuthProvider } from './lib/authContext';

const queryClient = new QueryClient();

const Root = () => (
  <AuthProvider>
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem>
      <Outlet />
    </ThemeProvider>
  </AuthProvider>
);

const rootRoute = createRootRoute({ component: Root });

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: ChatPage,
});

export const chatRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/chat/$chatId',
  component: ChatPage,
});

const routeTree = rootRoute.addChildren([indexRoute, chatRoute]);

const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);
