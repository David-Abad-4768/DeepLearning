import ChatBubble from '@/components/ChatBubble';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

describe('ChatBubble component', () => {
  it('renders user text on the right with blue background', () => {
    render(
      <ChatBubble
        text="Hello user"
        isUser
      />
    );
    const bubble = screen.getByText('Hello user').closest('div');
    // debe tener la clase de fondo azul de usuario
    expect(bubble).toHaveClass('bg-blue-500');
    // alineación a la derecha
    expect(bubble?.parentElement).toHaveClass('justify-end');
  });

  it('renders system text on the left with gray background', () => {
    render(<ChatBubble text="Hello system" />);
    const bubble = screen.getByText('Hello system').closest('div');
    expect(bubble).toHaveClass('bg-gray-200');
    expect(bubble?.parentElement).toHaveClass('justify-start');
  });

  it('renders an image when imageUrl is provided', () => {
    render(<ChatBubble imageUrl="https://foo/bar.png" />);
    const img = screen.getByRole('img', { name: /Generated content/i });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'https://foo/bar.png');
  });

  it('renders a loader when isLoading is true', () => {
    render(<ChatBubble isLoading />);
    const spinner = screen.getByRole('status'); // we'll add role
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('animate-spin');
  });
});
