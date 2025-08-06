import { useIsMobile } from '@/hooks/use-mobile';
import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const MOBILE_BREAKPOINT = 768;

// A tiny component that reads the hook and renders “mobile” or “desktop”
function TestComponent() {
  const isMobile = useIsMobile();
  return <div data-testid="result">{isMobile ? 'mobile' : 'desktop'}</div>;
}

describe('useIsMobile', () => {
  beforeEach(() => {
    // Mock matchMedia to return a minimal MediaQueryList
    vi.spyOn(window, 'matchMedia').mockImplementation(query => {
      // matches must reflect window.innerWidth < MOBILE_BREAKPOINT
      const mql = {
        matches: window.innerWidth < MOBILE_BREAKPOINT,
        addEventListener: () => {},
        removeEventListener: () => {},
        // for older browsers:
        addListener: () => {},
        removeListener: () => {},
        media: query,
        onchange: null,
        dispatchEvent: () => false,
      };
      return mql as unknown as MediaQueryList;
    });
  });

  it('renders "desktop" when window.innerWidth ≥ breakpoint', () => {
    window.innerWidth = MOBILE_BREAKPOINT;
    render(<TestComponent />);
    expect(screen.getByTestId('result')).toHaveTextContent('desktop');
  });

  it('renders "mobile" when window.innerWidth < breakpoint', () => {
    window.innerWidth = MOBILE_BREAKPOINT - 1;
    render(<TestComponent />);
    expect(screen.getByTestId('result')).toHaveTextContent('mobile');
  });
});
