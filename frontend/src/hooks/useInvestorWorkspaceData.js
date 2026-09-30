import { useEffect, useState } from "react";
import {
  analyzeHistory,
  getAIContext,
  getHistory,
  getMonitoringEvents,
  getMonitoringSnapshots,
  getProfile,
  getStressHistory,
} from "../services/api";

async function settle(request, fallback) {
  try {
    return { value: await request(), error: "" };
  } catch (error) {
    return { value: fallback, error: error.message || "Unable to load this data." };
  }
}

export default function useInvestorWorkspaceData() {
  const [workspace, setWorkspace] = useState({
    userId: null,
    profile: null,
    transactions: [],
    historyAnalysis: null,
    stressHistory: [],
    snapshots: [],
    events: [],
    aiContext: null,
    errors: {},
    loading: true,
  });

  useEffect(() => {
    const userId = localStorage.getItem("investtwin.user_id");
    if (!userId) {
      setWorkspace((current) => ({ ...current, loading: false }));
      return undefined;
    }

    let active = true;
    Promise.all([
      settle(() => getProfile(userId), null),
      settle(() => getHistory(userId), []),
      settle(() => analyzeHistory(userId), null),
      settle(() => getStressHistory(userId), []),
      settle(() => getMonitoringSnapshots(userId), { data: [] }),
      settle(() => getMonitoringEvents(userId), { data: [] }),
      settle(() => getAIContext(userId), null),
    ]).then(([profile, history, analysis, stress, snapshots, events, context]) => {
      if (!active) return;
      setWorkspace({
        userId,
        profile: profile.value,
        transactions: Array.isArray(history.value) ? history.value : [],
        historyAnalysis: analysis.value,
        stressHistory: Array.isArray(stress.value) ? stress.value : [],
        snapshots: snapshots.value?.data || [],
        events: events.value?.data || [],
        aiContext: context.value?.context || null,
        errors: {
          profile: profile.error,
          history: history.error || analysis.error,
          stress: stress.error,
          monitoring: snapshots.error || events.error,
          context: context.error,
        },
        loading: false,
      });
    });

    return () => {
      active = false;
    };
  }, []);

  return workspace;
}