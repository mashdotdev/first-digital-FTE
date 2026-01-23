"use client";

import { useState, useEffect, useCallback } from "react";
import type {
  SystemStatus,
  TaskCounts,
  PendingApproval,
  AuditEntry,
  DailyMetrics,
} from "@/lib/types";

interface DashboardState {
  status: SystemStatus | null;
  taskCounts: TaskCounts | null;
  approvals: PendingApproval[];
  activity: AuditEntry[];
  metrics: DailyMetrics[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useDashboard(refreshInterval: number = 30000) {
  const [state, setState] = useState<DashboardState>({
    status: null,
    taskCounts: null,
    approvals: [],
    activity: [],
    metrics: [],
    isLoading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchData = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      // Fetch all data in parallel
      const [statusRes, tasksRes, approvalsRes, activityRes, metricsRes] = await Promise.all([
        fetch("/api/status"),
        fetch("/api/tasks"),
        fetch("/api/approvals"),
        fetch("/api/activity?limit=30"),
        fetch("/api/metrics?days=7"),
      ]);

      // Check for errors
      if (!statusRes.ok || !tasksRes.ok || !approvalsRes.ok || !activityRes.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const [status, taskCounts, approvals, activity, metrics] = await Promise.all([
        statusRes.json() as Promise<SystemStatus>,
        tasksRes.json() as Promise<TaskCounts>,
        approvalsRes.json() as Promise<PendingApproval[]>,
        activityRes.json() as Promise<AuditEntry[]>,
        metricsRes.ok ? (metricsRes.json() as Promise<DailyMetrics[]>) : Promise.resolve([]),
      ]);

      setState({
        status,
        taskCounts,
        approvals,
        activity,
        metrics,
        isLoading: false,
        error: null,
        lastUpdated: new Date(),
      });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : "Unknown error",
      }));
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval]);

  // Approve or reject a task
  const handleApproval = useCallback(
    async (taskId: string, action: "approve" | "reject") => {
      try {
        const res = await fetch("/api/approve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ taskId, action }),
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error || "Failed to process approval");
        }

        // Refresh data after approval
        await fetchData();
        return { success: true };
      } catch (err) {
        return {
          success: false,
          error: err instanceof Error ? err.message : "Unknown error",
        };
      }
    },
    [fetchData]
  );

  return {
    ...state,
    refresh: fetchData,
    handleApproval,
  };
}
