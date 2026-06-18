import * as teams from '@microsoft/teams-js';
import { env } from '../config/env';
import type { TeamsContextPayload } from '../types/api';

const SSO_TIMEOUT_MS = 8_000;

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label} timed out`)), ms);
    promise
      .then((value) => {
        clearTimeout(timer);
        resolve(value);
      })
      .catch((error) => {
        clearTimeout(timer);
        reject(error);
      });
  });
}

export async function initializeTeams(): Promise<boolean> {
  try {
    await withTimeout(teams.app.initialize(), SSO_TIMEOUT_MS, 'Teams initialize');
    return true;
  } catch {
    return false;
  }
}

export async function getTeamsContext(): Promise<TeamsContextPayload> {
  try {
    const ctx = await withTimeout(teams.app.getContext(), SSO_TIMEOUT_MS, 'Teams context');
    return {
      teamId: ctx.team?.groupId,
      channelId: ctx.channel?.id,
      userId: ctx.user?.id,
      locale: ctx.app?.locale,
      tenantId: ctx.user?.tenant?.id,
    };
  } catch {
    return {};
  }
}

function shouldUseDevToken(inTeams: boolean): boolean {
  if (!env.devAuthToken) return false;
  if (!import.meta.env.DEV) return false;
  if (!env.enableTeamsAuth || env.enableMockTeamsShell) return true;
  return !inTeams;
}

export async function getTeamsSsoToken(inTeams: boolean): Promise<string> {
  if (shouldUseDevToken(inTeams)) {
    return env.devAuthToken;
  }

  try {
    return await withTimeout(
      teams.authentication.getAuthToken(),
      SSO_TIMEOUT_MS,
      'Teams SSO'
    );
  } catch (error) {
    if (import.meta.env.DEV && env.devAuthToken) {
      return env.devAuthToken;
    }
    throw error instanceof Error ? error : new Error('Authentication failed');
  }
}
