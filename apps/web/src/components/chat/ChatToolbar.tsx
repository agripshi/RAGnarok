import { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Dropdown, Option, Text } from '@fluentui/react-components';
import { Add24Regular, History24Regular } from '@fluentui/react-icons';
import { fetchConversation, fetchConversations } from '../../api/conversationApi';
import { EngLogo } from '../brand/EngLogo';
import { useChatStore } from '../../store/chatStore';
import type { MessageDto } from '../../types/api';
import type { ChatMessageVm } from '../../types/chat';

interface ChatToolbarProps {
  token: string;
  refreshKey?: number;
}

function toChatMessageVm(message: MessageDto): ChatMessageVm {
  return {
    id: message.id,
    role: message.role === 'user' ? 'user' : 'assistant',
    content: message.content,
    status: message.status,
    language: message.language,
    sources: message.sources,
    createdAt: message.createdAt,
    backendMessageId: message.role === 'assistant' ? message.id : undefined,
  };
}

export function ChatToolbar({ token, refreshKey = 0 }: ChatToolbarProps) {
  const {
    conversationId,
    conversations,
    clearConversation,
    setConversationId,
    setConversations,
    setMessages,
    isSending,
  } = useChatStore();

  const [historyError, setHistoryError] = useState<string | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const selectedConversation = useMemo(
    () => conversations.find((c) => c.id === conversationId),
    [conversations, conversationId]
  );

  const loadConversations = useCallback(async () => {
    setLoadingHistory(true);
    setHistoryError(null);
    try {
      const list = await fetchConversations(token);
      setConversations(list);
    } catch (e) {
      setConversations([]);
      setHistoryError(e instanceof Error ? e.message : 'Could not load chat history');
    } finally {
      setLoadingHistory(false);
    }
  }, [token, setConversations]);

  useEffect(() => {
    void loadConversations();
  }, [loadConversations, refreshKey]);

  const handleNewChat = () => {
    clearConversation();
  };

  const handleSelectConversation = async (id: string) => {
    if (!id) return;

    setHistoryError(null);
    try {
      const detail = await fetchConversation(token, id);
      setConversationId(detail.id);
      setMessages(detail.messages.map(toChatMessageVm));
    } catch (e) {
      setHistoryError(e instanceof Error ? e.message : 'Could not open conversation');
    }
  };

  const historyPlaceholder = loadingHistory
    ? 'Loading history…'
    : conversations.length === 0
      ? 'No past chats yet'
      : 'Chat history';

  return (
    <div className="eng-toolbar">
      <EngLogo />
      <div className="eng-toolbar__actions">
        <Button
          appearance="primary"
          icon={<Add24Regular />}
          onClick={handleNewChat}
          disabled={isSending}
        >
          New chat
        </Button>
        <Dropdown
          aria-label="Chat history"
          placeholder={historyPlaceholder}
          value={selectedConversation?.title ?? ''}
          selectedOptions={conversationId ? [conversationId] : []}
          onOptionSelect={(_, data) => {
            if (data.optionValue) {
              void handleSelectConversation(String(data.optionValue));
            }
          }}
          disabled={isSending || loadingHistory || (conversations.length === 0 && !historyError)}
          style={{ minWidth: 240 }}
          expandIcon={<History24Regular />}
        >
          {conversations.map((conversation) => (
            <Option key={conversation.id} value={conversation.id} text={conversation.title}>
              {conversation.title}
            </Option>
          ))}
        </Dropdown>
        {historyError && (
          <Text size={200} style={{ color: '#f87171', maxWidth: 200 }}>
            {historyError}
          </Text>
        )}
      </div>
    </div>
  );
}
