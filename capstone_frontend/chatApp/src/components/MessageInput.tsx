import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface MessageInputProps {
  onSend: (opts: { content: string; image: boolean; negativePrompt?: string }) => void;
  disabled?: boolean;
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [value, setValue] = useState('');
  const [isImage, setIsImage] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onSend({ content: trimmed, image: isImage });
    setValue('');
    setIsImage(false);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center space-x-3 px-4 py-2 bg-white dark:bg-gray-900">
      <Input
        className="flex-1"
        placeholder="Type a message…"
        value={value}
        onChange={e => setValue(e.target.value)}
        disabled={disabled}
      />

      <Label
        htmlFor="request-image"
        className={cn(
          'inline-flex items-center space-x-2 px-2 py-1 rounded-full cursor-pointer select-none',
          isImage ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-800'
        )}>
        <Checkbox
          id="request-image"
          checked={isImage}
          onCheckedChange={checked => setIsImage(!!checked)}
          disabled={disabled}
        />
        <span
          className={cn(
            'text-sm font-medium',
            isImage ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'
          )}>
          Request image
        </span>
      </Label>

      <Button
        type="submit"
        disabled={disabled || !value.trim()}>
        Send
      </Button>
    </form>
  );
}
