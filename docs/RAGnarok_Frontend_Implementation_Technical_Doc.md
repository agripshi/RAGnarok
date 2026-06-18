# RAGnarok HR Assistant - Frontend Implementation Technical Doc

**Audience:** Cursor / frontend developer  
**Scope:** Frontend only  
**App type:** Microsoft Teams app tab with Copilot-like HR chat UI  
**Frontend stack:** React + TypeScript + Vite + Fluent UI + Microsoft Teams JavaScript SDK  
**Backend dependency:** FastAPI backend exposed through `VITE_API_BASE_URL`  
**Version:** 1.0

---

## 1. Goal of This Document

Build the frontend for the RAGnarok HR Assistant. The UI must run inside Microsoft Teams as an app tab and must look and behave like a Copilot-style chat assistant.

The frontend must not implement business rules directly. It must:

1. Initialize inside Teams.
2. Acquire the Teams SSO token.
3. Send all chat requests to the Backend API.
4. Display answers, source cards, refusals, access errors, and feedback controls.
5. Never call the AI backend directly.
6. Never call the relational DB directly.
7. Never call the vector DB directly.
8. Never make authorization decisions locally.

The frontend is a client surface only. Security and HR answer policy are enforced by the Backend and AI layers.

---

## 2. Component Boundaries

```text
Microsoft Teams Client
        |
        v
RAGnarok React Frontend
        |
        | HTTPS REST API
        v
Backend API - FastAPI
        |
        +--> PostgreSQL
        +--> Microsoft Graph / access check
        +--> AI Backend - LangChain / LangGraph
```

### Frontend may call

- `GET /api/health`
- `GET /api/me`
- `POST /api/chat`
- `GET /api/conversations`
- `GET /api/conversations/{conversationId}`
- `POST /api/feedback`

### Frontend must not call

- Microsoft Graph directly for HR access decisions.
- LangChain / LangGraph AI service directly.
- Qdrant / Chroma vector DB.
- PostgreSQL.
- Cloud LLM APIs.

---

## 3. Required User Experience

The UI must follow the Copilot-like layout shown in the screenshot:

- Large centered welcome message.
- Rounded, wide chat composer centered below the title.
- Quick action chips below the composer.
- Minimal white/gray workspace.
- Top command area with model/mode selector placeholder and new-chat button.
- Conversation-first layout after the first message.
- Source cards under assistant responses.
- Feedback buttons under assistant responses.

Important implementation rule:

- When running inside Teams, do not recreate the real Teams left navigation rail. Teams already provides it.
- For local browser development, create a `MockTeamsShell` wrapper that visually resembles the screenshot. Hide this wrapper when `isRunningInTeams === true`.

---

## 4. Tech Stack

| Area | Technology |
|---|---|
| Framework | React 18+ |
| Language | TypeScript |
| Build tool | Vite |
| Teams SDK | `@microsoft/teams-js` |
| UI library | `@fluentui/react-components` |
| Icons | `@fluentui/react-icons` |
| State | React hooks + small Zustand store, or React context if preferred |
| HTTP | Native `fetch` wrapper |
| Styling | CSS modules or plain CSS with design tokens |
| Testing | Vitest + React Testing Library optional |

Use Fluent UI because it naturally matches Microsoft Teams visual patterns.

---

## 5. Project Setup Commands

Create the frontend under `apps/web`.

```bash
npm create vite@latest apps/web -- --template react-ts
cd apps/web
npm install @microsoft/teams-js @fluentui/react-components @fluentui/react-icons zustand uuid
npm install -D prettier eslint @types/node vitest @testing-library/react @testing-library/jest-dom jsdom
```

Recommended scripts in `apps/web/package.json`:

```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 5173",
    "build": "tsc -b && vite build",
    "preview": "vite preview --host 0.0.0.0 --port 4173",
    "test": "vitest"
  }
}
```

---

## 6. Environment Variables

Create `apps/web/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_TEAMS_AUTH=true
VITE_ENABLE_MOCK_TEAMS_SHELL=true
VITE_APP_DISPLAY_NAME=RAGnarok HR Assistant
VITE_DEV_AUTH_TOKEN=dev-token
```

Create `apps/web/.env.local` for local development.

Rules:

- `VITE_API_BASE_URL` points to the Backend API, not AI backend.
- `VITE_DEV_AUTH_TOKEN` is only for local non-Teams testing.
- Do not store cloud LLM API keys in frontend env files.
- Do not store Microsoft client secrets in frontend env files.

