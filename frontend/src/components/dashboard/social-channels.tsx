"use client";

import { Linkedin, MessageCircle, Twitter, AlertCircle, CheckCircle2, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { SocialChannelsData, SocialPlatform } from "@/lib/types";

interface SocialChannelsProps {
  data: SocialChannelsData | null;
  isLoading: boolean;
}

function getPlatformIcon(platform: SocialPlatform) {
  switch (platform) {
    case "linkedin":
      return <Linkedin className="h-4 w-4 text-[#0A66C2]" />;
    case "whatsapp":
      return <MessageCircle className="h-4 w-4 text-[#25D366]" />;
    case "twitter":
      return <Twitter className="h-4 w-4 text-[#1DA1F2]" />;
    default:
      return <AlertCircle className="h-4 w-4" />;
  }
}

function getStatusBadge(status: string) {
  switch (status) {
    case "connected":
      return (
        <Badge className="bg-green-500 hover:bg-green-600 text-xs">
          <CheckCircle2 className="h-3 w-3 mr-1" />
          Connected
        </Badge>
      );
    case "not_configured":
      return (
        <Badge variant="secondary" className="text-xs">
          <Clock className="h-3 w-3 mr-1" />
          Not Configured
        </Badge>
      );
    case "error":
      return (
        <Badge variant="destructive" className="text-xs">
          <AlertCircle className="h-3 w-3 mr-1" />
          Error
        </Badge>
      );
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

function formatRelativeTime(dateStr: string | undefined) {
  if (!dateStr) return null;

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

export function SocialChannels({ data, isLoading }: SocialChannelsProps) {
  if (isLoading && !data) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Social Channels</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-4 rounded" />
                  <Skeleton className="h-4 w-20" />
                </div>
                <Skeleton className="h-5 w-24" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const channels = data?.channels ?? [];

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Social Channels</CardTitle>
          {data && data.totalPendingPosts > 0 && (
            <Badge variant="secondary" className="text-xs">
              {data.totalPendingPosts} pending
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {channels.map((channel) => (
            <div
              key={channel.platform}
              className="flex items-center justify-between py-2 border-b last:border-0"
            >
              <div className="flex items-center gap-3">
                {getPlatformIcon(channel.platform)}
                <div>
                  <span className="font-medium text-sm">{channel.name}</span>
                  {channel.lastActivity && (
                    <p className="text-xs text-muted-foreground">
                      Last: {formatRelativeTime(channel.lastActivity)}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {channel.pendingPosts && channel.pendingPosts > 0 ? (
                  <Badge variant="outline" className="text-xs">
                    {channel.pendingPosts} queued
                  </Badge>
                ) : null}
                {getStatusBadge(channel.status)}
              </div>
            </div>
          ))}
        </div>
        {channels.every((c) => c.status === "not_configured") && (
          <p className="text-xs text-muted-foreground mt-3 text-center">
            Configure API keys in .env to enable channels
          </p>
        )}
      </CardContent>
    </Card>
  );
}
