// Dashboard TypeScript Types

export interface WatcherStatus {
  name: string;
  status: "running" | "stopped" | "error";
  lastCheck: string;
}

export interface SystemStatus {
  watchers: WatcherStatus[];
  overallStatus: "healthy" | "degraded" | "error";
  lastUpdated: string;
}

export interface TaskCounts {
  needs_action: number;
  pending_approval: number;
  in_progress: number;
  done: number;
  approved: number;
  rejected: number;
}

export interface Task {
  id: string;
  filename: string;
  title: string;
  source: string;
  priority: string;
  created: string;
  content: string;
}

export interface ProposedAction {
  actionId: string;
  type: string;
  confidence: number;
  reasoning: string;
  details: Record<string, unknown>;
  handbookReferences: string[];
}

export interface PendingApproval {
  task: Task;
  action: ProposedAction;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  event_type: string;
  actor: string;
  task_id: string | null;
  action_id: string | null;
  details: {
    summary?: string;
    [key: string]: unknown;
  };
  success: boolean;
  error_message: string | null;
}

export interface DashboardData {
  status: SystemStatus;
  taskCounts: TaskCounts;
  approvals: PendingApproval[];
  activity: AuditEntry[];
  lastUpdated: string;
}

export interface DailyMetrics {
  date: string;
  completed: number;
  approved: number;
  rejected: number;
}
