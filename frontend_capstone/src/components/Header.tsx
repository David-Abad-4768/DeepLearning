import { LoginModal } from '@/components/LoginModal';
import { SignupModal } from '@/components/SignUpModal';
import { Button } from '@/components/ui/button';
import { useSidebar } from '@/components/ui/sidebar';
import { useAuth } from '@/lib/authContext';
import i18n from '@/lib/i18n';
import { ES, US } from 'country-flag-icons/react/3x2';
import { LogOut, Menu, Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export function Header() {
  const { toggleSidebar } = useSidebar();
  const { isLoggedIn, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { t } = useTranslation();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const raw = i18n.language || 'en';
  const base = raw.split('-')[0];
  const currentLang = ['en', 'es'].includes(base) ? base : 'en';

  function toggleLang() {
    const next = currentLang === 'en' ? 'es' : 'en';
    i18n.changeLanguage(next);
  }

  function toggleTheme() {
    setTheme(theme === 'light' ? 'dark' : 'light');
  }

  return (
    <header className="w-screen bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-8 flex items-center justify-between h-16">
        <button
          onClick={toggleSidebar}
          className="p-2 !bg-blue-500 !itext-white dark:text-gray-300 dark:hover:text-white  
  ">
          <Menu className="w-6 h-6" />
        </button>

        <div className="flex items-center space-x-4">
          <button
            onClick={toggleLang}
            aria-label={t('language_selector_aria')}
            className="flex items-center space-x-1 !bg-blue-500 !text-white">
            {currentLang === 'en' ? (
              <US
                className="w-5 h-5 "
                title="English"
              />
            ) : (
              <ES
                className="w-5 h-5"
                title="Español"
              />
            )}
            <span className="text-sm font-medium">{currentLang.toUpperCase()}</span>
          </button>

          {mounted && (
            <button
              onClick={toggleTheme}
              aria-label={theme === 'light' ? t('switch_to_dark') : t('switch_to_light')}
              className="!bg-blue-500 !text-white">
              {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            </button>
          )}

          {isLoggedIn ? (
            <Button
              size="sm"
              onClick={logout}
              className="!bg-blue-500 !text-white flex items-center space-x-1">
              <LogOut className="w-5 h-5" />
              <span>{t('logout')}</span>
            </Button>
          ) : (
            <>
              <LoginModal />
              <SignupModal />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
