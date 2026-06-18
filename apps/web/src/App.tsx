import { FluentProvider, webLightTheme, Spinner, Text } from '@fluentui/react-components';
import { useTeamsAuth } from './auth/useTeamsAuth';
import { ChatPage } from './components/chat/ChatPage';
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

  if (auth.isInitializing) {
    return (
      <FluentProvider theme={webLightTheme}>
        <LoadingState label={`Starting ${env.appDisplayName}…`} />
      </FluentProvider>
    );
  }

  if (auth.error || !auth.token) {
    return (
      <FluentProvider theme={webLightTheme}>
        <ErrorState title="Authentication failed" message={auth.error ?? 'No token available'} />
      </FluentProvider>
    );
  }

  return (
    <FluentProvider theme={webLightTheme}>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--rag-border)', background: 'var(--rag-surface)' }}>
          <Text weight="semibold">{env.appDisplayName}</Text>
        </header>
        <ChatPage token={auth.token} teamsContext={auth.teamsContext} />
      </div>
    </FluentProvider>
  );
}

export default App;
