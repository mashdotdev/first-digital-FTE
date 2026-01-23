"use client";

import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Inbox,
  ListTodo,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { SystemStatus, TaskCounts } from "@/lib/types";

interface StatusCardsProps {
  status: SystemStatus | null;
  taskCounts: TaskCounts | null;
  isLoading: boolean;
}

export function StatusCards({ status, taskCounts, isLoading }: StatusCardsProps) {
  if (isLoading && !status && !taskCounts) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-12 mb-1" />
              <Skeleton className="h-3 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const runningWatchers = status?.watchers.filter((w) => w.status === "running").length ?? 0;
  const totalWatchers = status?.watchers.length ?? 0;
  const systemHealthy = status?.overallStatus === "healthy";
  const systemDegraded = status?.overallStatus === "degraded";

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* System Status */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Status</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            {systemHealthy ? (
              <Badge className="bg-green-500 hover:bg-green-600">Healthy</Badge>
            ) : systemDegraded ? (
              <Badge className="bg-yellow-500 hover:bg-yellow-600">Degraded</Badge>
            ) : (
              <Badge variant="destructive">Error</Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {runningWatchers}/{totalWatchers} watchers running
          </p>
          {status?.watchers.map((watcher) => (
            <div key={watcher.name} className="flex items-center gap-2 mt-1">
              {watcher.status === "running" ? (
                <CheckCircle2 className="h-3 w-3 text-green-500" />
              ) : (
                <AlertCircle className="h-3 w-3 text-red-500" />
              )}
              <span className="text-xs capitalize">{watcher.name}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Pending Approvals */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {taskCounts?.pending_approval ?? 0}
          </div>
          <p className="text-xs text-muted-foreground">
            awaiting your review
          </p>
        </CardContent>
      </Card>

      {/* Tasks Needing Action */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Needs Action</CardTitle>
          <Inbox className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {taskCounts?.needs_action ?? 0}
          </div>
          <p className="text-xs text-muted-foreground">
            tasks to process
          </p>
        </CardContent>
      </Card>

      {/* Completed Today */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Completed</CardTitle>
          <ListTodo className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {(taskCounts?.done ?? 0) + (taskCounts?.approved ?? 0)}
          </div>
          <p className="text-xs text-muted-foreground">
            {taskCounts?.approved ?? 0} approved, {taskCounts?.done ?? 0} done
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
