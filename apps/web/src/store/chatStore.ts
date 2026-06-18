import { create } from 'zustand';
import type { ConversationSummaryDto } from '../types/api';
import type { ChatMessageVm } from '../types/chat';

interface ChatState {
  conversationId: string | null;
  messages: ChatMessageVm[];
  conversations: ConversationSummaryDto[];
  isSending: boolean;
  globalError: string | null;
  accessDenied: boolean;
  setConversationId: (id: string | null) => void;
  setConversations: (conversations: ConversationSummaryDto[]) => void;
  setMessages: (messages: ChatMessageVm[]) => void;
  addMessage: (message: ChatMessageVm) => void;
  updateMessage: (id: string, patch: Partial<ChatMessageVm>) => void;
  clearConversation: () => void;
  setSending: (value: boolean) => void;
  setGlobalError: (value: string | null) => void;
  setAccessDenied: (value: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  conversationId: null,
  messages: [],
  conversations: [],
  isSending: false,
  globalError: null,
  accessDenied: false,
  setConversationId: (id) => set({ conversationId: id }),
  setConversations: (conversations) => set({ conversations }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  updateMessage: (id, patch) =>
    set((s) => ({
      messages: s.messages.map((m) => (m.id === id ? { ...m, ...patch } : m)),
    })),
  clearConversation: () => set({ conversationId: null, messages: [] }),
  setSending: (value) => set({ isSending: value }),
  setGlobalError: (value) => set({ globalError: value }),
  setAccessDenied: (value) => set({ accessDenied: value }),
}));