---

## 7. Recommended Frontend File Structure

```text
apps/web/
  index.html
  package.json
  vite.config.ts
  tsconfig.json
  .env.example
  src/
    main.tsx
    App.tsx
    config/
      env.ts
    api/
      apiClient.ts
      chatApi.ts
      feedbackApi.ts
      conversationApi.ts
    auth/
      teamsAuth.ts
      useTeamsAuth.ts
    store/
      chatStore.ts
    types/
      api.ts
      chat.ts
      teams.ts
    components/
      layout/
        AppShell.tsx
        MockTeamsShell.tsx
        HeaderBar.tsx
      welcome/
        WelcomePanel.tsx
        QuickActionChips.tsx
      chat/
        ChatPage.tsx
        ConversationThread.tsx
        ChatComposer.tsx
        UserMessage.tsx
        AssistantMessage.tsx
        SourceCardList.tsx
        SourceCard.tsx
        FeedbackButtons.tsx
        StatusBadge.tsx
      states/
        LoadingState.tsx
        AccessDeniedView.tsx
        ErrorState.tsx
        EmptyState.tsx
    styles/
      globals.css
      tokens.css
      layout.css
```

---

## 8. TypeScript DTOs

Create `src/types/api.ts`.

```ts
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

export interface ConversationSummaryDto {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface MessageDto {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  status?: AnswerStatus;
  language?: SupportedLanguage;
  sources?: SourceCardDto[];
  createdAt: string;
}

export interface FeedbackRequest {
  messageId: string;
  rating: 'helpful' | 'not_helpful';
  comment?: string;
}
```

Create `src/types/chat.ts` for frontend UI state.

```ts
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
}
```

---

## 9. Teams Authentication Implementation

## 9.1 Teams SDK Initialization

Create `src/auth/teamsAuth.ts`.

Responsibilities:

1. Initialize Teams SDK.
2. Detect whether app runs inside Teams.
3. Get Teams context.
4. Get SSO token.
5. Provide fallback token for local dev only.

Implementation logic:

```ts
import * as teams from '@microsoft/teams-js';

export async function initializeTeams(): Promise<boolean> {
  try {
    await teams.app.initialize();
    return true;
  } catch {
    return false;
  }
}

export async function getTeamsContext() {
  try {
    return await teams.app.getContext();
  } catch {
    return null;
  }
}

export async function getTeamsSsoToken(): Promise<string> {
  try {
    return await teams.authentication.getAuthToken();
  } catch (error) {
    if (import.meta.env.DEV && import.meta.env.VITE_DEV_AUTH_TOKEN) {
      return import.meta.env.VITE_DEV_AUTH_TOKEN;
    }
    throw error;
  }
}
```

Do not decode the token in the frontend for authorization. The backend validates it.

## 9.2 Auth Hook

Create `src/auth/useTeamsAuth.ts`.

State returned by hook:

```ts
interface UseTeamsAuthResult {
  isInitializing: boolean;
  isRunningInTeams: boolean;
  token: string | null;
  teamsContext: TeamsContextPayload;
  error: string | null;
  refreshToken: () => Promise<string>;
}
```

Flow:

1. On app mount, call `initializeTeams()`.
2. Call `getTeamsContext()`.
3. Call `getTeamsSsoToken()`.
4. Store token in memory only.
5. Do not store token in localStorage.

---

## 10. API Client Implementation

Create `src/api/apiClient.ts`.

```ts
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly payload?: unknown
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit,
  token: string
): Promise<T> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError(`API request failed: ${response.status}`, response.status, payload);
  }

  return response.json() as Promise<T>;
}
```

Create `src/api/chatApi.ts`.

```ts
import { apiFetch } from './apiClient';
import type { ChatRequest, ChatResponse } from '../types/api';

export function sendChatMessage(token: string, request: ChatRequest) {
  return apiFetch<ChatResponse>(
    '/api/chat',
    {
      method: 'POST',
      body: JSON.stringify(request)
    },
    token
  );
}
```

Create `src/api/feedbackApi.ts`.

```ts
import { apiFetch } from './apiClient';
import type { FeedbackRequest } from '../types/api';

export function submitFeedback(token: string, request: FeedbackRequest) {
  return apiFetch<{ ok: boolean }>(
    '/api/feedback',
    {
      method: 'POST',
      body: JSON.stringify(request)
    },
    token
  );
}
```

