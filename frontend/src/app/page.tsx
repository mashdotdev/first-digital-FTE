"use client";

import { useDashboard } from "@/hooks/use-dashboard";
import {
  TopNav,
  StatusCards,
  PendingApprovals,
  ActivityFeed,
  MetricsChart,
  SocialChannels,
  TaskQueue,
} from "@/components/dashboard";
import { toast } from "sonner";

export default function Dashboard() {
  const {
    status,
    taskCounts,
    approvals,
    activity,
    metrics,
    socialChannels,
    queuedTasks,
    isLoading,
    error,
    lastUpdated,
    refresh,
    handleApproval,
    handleDeleteTask,
    handleCleanupTasks,
  } = useDashboard(30000); // 30 second polling

  const onApprove = async (taskId: string, action: "approve" | "reject") => {
    const result = await handleApproval(taskId, action);

    if (result.success) {
      toast.success(
        action === "approve"
          ? "Task approved successfully"
          : "Task rejected"
      );
    } else {
      toast.error(result.error || "Failed to process action");
    }

    return result;
  };

  // Use metrics from API or generate placeholder if empty
  const displayMetrics = metrics.length > 0 ? metrics : generatePlaceholderMetrics();

  return (
    <div className="min-h-screen bg-zinc-50">
      <TopNav
        onRefresh={refresh}
        isLoading={isLoading}
        lastUpdated={lastUpdated}
      />

      <main className="container mx-auto px-4 py-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Status Cards Row */}
        <StatusCards
          status={status}
          taskCounts={taskCounts}
          isLoading={isLoading}
        />

        {/* Social Channels */}
        <SocialChannels
          data={socialChannels}
          isLoading={isLoading}
        />

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Task Queue (Needs Action) */}
          <TaskQueue
            tasks={queuedTasks}
            isLoading={isLoading}
            onDelete={handleDeleteTask}
            onRefresh={refresh}
            onCleanup={handleCleanupTasks}
          />

          {/* Pending Approvals */}
          <PendingApprovals
            approvals={approvals}
            isLoading={isLoading}
            onApprove={onApprove}
          />
        </div>

        {/* Activity Feed - Full Width */}
        <ActivityFeed
          activity={activity}
          isLoading={isLoading}
        />

        {/* Metrics Chart */}
        <MetricsChart
          metrics={displayMetrics}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}

// Generate placeholder metrics for the last 7 days
function generatePlaceholderMetrics() {
  const metrics = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    metrics.push({
      date: date.toISOString().split("T")[0],
      completed: 0,
      approved: 0,
      rejected: 0,
    });
  }
  return metrics;
}
