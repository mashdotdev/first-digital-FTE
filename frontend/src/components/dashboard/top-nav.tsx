"use client";

import { RefreshCw, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

interface TopNavProps {
  onRefresh: () => void;
  isLoading: boolean;
  lastUpdated: Date | null;
}

export function TopNav({ onRefresh, isLoading, lastUpdated }: TopNavProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-backdrop-filter:bg-white/60">
      <div className="container mx-auto flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            FTE
          </div>
          <h1 className="text-lg font-semibold tracking-tight">
            Digital FTE Dashboard
          </h1>
        </div>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-sm text-muted-foreground hidden sm:inline">
              Updated {formatTime(lastUpdated)}
            </span>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
            <span className="hidden sm:inline ml-2">Refresh</span>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-sm">
                <Settings className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem disabled>
                Settings (Coming Soon)
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
