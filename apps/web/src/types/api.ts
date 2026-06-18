export type AnswerStatus =
  | 'ANSWERED'
  | 'NEEDS_CLARIFICATION'
  | 'NOT_FOUND'
  | 'ACCESS_DENIED'
  | 'ERROR';

export type SupportedLanguage = 'sq' | 'it' | 'sr' | 'en' | 'unknown';

export interface TeamsContextPayload {
  teamId?: string;
  channelId?: string;
  userId?: string;
  locale?: string;
  tenantId?: string;
}

export interface ChatRequest {
  conversationId: string | null;
  message: string;
  teamsContext: TeamsContextPayload;
}

export interface SourceCardDto {
  documentId?: string;
  title: string;
  page?: number | null;
  section?: string | null;
  sourceUrl?: string | null;
  modifiedAt?: string | null;
  confidence?: number | null;
}

export interface ChatResponse {
  conversationId: string;
  messageId: string;
  status: AnswerStatus;
  language: SupportedLanguage;
  answer: string;
  clarificationQuestion?: string | null;
  sources: SourceCardDto[];
}

export interface MeResponse {
  userId: string;
  email?: string | null;
  displayName?: string | null;
  hasHrAccess: boolean;
}

export interface FeedbackRequest {
  messageId: string;
  rating: 'helpful' | 'not_helpful';
  comment?: string;
}
