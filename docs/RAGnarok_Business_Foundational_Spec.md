# RAGnarok HR Assistant - Business Foundational Specification

**Team:** RAGnarok / Ragnarok  
**Event:** HR Chatbot Hackathon 2026  
**Product:** Multilingual HR Assistant for Microsoft Teams  
**Delivery target:** Working demo and GitHub repository under 8 hours  
**Document type:** Business foundation, functional scope, and business flows  
**Version:** 1.0

---

## 1. Executive Summary

RAGnarok HR Assistant is a Microsoft Teams application that allows employees to ask HR questions and receive clear, sourced answers based only on HR documents stored in a private Teams channel / SharePoint document library.

The assistant behaves as an HR support agent, but it does not invent policy, does not answer from general model knowledge, and does not expose HR content to users who do not have access to the private channel where the source documents are stored.

The application must support multilingual communication. For the RAGnarok MVP, the locked languages are:

- Albanian / SQ
- Italian / IT
- Serbian / SR, preserving the user's script when possible

Optional event-alignment fallback:

- English / EN can be added as an extra language if required by the judges or if source documents include English policy material.

The Teams UI must follow the same interaction pattern as Microsoft Copilot inside Teams: centered welcome message, rounded chat composer, quick action chips, left navigation rail, top bar, and conversation-first layout. The app should not require users to learn a new interaction model.

---

## 2. Business Problem

HR knowledge is already documented, but it is locked inside PDFs and files across Teams / SharePoint folders. Employees lose time searching for the right file, the correct language, and the latest policy version. HR teams are interrupted by repeated questions that already have official answers.

Current pain points:

1. Employees do not know which HR document contains the answer.
2. HR documents may exist in different languages and for different offices.
3. Manual search across PDFs is slow.
4. Users may rely on outdated versions of policy documents.
5. Generic AI assistants may answer from model knowledge instead of internal HR policy.
6. Private HR documents must not be exposed outside the authorized Teams channel audience.

RAGnarok solves this by placing a controlled, document-grounded HR assistant directly inside Teams.

---

## 3. Product Vision

**Vision statement:**

> Ask HR anything in Teams, in your language, and receive a verified answer grounded only in the HR documents you are allowed to access.

The product is not a generic chatbot. It is a controlled HR knowledge interface with three mandatory moves:

1. **Ask:** the employee asks a question in Albanian, Italian, or Serbian.
2. **Retrieve:** the system retrieves only authorized, latest HR document chunks from the private Teams channel source.
3. **Answer:** the assistant answers in the same language, with document citations and a refusal when the documents do not support an answer.

---

## 4. Business Objectives

### 4.1 Primary Objectives

- Reduce repeated HR questions by making HR policy searchable through natural language.
- Ensure employees receive answers based on official internal documents only.
- Preserve document-level and channel-level access control.
- Support multilingual employees without forcing them to search in another language.
- Provide a Teams-native experience that feels familiar and fast.
- Deliver a credible production-oriented MVP within the hackathon time limit.

### 4.2 Secondary Objectives

- Show a reusable architecture that can later support other internal knowledge domains.
- Expose an API layer so the assistant can become middleware for other apps.
- Provide auditability: every answer should be traceable to source documents.
- Give HR visibility into unanswered questions and document gaps.

---

## 5. Scope

### 5.1 In Scope for Hackathon MVP

- Microsoft Teams app with Copilot-like chat UI.
- Authentication through Teams / Microsoft Entra ID.
- Authorization check against the private Teams channel or private channel-backed SharePoint site.
- Document ingestion from the HR documents stored in the Teams channel / SharePoint location.
- RAG-based Q&A using LangChain or LangGraph.
- Vector search over HR document chunks.
- Answer generation using cloud LLM API keys.
- Same-language response behavior for Albanian, Italian, and Serbian.
- Source citations in every successful answer.
- Refusal when the answer is not present in the documents.
- Basic conversation history.
- Feedback button: helpful / not helpful.
- Admin or developer endpoint to trigger re-indexing.
- GitHub repository with specifications, setup guide, and demo instructions.