---

## 11. Chat Store

Use Zustand for simplicity. Create `src/store/chatStore.ts`.

State:

```ts
interface ChatState {
  conversationId: string | null;
  messages: ChatMessageVm[];
  isSending: boolean;
  globalError: string | null;
  accessDenied: boolean;

  setConversationId: (id: string | null) => void;
  addMessage: (message: ChatMessageVm) => void;
  updateMessage: (id: string, patch: Partial<ChatMessageVm>) => void;
  clearConversation: () => void;
  setSending: (value: boolean) => void;
  setGlobalError: (value: string | null) => void;
  setAccessDenied: (value: boolean) => void;
}
```

Rules:

- Store only UI state.
- Do not store auth token in Zustand unless necessary; prefer hook memory state.
- Keep conversation ID in memory. Optional localStorage can be added after MVP.

---

## 12. Main App Flow

Implement `App.tsx` as the root orchestrator.

Flow:

1. Load Teams auth hook.
2. If auth is initializing, show `LoadingState`.
3. If auth failed, show `ErrorState`.
4. If `accessDenied` is true, show `AccessDeniedView`.
5. Otherwise render `AppShell` and `ChatPage`.

Pseudo-structure:

```tsx
function App() {
  const auth = useTeamsAuth();

  if (auth.isInitializing) return <LoadingState label="Starting RAGnarok HR Assistant..." />;
  if (auth.error) return <ErrorState title="Authentication failed" message={auth.error} />;

  return (
    <AppShell isRunningInTeams={auth.isRunningInTeams}>
      <ChatPage token={auth.token!} teamsContext={auth.teamsContext} />
    </AppShell>
  );
}
```

---

## 13. Chat Page Flow

Create `src/components/chat/ChatPage.tsx`.

Props:

```ts
interface ChatPageProps {
  token: string;
  teamsContext: TeamsContextPayload;
}
```

Send message flow:

1. User submits text.
2. Validate non-empty.
3. Add user message to UI.
4. Add assistant loading message.
5. Call `POST /api/chat`.
6. If `403`, set access denied.
7. If response status is `ANSWERED`, replace loading with answer + source cards.
8. If `NEEDS_CLARIFICATION`, replace loading with clarification question.
9. If `NOT_FOUND`, replace loading with no-answer message.
10. If error, replace loading with controlled error.

Important:

- The frontend displays the backend's `answer` exactly. It does not rewrite or translate the answer.
- The frontend does not decide if the answer is good enough.
- The frontend does not hide sources if sources are returned.

---

## 14. Chat Composer

Create `ChatComposer.tsx`.

Requirements:

- Large rounded rectangular composer.
- Placeholder: `Message HR Assistant`.
- Plus icon on left, disabled for MVP or used only to show tooltip: `Documents are managed from the HR Teams channel`.
- Microphone icon on right as visual placeholder unless voice is implemented.
- Submit on Enter.
- New line on Shift+Enter.
- Disable while request is sending.

Props:

```ts
interface ChatComposerProps {
  disabled?: boolean;
  onSubmit: (message: string) => void;
}
```

---

## 15. Quick Action Chips

DO NOT IMPLEMENT NOTHIGN IS NOT PART OF MVP 

---

## 16. Source Card UI

Create `SourceCard.tsx`.

Display fields:

- Document title.
- Page, if available.
- Section, if available.
- Modified date, if available.
- Confidence, if available.
- `Open source` link if `sourceUrl` exists.

Rules:

- If `sourceUrl` is missing, show the card without link.
- If answer status is `NOT_FOUND`, there should usually be no source cards.
- Do not expose source cards for `ACCESS_DENIED`.

---

## 17. Status Badge UI

Create `StatusBadge.tsx`.

Map statuses:

| Status | Label |
|---|---|
| ANSWERED | Grounded answer |
| NEEDS_CLARIFICATION | Needs clarification |
| NOT_FOUND | Not found in HR documents |
| ACCESS_DENIED | Access denied |
| ERROR | Service error |

This is the UI implementation of the RAG Shield feature.

---

## 18. Access Denied View

Create `AccessDeniedView.tsx`.

Content:

```text
Access restricted
This HR assistant is available only to members of the private HR Teams channel.
If you believe you should have access, contact HR or your Teams administrator.
```

Rules:

- Hide chat composer.
- Hide conversation history if access is denied at app startup.
- Do not show document names.
- Do not show source links.

