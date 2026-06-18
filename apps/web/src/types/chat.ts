import type { AnswerStatus, SourceCardDto, SupportedLanguage } from './api';

export interface ChatMessageVm {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: AnswerStatus;
  language?: SupportedLanguage;
  sources?: SourceCardDto[];
  createdAt: string;
  isLoading?: boolean;
  backendMessageId?: string;
}
