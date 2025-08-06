import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from '@/lib/locales/en.json';
import es from '@/lib/locales/es.json';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    es: { translation: es },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;