### 5.2 Out of Scope for Hackathon MVP

- Full HR ticketing workflow.
- Employee-specific salary or payroll calculations.
- Personal HR case management.
- Editing HR documents from the chatbot.
- Long-term analytics dashboard.
- Full enterprise deployment hardening.
- Mobile-specific Teams optimization beyond responsive layout.
- Automatic translation of entire documents.
- Replacing HR personnel in complex or sensitive cases.

---

## 6. Users and Actors

| Actor | Description | Main goals |
|---|---|---|
| Employee / End User | A user who belongs to the authorized private Teams channel. | Ask HR questions and receive policy-grounded answers. |
| Unauthorized User | A Teams user who can open the app but is not allowed to access the HR document channel. | Must be denied safely. |
| HR Stakeholder | HR representative validating answer quality and policy correctness. | Confirm that answers match official HR documents. |
| Demo Judge | Evaluates usability, architecture, specification quality, LLM usage, and production readiness. | See a live, grounded, multilingual demo. |
| Technical Admin / Developer | Maintains ingestion, API keys, Teams app package, and deployment. | Configure source channel, run sync, monitor failures. |

---

## 7. Business Rules

### BR-001: Document-only answers
The assistant must answer only from HR documents indexed from the approved private Teams channel / SharePoint location. It must not use general model knowledge for HR policy claims.

### BR-002: Authorized users only
The assistant must answer only if the requesting user has access to the private Teams channel that contains the HR documents. If access cannot be verified, the system must deny access.

### BR-003: Same-language response
The assistant must detect the user's question language and answer in the same language. For Serbian, the assistant should preserve Latin or Cyrillic script based on the user's input when possible.

### BR-004: Source citation required
Every successful HR answer must include the document title and, where available, page / section / chunk reference. If the source cannot be shown, the answer should be treated as incomplete.

### BR-005: Latest source preferred
When multiple versions of a document exist, the assistant must prefer the latest version based on document metadata, modified date, version ID, or configured source priority.

### BR-006: No-answer fallback
If retrieved context does not contain enough evidence, the assistant must say that the answer was not found in the available HR documents and recommend contacting HR.

### BR-007: Sensitive HR boundary
The assistant must not infer personal employee information, employee status, salary, disciplinary matters, or private HR cases unless those facts are explicitly present in authorized source documents and relevant to the user.

### BR-008: Office-specific policy handling
If policy differs by location, the assistant must clarify whether the user refers to Albania, Serbia, or another office. Language alone must not be treated as office identity.

### BR-009: Fail closed
If authentication, authorization, document retrieval, vector DB, or source validation fails, the assistant must not produce a policy answer.

### BR-010: No hidden source leakage
Unauthorized users must not receive document names, document snippets, file paths, or SharePoint links from the protected channel.

---

## 8. User Experience Foundation

### 8.1 Teams Placement

The product is delivered as a Microsoft Teams app, preferably as a personal tab or channel tab for the hackathon. The UI is embedded inside Teams and uses the signed-in Teams context.

### 8.2 Copilot-like Layout Requirements

The UI must mimic the interaction pattern shown in the provided Copilot screenshot:

- Left vertical Teams rail remains visible.
- Top bar remains consistent with Teams shell.
- Main app canvas is clean and minimal.
- Centered welcome title: `Welcome, how can I help?`
- Large rounded chat composer centered on the page.
- Placeholder: `Message HR Assistant` or `Message Copilot-style HR Assistant`.
- Microphone icon can be shown as non-functional UI placeholder for MVP.
- Plus icon can be hidden or disabled for end users because document upload must remain controlled through the HR Teams channel.
- Quick action chips below the composer:
  - Learn
  - Find
  - Summarize
  - Suggest
- New conversation button at top-right or inside the app header.
- Conversation view uses message bubbles or Copilot-style stacked responses.
- Source cards appear under answers.

