import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { useChatList } from '@/hooks/useChatList';
import type { Chat } from '@/lib/api';
import { useAuth } from '@/lib/authContext';
import { cn } from '@/lib/utils';
import { chatRoute } from '@/main';
import { useNavigate } from '@tanstack/react-router';
import { Edit2, MessageCircle, PlusCircle, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function ChatSidebar() {
  const { t } = useTranslation();
  const { open, setOpen } = useSidebar();
  const navigate = useNavigate();
  const { chats, isLoading, isError, createChat, createLoading, editChat, deleteChat } = useChatList();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [newTitle, setNewTitle] = useState('');

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [chatToDelete, setChatToDelete] = useState<Chat | null>(null);
  const { isLoggedIn } = useAuth();
  if (!isLoggedIn) return null;

  function openCreateDialog() {
    setCurrentChat(null);
    setNewTitle('');
    setDialogOpen(true);
  }

  function openEditDialog(chat: Chat) {
    setCurrentChat(chat);
    setNewTitle(chat.title);
    setDialogOpen(true);
  }

  function handleDialogSubmit() {
    const title = newTitle.trim();
    if (!title) return;
    if (currentChat) {
      editChat({ chat_id: currentChat.chat_id, title });
    } else {
      createChat({ title });
    }
    setDialogOpen(false);
  }

  function openDeleteDialog(chat: Chat) {
    setChatToDelete(chat);
    setDeleteDialogOpen(true);
  }

  function handleDeleteConfirm() {
    if (chatToDelete) {
      deleteChat({ chat_id: chatToDelete.chat_id });
    }
    setDeleteDialogOpen(false);
  }

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 bg-opacity-50 z-30 transition-opacity',
          open ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
        onClick={() => setOpen(false)}
      />

      <Sidebar
        className={cn(
          'fixed top-0 left-0 z-40 h-full w-64 shadow-lg transform transition-transform duration-300',
          open ? 'translate-x-0' : '-translate-x-full'
        )}>
        <SidebarHeader className="px-4 py-3 border-b border-gray-200">
          <SidebarMenu>
            <SidebarMenuItem>
              <Dialog
                open={dialogOpen}
                onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <SidebarMenuButton
                    onClick={openCreateDialog}
                    disabled={createLoading}
                    className={cn(
                      'w-full h-10 flex items-center px-4 text-sm font-medium rounded-md',
                      'bg-blue-600 text-white hover:bg-blue-700',
                      'dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700'
                    )}>
                    <PlusCircle className="w-5 h-5" />
                    <span className="ml-2">{t('new_chat')}</span>
                  </SidebarMenuButton>
                </DialogTrigger>

                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{currentChat ? t('edit_chat') : t('new_chat')}</DialogTitle>
                    <DialogDescription>{currentChat ? t('enter_new_title') : t('enter_chat_title')}</DialogDescription>
                  </DialogHeader>
                  <Input
                    value={newTitle}
                    onChange={e => setNewTitle(e.target.value)}
                    autoFocus
                    className="mt-2"
                  />
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => setDialogOpen(false)}>
                      {t('cancel')}
                    </Button>
                    <Button
                      onClick={handleDialogSubmit}
                      disabled={!newTitle.trim()}>
                      {t('save')}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        {/* CONTENT */}
        <SidebarContent className="flex-1 overflow-y-auto  text-white">
          <SidebarMenu className="space-y-1 p-2">
            {isLoading && <div className="px-4 py-2 text-sm text-gray-500">{t('loading')}…</div>}
            {isError && <div className="px-4 py-2 text-sm text-red-500">{t('error_loading_chats')}</div>}

            {chats.map(chat => (
              <SidebarMenuItem key={chat.chat_id}>
                <SidebarMenuButton
                  onClick={() => {
                    navigate({ to: chatRoute.id, params: { chatId: chat.chat_id } });
                    setOpen(false);
                  }}
                  className="bg-blue-600">
                  <div className="flex items-center space-x-2">
                    <MessageCircle className="w-5 h-5" />
                    <span className="font-medium">{chat.title}</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span
                      onClick={e => {
                        e.stopPropagation();
                        openEditDialog(chat);
                      }}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700">
                      <Edit2 className="w-4 h-4" />
                    </span>

                    <Dialog
                      open={deleteDialogOpen}
                      onOpenChange={setDeleteDialogOpen}>
                      <DialogTrigger asChild>
                        <span
                          onClick={e => {
                            e.stopPropagation();
                            openDeleteDialog(chat);
                          }}
                          className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700">
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </span>
                      </DialogTrigger>

                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>{t('confirm_delete_title')}</DialogTitle>
                          <DialogDescription>{t('confirm_delete_message')}</DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setDeleteDialogOpen(false)}>
                            {t('cancel')}
                          </Button>
                          <Button
                            onClick={handleDeleteConfirm}
                            variant="destructive">
                            {t('delete')}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}

            {!isLoading && chats.length === 0 && <div className="px-4 py-2 text-sm text-gray-500">{t('no_chats_yet')}</div>}
          </SidebarMenu>
        </SidebarContent>

        <SidebarFooter className="px-4 py-3 border-t border-gray-200 dark:border-gray-700" />
      </Sidebar>
    </>
  );
}
