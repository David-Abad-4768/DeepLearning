import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@/components/ui/input', () => ({
  Input: (props: any) => (
    <input
      {...props}
      data-testid="text-input"
    />
  ),
}));
vi.mock('@/components/ui/label', () => ({
  Label: (props: any) => (
    <label
      {...props}
      data-testid="image-label"
    />
  ),
}));
vi.mock('@/components/ui/button', () => ({
  Button: (props: any) => (
    <button
      {...props}
      data-testid="send-button"
    />
  ),
}));

vi.mock('@/components/ui/checkbox', () => ({
  Checkbox: (props: any) => {
    const { checked, onCheckedChange, ...rest } = props;
    return (
      <input
        type="checkbox"
        {...rest}
        data-testid="image-checkbox"
        defaultChecked={!!checked}
        onChange={e => onCheckedChange?.(e.target.checked)}
      />
    );
  },
}));

import MessageInput from '@/components/MessageInput';

describe('MessageInput', () => {
  let onSend: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onSend = vi.fn();
    render(<MessageInput onSend={onSend} />);
  });

  it('renders a text input, a checkbox label and a send button (disabled)', () => {
    expect(screen.getByTestId('text-input')).toBeInTheDocument();
    expect(screen.getByTestId('image-checkbox')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeDisabled();
  });

  it('enables the send button when the user types something', () => {
    const input = screen.getByTestId('text-input');
    const send = screen.getByTestId('send-button');

    fireEvent.change(input, { target: { value: 'hello' } });
    expect(send).toBeEnabled();

    fireEvent.change(input, { target: { value: '' } });
    expect(send).toBeDisabled();
  });

  it('toggles the image checkbox and label styling', () => {
    const checkbox = screen.getByTestId('image-checkbox');
    const labelSpan = screen.getByTestId('image-label').querySelector('span')!;

    expect(checkbox).not.toBeChecked();

    fireEvent.click(labelSpan);
    expect(checkbox).toBeChecked();

    fireEvent.click(labelSpan);
    expect(checkbox).not.toBeChecked();
  });

  it('calls onSend with content and image=false by default, then clears input & checkbox', () => {
    const input = screen.getByTestId('text-input');
    const checkbox = screen.getByTestId('image-checkbox');
    const form = input.closest('form')!;

    fireEvent.change(input, { target: { value: 'ping' } });
    expect(checkbox).not.toBeChecked();

    fireEvent.submit(form);
    expect(onSend).toHaveBeenCalledWith({ content: 'ping', image: false });
    expect(input).toHaveValue('');
    expect(checkbox).not.toBeChecked();
  });

  it('calls onSend with image=true when checkbox is checked', () => {
    const input = screen.getByTestId('text-input');
    const checkbox = screen.getByTestId('image-checkbox');
    const form = input.closest('form')!;

    fireEvent.change(input, { target: { value: 'draw me' } });
    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();

    fireEvent.submit(form);
    expect(onSend).toHaveBeenCalledWith({ content: 'draw me', image: true });
  });
});