### 8.3 UX Principle

Users should not need to understand RAG, PDFs, SharePoint, embeddings, or Teams permissions. They should ask naturally and receive a safe HR answer.

---

## 9. Key Differentiators for the Demo

### 9.1 RAG Shield

A visible safety layer that explains why the assistant answered or refused.

Possible statuses:

- `Grounded answer` - enough document evidence was found.
- `Needs clarification` - the question is ambiguous by office, policy type, or employee group.
- `Not found in HR documents` - retrieval confidence is insufficient.
- `Access denied` - the user is not authorized for the HR source channel.

This turns safety into a visible product feature instead of a hidden technical constraint.

### 9.2 Policy Passport

Every answer includes a compact source card:

- Source document title
- Language of source
- Office / country if detected
- Last modified date if available
- Relevant section or page
- Confidence level
- Open source link if the user has access

This helps judges see that the assistant is not hallucinating and that the source is close at hand.

---

## 10. Core Business Flows

## BF-001 - First-Time User Opens Teams App

**Actor:** Employee  
**Precondition:** User is signed into Microsoft Teams.  
**Trigger:** User opens the RAGnarok HR Assistant app.

**Main flow:**

1. Teams loads the RAGnarok app tab.
2. Frontend initializes Teams SDK.
3. Frontend requests Teams SSO token.
4. Backend validates the token.
5. Backend checks whether the user has access to the configured private HR channel.
6. If authorized, the app displays the welcome screen and chat composer.
7. User can start asking HR questions.

**Success output:** Copilot-like chat UI is visible and ready.

**Failure flow:**

- If token is missing or invalid: show login/authentication error.
- If channel access check fails: show generic access denied message.
- If backend is unavailable: show service unavailable message.

---

## BF-002 - Authorized User Asks HR Question

**Actor:** Employee  
**Precondition:** User is authenticated and authorized.  
**Trigger:** User sends a question.

**Main flow:**

1. User enters a question in Albanian, Italian, or Serbian.
2. Frontend sends question, conversation ID, and Teams context to backend.
3. Backend validates user token and checks channel access.
4. Backend stores the user message.
5. AI service detects the input language.
6. AI service creates a retrieval query.
7. Vector DB returns relevant chunks filtered by authorized source channel and latest document versions.
8. AI service evaluates whether context is sufficient.
9. LLM generates a same-language answer using only retrieved context.
10. AI service validates that each answer claim is grounded in retrieved chunks.
11. Backend stores assistant response, source references, language, and status.
12. Frontend displays the answer and source cards.

**Success output:** User receives a same-language HR answer with citations.

**Failure flow:** If no evidence is found, execute BF-004.

---

## BF-003 - User Asks an Ambiguous Question

**Actor:** Employee  
**Example questions:**

- Albanian: `Sa ditë pushimi kam?`
- Italian: `Come funziona il congedo?`
- Serbian: `Kako funkcioniše bolovanje?`

**Main flow:**

1. User asks a broad or ambiguous HR question.
2. Retrieval finds multiple possible policy areas or office-specific rules.
3. AI service detects ambiguity.
4. Assistant asks a short clarification question in the same language.
5. User clarifies office, policy type, contract type, or timeframe.
6. System continues with BF-002.

**Business rule:** The assistant must not guess office or contract category when the documents show different rules.

---

## BF-004 - No Answer Found in HR Documents

**Actor:** Employee  
**Trigger:** Retrieval returns no strong evidence or answer validator fails.

**Main flow:**

1. User asks a question.
2. AI retrieval does not find sufficient source evidence.
3. Assistant refuses to answer from general knowledge.
4. Assistant explains that the answer was not found in the available HR documents.
5. Assistant suggests contacting HR or checking whether the document exists in the source channel.
6. System logs the question as a document gap.

**Example response pattern:**

> I could not find this information in the HR documents I am allowed to use. Please contact HR or ask an HR owner to add the relevant policy document to the HR Teams channel.

