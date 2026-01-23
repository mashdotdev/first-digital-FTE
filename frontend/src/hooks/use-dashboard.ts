"use client";

import { useState, useEffect, useCallback } from "react";
import type {
  SystemStatus,
  TaskCounts,
  PendingApproval,
  AuditEntry,
  DailyMetrics,
  SocialChannelsData,
  QueuedTask,
} from "@/lib/types";

interface DashboardState {
  status: SystemStatus | null;
  taskCounts: TaskCounts | null;
  approvals: PendingApproval[];
  activity: AuditEntry[];
  metrics: DailyMetrics[];
  socialChannels: SocialChannelsData | null;
  queuedTasks: QueuedTask[];
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
    socialChannels: null,
    queuedTasks: [],
    isLoading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchData = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      // Fetch all data in parallel
      const [statusRes, tasksRes, approvalsRes, activityRes, metricsRes, socialRes, queueRes] = await Promise.all([
        fetch("/api/status"),
        fetch("/api/tasks"),
        fetch("/api/approvals"),
        fetch("/api/activity?limit=30"),
        fetch("/api/metrics?days=7"),
        fetch("/api/social-channels"),
        fetch("/api/needs-action"),
      ]);

      // Check for errors
      if (!statusRes.ok || !tasksRes.ok || !approvalsRes.ok || !activityRes.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const [status, taskCounts, approvals, activity, metrics, socialChannels, queuedTasks] = await Promise.all([
        statusRes.json() as Promise<SystemStatus>,
        tasksRes.json() as Promise<TaskCounts>,
        approvalsRes.json() as Promise<PendingApproval[]>,
        activityRes.json() as Promise<AuditEntry[]>,
        metricsRes.ok ? (metricsRes.json() as Promise<DailyMetrics[]>) : Promise.resolve([]),
        socialRes.ok ? (socialRes.json() as Promise<SocialChannelsData>) : Promise.resolve(null),
        queueRes.ok ? (queueRes.json() as Promise<QueuedTask[]>) : Promise.resolve([]),
      ]);

      setState({
        status,
        taskCounts,
        approvals,
        activity,
        metrics,
        socialChannels,
        queuedTasks,
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

  // Delete a task from the queue
  const handleDeleteTask = useCallback(
    async (taskId: string) => {
      try {
        const res = await fetch("/api/needs-action", {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ taskId }),
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error || "Failed to delete task");
        }

        // Refresh data after deletion
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

  // Cleanup junk tasks automatically
  const handleCleanupTasks = useCallback(async () => {
    try {
      const res = await fetch("/api/cleanup", {
        method: "POST",
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to cleanup tasks");
      }

      const result = await res.json();

      // Refresh data after cleanup
      await fetchData();
      return { success: true, deleted: result.deleted };
    } catch (err) {
      return {
        success: false,
        deleted: 0,
        error: err instanceof Error ? err.message : "Unknown error",
      };
    }
  }, [fetchData]);

  return {
    ...state,
    refresh: fetchData,
    handleApproval,
    handleDeleteTask,
    handleCleanupTasks,
  };
}
