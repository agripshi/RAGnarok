import * as teams from '@microsoft/teams-js';
import { env } from '../config/env';
import type { TeamsContextPayload } from '../types/api';

export async function initializeTeams(): Promise<boolean> {
  try {
    await teams.app.initialize();
    return true;
  } catch {
    return false;
  }
}

export async function getTeamsContext(): Promise<TeamsContextPayload> {
  try {
    const ctx = await teams.app.getContext();
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

export async function getTeamsSsoToken(): Promise<string> {
  try {
    return await teams.authentication.getAuthToken();
  } catch (error) {
    if (import.meta.env.DEV && env.devAuthToken) {
      return env.devAuthToken;
    }
    throw error;
  }
}
