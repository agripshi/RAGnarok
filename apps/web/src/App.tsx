import { FluentProvider, webDarkTheme, Spinner, Text } from '@fluentui/react-components';
import { useEffect, useState } from 'react';
import { fetchMe } from './api/meApi';
import { useTeamsAuth } from './auth/useTeamsAuth';
import { ChatPage } from './components/chat/ChatPage';
import { ChatToolbar } from './components/chat/ChatToolbar';
import { env } from './config/env';
import './styles/globals.css';

function LoadingState({ label }: { label: string }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
      <Spinner />
      <Text>{label}</Text>
    </div>
  );
}

function ErrorState({ title, message }: { title: string; message: string }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
      <Text weight="semibold" size={500}>{title}</Text>
      <Text style={{ color: 'var(--rag-muted)' }}>{message}</Text>
    </div>
  );
}

function AccessDeniedView() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', textAlign: 'center', maxWidth: 480 }}>
      <Text weight="semibold" size={600}>Access restricted</Text>
      <Text style={{ marginTop: '1rem', color: 'var(--rag-muted)' }}>
        This HR assistant is available only to members of the private HR Teams channel.
        If you believe you should have access, contact HR or your Teams administrator.
      </Text>
    </div>
  );
}

function App() {
  const auth = useTeamsAuth();
  const [hasHrAccess, setHasHrAccess] = useState<boolean | null>(null);
  const [accessError, setAccessError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!auth.token) return;
    setAccessError(null);
    fetchMe(auth.token)
      .then((me) => setHasHrAccess(me.hasHrAccess))
      .catch((e) => {
        setHasHrAccess(false);
        setAccessError(e instanceof Error ? e.message : 'Could not reach backend API');
      });
  }, [auth.token]);

  if (auth.isInitializing || (auth.token && hasHrAccess === null && !accessError)) {
    return (
      <FluentProvider theme={webDarkTheme}>
        <LoadingState label={`Starting ${env.appDisplayName}…`} />
      </FluentProvider>
    );
  }

  if (auth.error || !auth.token) {
    return (
      <FluentProvider theme={webDarkTheme}>
        <ErrorState
          title="Authentication failed"
          message={auth.error ?? 'No token available'}
        />
      </FluentProvider>
    );
  }

  if (accessError) {
    return (
      <FluentProvider theme={webDarkTheme}>
        <ErrorState
          title="Cannot reach backend"
          message={`${accessError} — ensure the API is running at ${env.apiBaseUrl}`}
        />
      </FluentProvider>
    );
  }

  if (hasHrAccess === false) {
    return (
      <FluentProvider theme={webDarkTheme}>
        <AccessDeniedView />
      </FluentProvider>
    );
  }

  return (
    <FluentProvider theme={webDarkTheme}>
      <div className="eng-app">
        <header className="eng-app__header">
          <ChatToolbar token={auth.token!} refreshKey={refreshKey} />
        </header>
        <main className="eng-app__main">
          <ChatPage
            token={auth.token!}
            teamsContext={auth.teamsContext}
            onConversationChange={() => setRefreshKey((k) => k + 1)}
          />
        </main>
      </div>
    </FluentProvider>
  );
}

export default App;
