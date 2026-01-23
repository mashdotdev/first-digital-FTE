"use client";

import { useState } from "react";
import { Check, ChevronDown, ChevronUp, X, Mail, FileText, Linkedin, MessageCircle, Twitter } from "lucide-react";
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
import type { PendingApproval } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PendingApprovalsProps {
  approvals: PendingApproval[];
  isLoading: boolean;
  onApprove: (taskId: string, action: "approve" | "reject") => Promise<{ success: boolean; error?: string }>;
}

function getActionIcon(actionType: string, content?: string) {
  const type = actionType.toLowerCase();
  const contentLower = content?.toLowerCase() || "";

  // Social media platforms
  if (type.includes("linkedin") || contentLower.includes("platform: linkedin")) {
    return <Linkedin className="h-4 w-4 text-[#0A66C2]" />;
  }
  if (type.includes("whatsapp") || contentLower.includes("platform: whatsapp") || type.includes("whatsapp")) {
    return <MessageCircle className="h-4 w-4 text-[#25D366]" />;
  }
  if (type.includes("twitter") || contentLower.includes("platform: twitter")) {
    return <Twitter className="h-4 w-4 text-[#1DA1F2]" />;
  }

  // Email
  if (type.includes("email")) {
    return <Mail className="h-4 w-4" />;
  }

  // Default
  return <FileText className="h-4 w-4" />;
}

function getConfidenceBadge(confidence: number) {
  if (confidence >= 90) {
    return <Badge className="bg-green-500 hover:bg-green-600">{confidence}%</Badge>;
  } else if (confidence >= 70) {
    return <Badge className="bg-yellow-500 hover:bg-yellow-600">{confidence}%</Badge>;
  } else {
    return <Badge variant="destructive">{confidence}%</Badge>;
  }
}

function formatRelativeTime(dateStr: string) {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export function PendingApprovals({
  approvals,
  isLoading,
  onApprove,
}: PendingApprovalsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<{
    taskId: string;
    action: "approve" | "reject";
    title: string;
  } | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleAction = async () => {
    if (!confirmAction) return;

    setProcessing(true);
    const result = await onApprove(confirmAction.taskId, confirmAction.action);
    setProcessing(false);
    setConfirmAction(null);

    if (!result.success) {
      // You could add toast notification here
      console.error("Failed to process:", result.error);
    }
  };

  if (isLoading && approvals.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base">Pending Approvals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
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
            <CardTitle className="text-base">Pending Approvals</CardTitle>
            {approvals.length > 0 && (
              <Badge variant="secondary">{approvals.length}</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex-1 min-h-0">
          {approvals.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
              <Check className="h-8 w-8 mb-2" />
              <p className="text-sm">No pending approvals</p>
            </div>
          ) : (
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {approvals.map((approval) => {
                  const isExpanded = expandedId === approval.task.id;

                  return (
                    <div
                      key={approval.task.id}
                      className="rounded-lg border p-3 space-y-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-2 min-w-0">
                          {getActionIcon(approval.action.type, approval.task.content)}
                          <div className="min-w-0">
                            <h4 className="font-medium text-sm truncate">
                              {approval.task.title}
                            </h4>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              <span className="text-xs text-muted-foreground">
                                {approval.action.type.replace("ActionType.", "")}
                              </span>
                              {getConfidenceBadge(approval.action.confidence)}
                              <span className="text-xs text-muted-foreground">
                                {formatRelativeTime(approval.task.created)}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={() =>
                            setExpandedId(isExpanded ? null : approval.task.id)
                          }
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </Button>
                      </div>

                      <div
                        className={cn(
                          "overflow-hidden transition-all",
                          isExpanded ? "max-h-96" : "max-h-0"
                        )}
                      >
                        <div className="pt-2 space-y-2 text-sm">
                          <div>
                            <span className="font-medium">Reasoning:</span>
                            <p className="text-muted-foreground mt-1">
                              {approval.action.reasoning || "No reasoning provided"}
                            </p>
                          </div>
                          {approval.action.handbookReferences.length > 0 && (
                            <div>
                              <span className="font-medium">References:</span>
                              <ul className="list-disc list-inside text-muted-foreground mt-1">
                                {approval.action.handbookReferences.map((ref, i) => (
                                  <li key={i} className="text-xs">{ref}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 pt-1">
                        <Button
                          size="sm"
                          className="flex-1 bg-green-600 hover:bg-green-700"
                          onClick={() =>
                            setConfirmAction({
                              taskId: approval.task.id,
                              action: "approve",
                              title: approval.task.title,
                            })
                          }
                        >
                          <Check className="h-3 w-3 mr-1" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          className="flex-1"
                          onClick={() =>
                            setConfirmAction({
                              taskId: approval.task.id,
                              action: "reject",
                              title: approval.task.title,
                            })
                          }
                        >
                          <X className="h-3 w-3 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={!!confirmAction} onOpenChange={() => setConfirmAction(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {confirmAction?.action === "approve" ? "Approve" : "Reject"} Task
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to {confirmAction?.action}{" "}
              <strong>{confirmAction?.title}</strong>?
              {confirmAction?.action === "approve"
                ? " The AI will execute the proposed action."
                : " The task will be moved to rejected."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={processing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleAction}
              disabled={processing}
              className={
                confirmAction?.action === "approve"
                  ? "bg-green-600 hover:bg-green-700"
                  : "bg-destructive hover:bg-destructive/90"
              }
            >
              {processing ? "Processing..." : confirmAction?.action === "approve" ? "Approve" : "Reject"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
