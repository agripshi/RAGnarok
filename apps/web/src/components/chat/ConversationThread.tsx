import { Text, Badge } from '@fluentui/react-components';
import type { ChatMessageVm } from '../../types/chat';
import type { AnswerStatus } from '../../types/api';

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

export function ConversationThread({ messages }: { messages: ChatMessageVm[] }) {
  return (
    <div style={{ width: '100%', maxWidth: 'var(--rag-max-content)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {messages.map((msg) => (
        <div
          key={msg.id}
          style={{
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%',
            padding: '1rem',
            borderRadius: 'var(--rag-radius-md)',
            background: msg.role === 'user' ? '#e8f3ff' : 'var(--rag-surface)',
            border: '1px solid var(--rag-border)',
          }}
        >
          {msg.isLoading ? (
            <Text>Thinking…</Text>
          ) : (
            <>
              <Text>{msg.content}</Text>
              {msg.status && <div style={{ marginTop: '0.5rem' }}><StatusBadge status={msg.status} /></div>}
              {msg.role === 'assistant' && <SourceCardList sources={msg.sources} />}
            </>
          )}
        </div>
      ))}
    </div>
  );
}
