import { useRef } from 'react';
import { Spinner } from '@fluentui/react-components';
import { Send24Regular } from '@fluentui/react-icons';
interface ChatComposerProps {
  disabled?: boolean;
  onSubmit: (message: string) => void;
}

export function ChatComposer({ disabled, onSubmit }: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const value = textareaRef.current?.value.trim();
    if (!value) return;
    onSubmit(value);
    if (textareaRef.current) textareaRef.current.value = '';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="eng-composer">
      <textarea
        ref={textareaRef}
        className="eng-composer__textarea"
        placeholder="Message HR HubÔÇª"
        rows={1}
        disabled={disabled}
        onKeyDown={handleKeyDown}
        aria-label="Message HR Hub"
      />
      <button
        type="button"
        className="eng-composer__send"
        disabled={disabled}
        aria-label="Send message"
        onClick={submit}
      >
        {disabled ? <Spinner size="tiny" /> : <Send24Regular />}
      </button>    </div>
  );
}
