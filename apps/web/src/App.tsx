import { FluentProvider, webLightTheme, Text, Spinner } from '@fluentui/react-components';
import { useEffect, useState } from 'react';
import { env } from './config/env';
import './styles/globals.css';

function App() {
  const [backendStatus, setBackendStatus] = useState<'loading' | 'ok' | 'error'>('loading');

  useEffect(() => {
    fetch(`${env.apiBaseUrl}/api/health`)
      .then((r) => (r.ok ? setBackendStatus('ok') : setBackendStatus('error')))
      .catch(() => setBackendStatus('error'));
  }, []);

  return (
    <FluentProvider theme={webLightTheme}>
      <main
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
          maxWidth: 'var(--rag-max-content)',
          margin: '0 auto',
        }}
      >
        <Text as="h1" size={800} weight="semibold" align="center">
          Welcome, how can I help?
        </Text>
        <Text align="center" style={{ color: 'var(--rag-muted)', marginTop: '0.5rem' }}>
          {env.appDisplayName} — Sprint 0 foundation
        </Text>
        <div
          style={{
            marginTop: '2rem',
            padding: '1rem 1.5rem',
            background: 'var(--rag-surface)',
            borderRadius: 'var(--rag-radius-lg)',
            boxShadow: 'var(--rag-shadow-soft)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          {backendStatus === 'loading' && <Spinner size="tiny" />}
          <Text>
            Backend API:{' '}
            {backendStatus === 'loading' && 'checking…'}
            {backendStatus === 'ok' && 'connected'}
            {backendStatus === 'error' && 'unreachable — start apps/api on :8000'}
          </Text>
        </div>
      </main>
    </FluentProvider>
  );
}

export default App;