The same pattern must be translated to the user's input language.

---

## BF-005 - Unauthorized User Attempts to Ask

**Actor:** Unauthorized User  
**Trigger:** User opens the app or sends a question.

**Main flow:**

1. User opens the app or submits a question.
2. Backend validates identity but cannot verify private channel access.
3. Backend denies the request.
4. Frontend displays an access message without exposing protected document metadata.

**Success output:** No HR content is disclosed.

**Example response pattern:**

> You do not have access to this HR assistant. Access is limited to members of the private HR Teams channel.

The message should be localized if the user's language is known.

---

## BF-006 - User Requests Summary of a Policy Document

**Actor:** Employee  
**Trigger:** User clicks `Summarize` or asks for a policy summary.

**Main flow:**

1. User requests a summary of a document or policy topic.
2. System checks authorization.
3. Retrieval finds the relevant document sections.
4. Assistant summarizes only retrieved content.
5. Assistant includes source cards.
6. If the requested document is not found, execute BF-004.

**Business rule:** Summary must not combine policies from different offices unless explicitly requested.

---

## BF-007 - User Clicks a Source Card

**Actor:** Employee  
**Trigger:** User clicks `Open source`.

**Main flow:**

1. User clicks the source card under an answer.
2. Backend or frontend opens the SharePoint / Teams file URL.
3. Microsoft 365 enforces file-level access.
4. User views the original document.

**Failure flow:** If Microsoft 365 denies access, show a simple access error and do not expose content in the app.

---

## BF-008 - HR Owner Adds or Updates Documents

**Actor:** HR Stakeholder / Technical Admin  
**Trigger:** HR adds or updates PDFs in the private Teams channel.

**Main flow:**

1. New or updated documents are placed in the configured Teams channel / SharePoint folder.
2. Admin triggers `Sync documents` or scheduled ingestion runs.
3. Ingestion service lists files from the authorized source.
4. System compares document IDs, modified timestamps, and content hash.
5. New or changed files are extracted, chunked, embedded, and stored.
6. Previous versions are marked inactive but kept for audit.
7. Vector DB is updated with the latest chunks.
8. Assistant uses latest active versions for new answers.

**Success output:** Updated HR content is available in chat.

---

## BF-009 - User Gives Feedback

**Actor:** Employee  
**Trigger:** User clicks helpful / not helpful.

**Main flow:**

1. User rates an answer.
2. System stores feedback, question, answer ID, source IDs, language, and status.
3. If negative, user can optionally provide a reason.
4. HR or developers can review unanswered or low-rated questions after the demo.

**MVP output:** Feedback is stored and visible in DB/logs.

---

## BF-010 - Demo Flow for Judges

**Actor:** Presenter / Judge  
**Trigger:** 10-minute live demo.

**Demo script:**

1. Open RAGnarok HR Assistant inside Microsoft Teams.
2. Show Copilot-like UI.
3. Ask a question in Albanian.
4. Show same-language answer with source card.
5. Ask a question in Italian.
6. Show same-language answer with source card.
7. Ask a question in Serbian.
8. Show same-language answer with source card.
9. Ask an unsupported question.
10. Show safe refusal and no hallucination.
11. Optionally show unauthorized flow or explain channel-based permission check.
12. Show architecture diagram and repository specifications.

---

## 11. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | User can open the app inside Microsoft Teams. | Must |
| FR-002 | User can ask free-text HR questions. | Must |
| FR-003 | App authenticates the Teams user. | Must |
| FR-004 | Backend verifies access to private HR source channel. | Must |
| FR-005 | System retrieves HR document chunks from vector DB. | Must |
| FR-006 | System filters retrieval by authorized source. | Must |
| FR-007 | Assistant answers only from retrieved document context. | Must |
| FR-008 | Assistant answers in the same language as the question. | Must |
| FR-009 | Assistant cites sources for every answer. | Must |
| FR-010 | Assistant refuses when answer is not found in documents. | Must |
| FR-011 | User can see source cards. | Should |
| FR-012 | Conversation history is stored. | Should |
| FR-013 | Admin/developer can trigger document sync. | Should |
| FR-014 | User can give feedback. | Should |
| FR-015 | API can be consumed as middleware by future apps. | Should |
| FR-016 | Quick action chips trigger preset prompts. | Could |
| FR-017 | Voice input icon appears in UI. | Could |

