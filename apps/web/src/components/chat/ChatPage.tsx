import { useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendChatMessage, ApiError } from '../../api/chatApi';
import { useChatStore } from '../../store/chatStore';
import type { TeamsContextPayload } from '../../types/api';
import { ChatComposer } from './ChatComposer';
import { ConversationThread } from './ConversationThread';

interface ChatPageProps {
  token: string;
  teamsContext: TeamsContextPayload;
  onConversationChange?: () => void;
}

export function ChatPage({ token, teamsContext, onConversationChange }: ChatPageProps) {
  const {
    conversationId,
    messages,
    isSending,
    setConversationId,
    addMessage,
    updateMessage,
    setSending,
    setAccessDenied,
    setGlobalError,
  } = useChatStore();

  const handleSubmit = useCallback(
    async (text: string) => {
      const userMsgId = uuidv4();
      const loadingId = uuidv4();
      addMessage({
        id: userMsgId,
        role: 'user',
        content: text,
        createdAt: new Date().toISOString(),
      });
      addMessage({
        id: loadingId,
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
        isLoading: true,
      });
      setSending(true);
      setGlobalError(null);

      try {
        const response = await sendChatMessage(token, {
          conversationId,
          message: text,
          teamsContext,
        });
        setConversationId(response.conversationId);
        updateMessage(loadingId, {
          isLoading: false,
          content: response.answer,
          status: response.status,
          language: response.language,
          sources: response.sources,
          backendMessageId: response.messageId,
        });
        onConversationChange?.();
      } catch (e) {
        if (e instanceof ApiError && e.status === 403) {
          setAccessDenied(true);
          updateMessage(loadingId, {
            isLoading: false,
            content: 'Access restricted.',
            status: 'ACCESS_DENIED',
          });
        } else {
          updateMessage(loadingId, {
            isLoading: false,
            content: 'Something went wrong. Please try again.',
            status: 'ERROR',
          });
        }
      } finally {
        setSending(false);
      }
    },
    [
      token,
      teamsContext,
      conversationId,
      addMessage,
      updateMessage,
      setConversationId,
      setSending,
      setAccessDenied,
      setGlobalError,
      onConversationChange,
    ]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className={`eng-chat-page${hasMessages ? '' : ' eng-chat-page--centered'}`}>
      {!hasMessages && (
        <div className="eng-welcome">
          <h1 className="eng-welcome__title">How can we help you today?</h1>
          <p className="eng-welcome__subtitle">
            Ask HR questions in Albanian, Italian, or Serbian ÔÇö answers are grounded in your
            authorized HR documents.
          </p>
        </div>
      )}
      {hasMessages && <ConversationThread messages={messages} token={token} />}
      <ChatComposer disabled={isSending} onSubmit={handleSubmit} />
    </div>
  );
}
