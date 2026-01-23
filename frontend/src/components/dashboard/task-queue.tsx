"use client";

import { useState } from "react";
import { Trash2, Mail, FileText, MessageCircle, RefreshCw, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface QueuedTask {
  id: string;
  filename: string;
  title: string;
  source: string;
  priority: string;
  created: string;
  snippet: string;
}

interface TaskQueueProps {
  tasks: QueuedTask[];
  isLoading: boolean;
  onDelete: (taskId: string) => Promise<{ success: boolean; error?: string }>;
  onRefresh: () => void;
  onCleanup: () => Promise<{ success: boolean; deleted: number; error?: string }>;
}

function getSourceIcon(source: string) {
  switch (source.toLowerCase()) {
    case "gmail":
      return <Mail className="h-4 w-4 text-red-500" />;
    case "whatsapp":
      return <MessageCircle className="h-4 w-4 text-green-500" />;
    default:
      return <FileText className="h-4 w-4 text-gray-500" />;
  }
}

function getPriorityBadge(priority: string) {
  switch (priority) {
    case "P0":
      return <Badge variant="destructive" className="text-xs">P0</Badge>;
    case "P1":
      return <Badge className="bg-orange-500 hover:bg-orange-600 text-xs">P1</Badge>;
    case "P2":
      return <Badge className="bg-yellow-500 hover:bg-yellow-600 text-xs">P2</Badge>;
    default:
      return <Badge variant="secondary" className="text-xs">{priority}</Badge>;
  }
}

function formatRelativeTime(dateStr: string) {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  } catch {
    return dateStr;
  }
}

export function TaskQueue({ tasks, isLoading, onDelete, onRefresh, onCleanup }: TaskQueueProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<QueuedTask | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [cleaning, setCleaning] = useState(false);

  const handleCleanup = async () => {
    setCleaning(true);
    const result = await onCleanup();
    setCleaning(false);
    if (result.success && result.deleted > 0) {
      onRefresh();
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;

    setDeleting(true);
    const result = await onDelete(deleteConfirm.id);
    setDeleting(false);
    setDeleteConfirm(null);

    if (!result.success) {
      console.error("Failed to delete:", result.error);
    }
  };

  if (isLoading && tasks.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Task Queue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-2 border rounded">
                <div className="space-y-1">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-8 w-8" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Task Queue (Needs Action)</CardTitle>
            <div className="flex items-center gap-2">
              {tasks.length > 0 && (
                <Badge variant="secondary">{tasks.length} waiting</Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={handleCleanup}
                disabled={cleaning || tasks.length === 0}
                className="text-xs"
              >
                <Sparkles className="h-3 w-3 mr-1" />
                {cleaning ? "Cleaning..." : "Auto Clean"}
              </Button>
              <Button variant="ghost" size="icon-sm" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Tasks waiting for AI to process. Delete unwanted tasks to save API calls.
          </p>
        </CardHeader>
        <CardContent className="flex-1 min-h-0">
          {tasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
              <FileText className="h-8 w-8 mb-2" />
              <p className="text-sm">No tasks in queue</p>
            </div>
          ) : (
            <ScrollArea className="h-[300px] pr-4">
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-start justify-between p-3 border rounded-lg hover:bg-zinc-50 transition-colors"
                  >
                    <div className="flex items-start gap-3 min-w-0 flex-1">
                      {getSourceIcon(task.source)}
                      <div className="min-w-0 flex-1">
                        <h4 className="font-medium text-sm truncate">{task.title}</h4>
                        {task.snippet && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {task.snippet}
                          </p>
                        )}
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <span className="text-xs text-muted-foreground capitalize">
                            {task.source}
                          </span>
                          {getPriorityBadge(task.priority)}
                          <span className="text-xs text-muted-foreground">
                            {formatRelativeTime(task.created)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={() => setDeleteConfirm(task)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Task</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{deleteConfirm?.title}</strong>?
              <br />
              <br />
              This will remove the task from the queue and the AI will not process it.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
