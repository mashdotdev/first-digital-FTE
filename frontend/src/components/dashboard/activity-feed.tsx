"use client";

import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  Mail,
  Play,
  XCircle,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import type { AuditEntry } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ActivityFeedProps {
  activity: AuditEntry[];
  isLoading: boolean;
}

function getEventIcon(eventType: string, success: boolean) {
  const className = cn(
    "h-4 w-4",
    success ? "text-green-500" : "text-red-500"
  );

  switch (eventType) {
    case "task_created":
      return <FileText className="h-4 w-4 text-blue-500" />;
    case "task_completed":
      return <CheckCircle2 className={className} />;
    case "action_approved":
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "action_rejected":
      return <XCircle className="h-4 w-4 text-red-500" />;
    case "action_executed":
      return <Zap className={className} />;
    case "email_sent":
      return <Mail className={className} />;
    case "watcher_started":
      return <Play className="h-4 w-4 text-green-500" />;
    case "orchestrator_started":
      return <Activity className="h-4 w-4 text-blue-500" />;
    case "health_check":
      return <Activity className="h-4 w-4 text-muted-foreground" />;
    case "error":
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

function formatEventType(eventType: string): string {
  return eventType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffSecs < 60) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function ActivityFeed({ activity, isLoading }: ActivityFeedProps) {
  if (isLoading && activity.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-4 w-4 rounded-full" />
                <div className="flex-1 space-y-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0">
        {activity.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
            <Activity className="h-8 w-8 mb-2" />
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-1">
              {activity.map((entry, index) => (
                <div
                  key={`${entry.id}-${index}`}
                  className="flex items-start gap-3 py-2 border-b last:border-0"
                >
                  <div className="mt-0.5">
                    {getEventIcon(entry.event_type, entry.success)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium">
                        {formatEventType(entry.event_type)}
                      </span>
                      {!entry.success && (
                        <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                          Failed
                        </Badge>
                      )}
                    </div>
                    {entry.details?.summary && (
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                        {entry.details.summary}
                      </p>
                    )}
                    {entry.error_message && (
                      <p className="text-xs text-red-500 mt-0.5 line-clamp-2">
                        {entry.error_message}
                      </p>
                    )}
                    <span className="text-[10px] text-muted-foreground">
                      {formatRelativeTime(entry.timestamp)}
                      {entry.actor && ` \u00B7 ${entry.actor}`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