---

## 12. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Security | Fail closed on authentication, authorization, or retrieval errors. |
| Privacy | Do not expose protected document content to unauthorized users. |
| Performance | First token should appear quickly enough for live demo; target under 5 seconds for common questions. |
| Cost | Use small cloud models and compact chunks to reduce token cost. |
| Reliability | If LLM fails, return a controlled error, not partial or unsafe content. |
| Auditability | Store question, answer, sources, status, and user ID hash or user reference. |
| Maintainability | Keep FE, BE, AI, DB, and Vector DB layers separated. |
| Portability | Use environment variables for API keys, Teams IDs, model config, and DB URLs. |
| Usability | UI must match familiar Teams/Copilot interaction patterns. |

---

## 13. Answer Policy

The assistant must follow this answer decision table:

| Situation | Assistant behavior |
|---|---|
| User authorized + evidence found | Answer in same language with source card. |
| User authorized + ambiguous query | Ask a clarification question. |
| User authorized + no evidence | Refuse and say the answer was not found in HR documents. |
| User unauthorized | Deny access without exposing document details. |
| Model uncertain | Refuse or clarify; never guess. |
| User asks outside HR scope | Say the assistant is limited to HR documents. |
| User asks for legal/medical/personal advice | Refer to HR / official channels unless documents explicitly cover the process. |

---

## 14. Data to Capture

Minimum data for MVP:

- User ID from Teams / Entra ID
- Conversation ID
- Message ID
- Question text
- Detected language
- Answer text
- Source document IDs
- Source chunk IDs
- Confidence / status
- Timestamp
- Feedback rating

Avoid storing unnecessary personal content.

---

## 15. Acceptance Criteria

The MVP is accepted for demo if:

1. The app opens inside Microsoft Teams.
2. The UI follows the Copilot-like design pattern.
3. An authorized user can ask at least three HR questions.
4. The app answers in Albanian, Italian, and Serbian.
5. Answers include visible source cards.
6. The app refuses unsupported questions.
7. The app does not answer when access cannot be verified.
8. The repository includes specification documents.
9. The architecture has FE, BE, DB, AI, and Vector DB layers.
10. The demo can be completed live in under 10 minutes.

---

## 16. 8-Hour Business Delivery Plan

| Timebox | Business output |
|---|---|
| Hour 0-1 | Finalize scope, source channel, supported languages, demo questions. |
| Hour 1-2 | Create Teams app shell and Copilot-like UI skeleton. |
| Hour 2-3 | Ingest initial HR documents and prepare vector index. |
| Hour 3-4 | Implement document-grounded Q&A. |
| Hour 4-5 | Implement same-language answer and source cards. |
| Hour 5-6 | Add authorization guard and no-answer refusal. |
| Hour 6-7 | Polish UI, quick action chips, feedback, logs. |
| Hour 7-8 | Test demo script, commit specs, add reviewers, freeze repo. |

---

## 17. Final Business Positioning

RAGnarok is not trying to build the biggest chatbot. It is trying to build the safest and most useful HR assistant for Teams:

- Same place employees already work: Microsoft Teams.
- Same documents HR already trusts: private Teams / SharePoint HR files.
- Same language employees use: Albanian, Italian, or Serbian.
- Same access rules as the private HR channel.
- No hallucinated HR policy.
- No unauthorized document leakage.

This positioning directly supports the hackathon scoring criteria: usable solution, strong specification, effective LLM use, solid architecture, and agent setup.
