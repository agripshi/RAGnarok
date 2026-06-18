import { Button, Textarea, Spinner } from '@fluentui/react-components';
import { Send24Regular } from '@fluentui/react-icons';

interface ChatComposerProps {
  disabled?: boolean;
  onSubmit: (message: string) => void;
}

export function ChatComposer({ disabled, onSubmit }: ChatComposerProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const value = e.currentTarget.value.trim();
      if (value) {
        onSubmit(value);
        e.currentTarget.value = '';
      }
    }
  };

  return (
    <div
      style={{
        width: '100%',
        maxWidth: 'var(--rag-max-content)',
        background: 'var(--rag-surface)',
        borderRadius: 'var(--rag-radius-lg)',
        boxShadow: 'var(--rag-shadow-soft)',
        padding: '0.75rem 1rem',
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'flex-end',
      }}
    >
      <Textarea
        placeholder="Message HR Assistant"
        resize="none"
        rows={2}
        disabled={disabled}
        onKeyDown={handleKeyDown}
        style={{ flex: 1, border: 'none', boxShadow: 'none' }}
      />
      <Button
        appearance="primary"
        icon={disabled ? <Spinner size="tiny" /> : <Send24Regular />}
        disabled={disabled}
        aria-label="Send message"
        onClick={() => {
          const el = document.querySelector('textarea[placeholder="Message HR Assistant"]') as HTMLTextAreaElement | null;
          const value = el?.value.trim();
          if (value) {
            onSubmit(value);
            if (el) el.value = '';
          }
        }}
      />
    </div>
  );
}
