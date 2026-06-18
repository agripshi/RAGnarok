import { useCallback, useEffect, useState } from 'react';
import { getTeamsContext, getTeamsSsoToken, initializeTeams } from './teamsAuth';
import type { TeamsContextPayload } from '../types/api';

interface UseTeamsAuthResult {
  isInitializing: boolean;
  isRunningInTeams: boolean;
  token: string | null;
  teamsContext: TeamsContextPayload;
  error: string | null;
  refreshToken: () => Promise<string>;
}

export function useTeamsAuth(): UseTeamsAuthResult {
  const [isInitializing, setIsInitializing] = useState(true);
  const [isRunningInTeams, setIsRunningInTeams] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [teamsContext, setTeamsContext] = useState<TeamsContextPayload>({});
  const [error, setError] = useState<string | null>(null);

  const refreshToken = useCallback(async () => {
    const t = await getTeamsSsoToken();
    setToken(t);
    return t;
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const inTeams = await initializeTeams();
        if (cancelled) return;
        setIsRunningInTeams(inTeams);
        const ctx = await getTeamsContext();
        if (cancelled) return;
        setTeamsContext(ctx);
        const t = await getTeamsSsoToken();
        if (cancelled) return;
        setToken(t);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Authentication failed');
      } finally {
        if (!cancelled) setIsInitializing(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { isInitializing, isRunningInTeams, token, teamsContext, error, refreshToken };
}
