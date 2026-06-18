import { Text, Badge } from '@fluentui/react-components';
import type { ChatMessageVm } from '../../types/chat';
import type { AnswerStatus } from '../../types/api';
import { FeedbackButtons } from './FeedbackButtons';

const STATUS_LABELS: Record<AnswerStatus, string> = {
  ANSWERED: 'Grounded answer',
  NEEDS_CLARIFICATION: 'Needs clarification',
  NOT_FOUND: 'Not found in HR documents',
  ACCESS_DENIED: 'Access denied',
  ERROR: 'Service error',
};

function StatusBadge({ status }: { status: AnswerStatus }) {
  return <Badge appearance="outline">{STATUS_LABELS[status]}</Badge>;
}

function SourceCardList({ sources }: { sources: ChatMessageVm['sources'] }) {
  if (!sources?.length) return null;
  return (
    <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {sources.map((src, i) => (
        <div
          key={`${src.title}-${i}`}
          style={{
            padding: '0.75rem',
            border: '1px solid var(--rag-border)',
            borderRadius: 'var(--rag-radius-md)',
            background: 'var(--rag-bg)',
          }}
        >
          <Text weight="semibold">{src.title}</Text>
          {(src.page || src.section) && (
            <Text size={200} style={{ display: 'block', color: 'var(--rag-muted)' }}>
              {[src.section, src.page ? `p. ${src.page}` : null].filter(Boolean).join(' · ')}
            </Text>
          )}
          {src.sourceUrl && (
            <a href={src.sourceUrl} target="_blank" rel="noreferrer">
              Open source
            </a>
          )}
        </div>
      ))}
    </div>
  );
}

interface ConversationThreadProps {
  messages: ChatMessageVm[];
  token: string;
}

export function ConversationThread({ messages, token }: ConversationThreadProps) {
  return (
    <div className="eng-thread">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`eng-message eng-message--${msg.role}`}
        >
          {msg.isLoading ? (
            <Text style={{ color: 'var(--eng-text)' }}>Thinking…</Text>
          ) : (
            <>
              <Text style={{ color: 'var(--eng-text)' }}>{msg.content}</Text>
              {msg.status && (
                <div style={{ marginTop: '0.5rem' }}>
                  <StatusBadge status={msg.status} />
                </div>
              )}
              {msg.role === 'assistant' && <SourceCardList sources={msg.sources} />}
              {msg.role === 'assistant' && msg.backendMessageId && msg.status === 'ANSWERED' && (
                <FeedbackButtons token={token} messageId={msg.backendMessageId} />
              )}
            </>
          )}
        </div>
      ))}
    </div>
  );
}
