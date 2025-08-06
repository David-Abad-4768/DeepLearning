import { SidebarProvider } from '@/components/ui/sidebar';
import { useAuth } from '@/lib/authContext';
import { useMatch } from '@tanstack/react-router';
import ChatSidebar from './ChatSidebar';
import ChatWindow from './ChatWindow';
import { Header } from './Header';
import WelcomeSection from './Welcome';

export default function ChatPage() {
  const { isLoggedIn } = useAuth();
  const match = useMatch({ strict: false });
  const params = match?.params as { chatId?: string } | undefined;
  const chatId = params?.chatId;

  return (
    <SidebarProvider defaultOpen={false}>
      <div className="flex flex-col h-screen">
        <Header />

        <div className="flex flex-1 overflow-hidden">
          {isLoggedIn ? (
            <>
              <ChatSidebar />

              <main className="flex-1 overflow-auto bg-white dark:bg-gray-900">
                {chatId ? (
                  <ChatWindow chatId={chatId} />
                ) : (
                  <div className="flex h-full items-center justify-center text-gray-500">Selecciona un chat a la izquierda…</div>
                )}
              </main>
            </>
          ) : (
            <main className="flex-1 overflow-auto bg-white dark:bg-gray-900">
              <WelcomeSection />
            </main>
          )}
        </div>
      </div>
    </SidebarProvider>
  );
}
