// src/tests/components/WelcomeSection.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

// 1) Mock de react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback: string) => {
      // podremos distinguir keys concretas en el test
      if (key === 'welcome_title') return '¡Bienvenido a ChatApp!';
      return fallback;
    },
  }),
}));

// 2) Importa el componente
import WelcomeSection from '@/components/Welcome';

describe('WelcomeSection', () => {
  it('renders the translated title', () => {
    render(<WelcomeSection />);
    // Esperamos que el H1 contenga la traducción mockeada
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('¡Bienvenido a ChatApp!');
  });

  it('applies the optional className prop', () => {
    render(<WelcomeSection className="my-custom-class" />);
    const container = screen.getByRole('heading', { level: 1 }).parentElement;
    expect(container).toHaveClass('my-custom-class');
  });
});
