export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  enableTeamsAuth: import.meta.env.VITE_ENABLE_TEAMS_AUTH === 'true',
  enableMockTeamsShell:
    import.meta.env.VITE_ENABLE_MOCK_TEAMS_SHELL !== 'false' && import.meta.env.DEV,
  appDisplayName: import.meta.env.VITE_APP_DISPLAY_NAME ?? 'HR Hub',
  devAuthToken: import.meta.env.VITE_DEV_AUTH_TOKEN ?? 'dev-token',
};
