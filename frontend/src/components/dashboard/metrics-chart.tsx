"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DailyMetrics } from "@/lib/types";

interface MetricsChartProps {
  metrics: DailyMetrics[];
  isLoading: boolean;
}

export function MetricsChart({ metrics, isLoading }: MetricsChartProps) {
  if (isLoading && metrics.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Weekly Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
      </Card>
    );
  }

  // Format dates for display
  const chartData = metrics.map((m) => ({
    ...m,
    day: new Date(m.date).toLocaleDateString("en-US", { weekday: "short" }),
    total: m.completed + m.approved + m.rejected,
  }));

  const hasData = chartData.some((d) => d.total > 0);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Weekly Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {!hasData ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
            No activity data available
          </div>
        ) : (
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="day"
                  tickLine={false}
                  axisLine={false}
                  fontSize={12}
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  fontSize={12}
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                  allowDecimals={false}
                />
                <Tooltip
                  cursor={{ fill: "hsl(var(--muted))", opacity: 0.3 }}
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "6px",
                    fontSize: "12px",
                  }}
                  labelStyle={{ fontWeight: 500, marginBottom: "4px" }}
                />
                <Bar
                  dataKey="approved"
                  stackId="a"
                  fill="hsl(142, 76%, 36%)"
                  radius={[0, 0, 0, 0]}
                  name="Approved"
                />
                <Bar
                  dataKey="completed"
                  stackId="a"
                  fill="hsl(221, 83%, 53%)"
                  radius={[0, 0, 0, 0]}
                  name="Completed"
                />
                <Bar
                  dataKey="rejected"
                  stackId="a"
                  fill="hsl(0, 84%, 60%)"
                  radius={[4, 4, 0, 0]}
                  name="Rejected"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="flex items-center justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span className="text-muted-foreground">Approved</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-full bg-blue-600" />
            <span className="text-muted-foreground">Completed</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-full bg-red-500" />
            <span className="text-muted-foreground">Rejected</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