---

## 19. Styling Requirements

Create `src/styles/tokens.css`:

```css
:root {
  --rag-bg: #f7f7f7;
  --rag-surface: #ffffff;
  --rag-border: #e5e5e5;
  --rag-text: #242424;
  --rag-muted: #616161;
  --rag-radius-lg: 24px;
  --rag-radius-md: 14px;
  --rag-shadow-soft: 0 8px 28px rgba(0, 0, 0, 0.08);
  --rag-max-content: 940px;
}
```

Create layout behavior:

- Welcome panel vertically centered when no messages exist.
- Conversation thread starts near top when messages exist.
- Composer stays below thread; optional sticky bottom for better UX.
- Content width max around `940px`.
- Use whitespace heavily, similar to Copilot.

---

## 20. Error Mapping in Frontend

| Backend response | UI behavior |
|---|---|
| 401 | Show authentication error and ask user to reopen Teams app. |
| 403 | Show `AccessDeniedView`. |
| 404 conversation | Show error and reset conversation. |
| 500 | Show controlled service error under assistant bubble. |
| Network error | Show retry message. |
| AI status `NOT_FOUND` | Show no-answer assistant card. |
| AI status `NEEDS_CLARIFICATION` | Show clarification question and keep composer active. |

---

## 21. Accessibility

Minimum requirements:

- Buttons must have accessible labels.
- Composer must be keyboard usable.
- Source links must be real anchor elements.
- Loading state must have readable text.
- Message role should be clear visually and semantically.
- Do not rely on color only for answer status.

---

## 22. Implementation Steps for Cursor

### Step 1 - Create Vite React app

Generate the app under `apps/web` and install required dependencies.

### Step 2 - Add environment config

Create `src/config/env.ts`:

```ts
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  enableTeamsAuth: import.meta.env.VITE_ENABLE_TEAMS_AUTH === 'true',
  enableMockTeamsShell: import.meta.env.VITE_ENABLE_MOCK_TEAMS_SHELL === 'true',
  appDisplayName: import.meta.env.VITE_APP_DISPLAY_NAME ?? 'RAGnarok HR Assistant'
};
```

### Step 3 - Implement Teams auth

Create `teamsAuth.ts` and `useTeamsAuth.ts` exactly as described.

### Step 4 - Implement API DTOs and API client

Create all DTOs and `apiFetch` wrapper. All requests must include bearer token.

### Step 5 - Implement app shell

Create `AppShell`, `HeaderBar`, and optional `MockTeamsShell`.

### Step 6 - Implement welcome screen

Create `WelcomePanel`, `QuickActionChips`, and initial centered composer.

### Step 7 - Implement chat flow

Create `ChatPage`, `ConversationThread`, `ChatComposer`, message components, and Zustand store.

### Step 8 - Implement source cards and status badges

Display returned `sources` and `status` from backend.

### Step 9 - Implement feedback

`FeedbackButtons` calls `POST /api/feedback` with `messageId` and rating.

### Step 10 - Implement access denied and error states

Map HTTP status codes and AI statuses to proper UI states.

### Step 11 - Test locally

Run:

```bash
npm run dev
```

Use backend local URL:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_AUTH_TOKEN=dev-token
```

### Step 12 - Package for Teams

Keep Teams manifest under:

```text
apps/web/appPackage/manifest.json
```

Set `validDomains` to the frontend host domain and backend host domain if required.

---

## 23. Frontend Acceptance Criteria

The frontend is complete when:

1. It runs with `npm run dev`.
2. It initializes inside Teams without crashing.
3. It can work in local browser mode with mock auth.
4. It displays the Copilot-like welcome layout.
5. It sends chat messages to `POST /api/chat`.
6. It includes the bearer token in API calls.
7. It sends Teams context to backend.
8. It displays `ANSWERED` responses with source cards.
9. It displays `NOT_FOUND` responses safely.
10. It displays `NEEDS_CLARIFICATION` responses as a follow-up question.
11. It hides composer on `ACCESS_DENIED`.
12. It supports quick action chips.
13. It supports feedback buttons.
14. It does not call AI, DB, vector DB, Graph, or LLM APIs directly.

---

## 24. Cursor Final Instruction

When using this document in Cursor, generate only the frontend code under `apps/web`. Do not implement backend, database, AI, vector DB, or cloud model logic in this frontend project. All business logic must be consumed through the Backend API contracts defined above.
