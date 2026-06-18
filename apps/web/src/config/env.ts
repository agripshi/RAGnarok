export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  enableTeamsAuth: import.meta.env.VITE_ENABLE_TEAMS_AUTH === 'true',
  enableMockTeamsShell: import.meta.env.VITE_ENABLE_MOCK_TEAMS_SHELL === 'true',
  appDisplayName: import.meta.env.VITE_APP_DISPLAY_NAME ?? 'RAGnarok HR Assistant',
  devAuthToken: import.meta.env.VITE_DEV_AUTH_TOKEN ?? 'dev-token',
};
