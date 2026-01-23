import * as fs from "fs";
import * as path from "path";
import type {
  WatcherStatus,
  SystemStatus,
  Task,
  ProposedAction,
  PendingApproval,
  AuditEntry,
  TaskCounts,
  DailyMetrics,
} from "./types";

// Get vault path from env or use default relative path
export function getVaultPath(): string {
  return process.env.VAULT_PATH || path.join(process.cwd(), "..", "AI_Employee_Valut");
}

// Parse Dashboard.md to extract system status
export function getSystemStatus(): SystemStatus {
  const vaultPath = getVaultPath();
  const dashboardPath = path.join(vaultPath, "Dashboard.md");

  try {
    const content = fs.readFileSync(dashboardPath, "utf-8");

    // Extract overall status from frontmatter
    const statusMatch = content.match(/status:\s*(\w+)/);
    const overallStatus = (statusMatch?.[1] || "unknown") as SystemStatus["overallStatus"];

    // Extract last_updated from frontmatter
    const lastUpdatedMatch = content.match(/last_updated:\s*(.+)/);
    const lastUpdated = lastUpdatedMatch?.[1] || new Date().toISOString();

    // Parse watcher status table
    const watchers: WatcherStatus[] = [];
    const tableRegex = /\|\s*(\w+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|/g;
    let match;

    while ((match = tableRegex.exec(content)) !== null) {
      const [, name, statusCell, lastCheck] = match;
      if (name === "Component" || name === "---") continue;

      const isRunning = statusCell.includes("Running") || statusCell.includes("🟢");
      watchers.push({
        name: name.trim(),
        status: isRunning ? "running" : "stopped",
        lastCheck: lastCheck.trim(),
      });
    }

    return {
      watchers,
      overallStatus: overallStatus === "healthy" || overallStatus === "degraded" || overallStatus === "error"
        ? overallStatus
        : "degraded",
      lastUpdated,
    };
  } catch {
    return {
      watchers: [],
      overallStatus: "error",
      lastUpdated: new Date().toISOString(),
    };
  }
}

// Count tasks in each folder
export function getTaskCounts(): TaskCounts {
  const vaultPath = getVaultPath();
  const folders = {
    needs_action: "Needs_Action",
    pending_approval: "Pending_Approval",
    in_progress: "In_Progress",
    done: "Done",
    approved: "Approved",
    rejected: "Rejected",
  };

  const counts: TaskCounts = {
    needs_action: 0,
    pending_approval: 0,
    in_progress: 0,
    done: 0,
    approved: 0,
    rejected: 0,
  };

  for (const [key, folder] of Object.entries(folders)) {
    const folderPath = path.join(vaultPath, folder);
    try {
      const files = fs.readdirSync(folderPath).filter((f) => f.endsWith(".md"));
      counts[key as keyof TaskCounts] = files.length;
    } catch {
      counts[key as keyof TaskCounts] = 0;
    }
  }

  return counts;
}

// List markdown files in a vault folder
export function listTaskFiles(folder: string): string[] {
  const vaultPath = getVaultPath();
  const folderPath = path.join(vaultPath, folder);

  try {
    return fs
      .readdirSync(folderPath)
      .filter((f) => f.endsWith(".md"))
      .map((f) => path.join(folderPath, f));
  } catch {
    return [];
  }
}

// Parse a task markdown file
export function parseTaskFile(filePath: string): Task {
  const content = fs.readFileSync(filePath, "utf-8");
  const filename = path.basename(filePath, ".md");

  // Extract title from first heading
  const titleMatch = content.match(/^#\s+(?:Task:\s*)?(.+)/m);
  const title = titleMatch?.[1] || filename;

  // Extract metadata
  const sourceMatch = content.match(/\*\*Source:\*\*\s*(.+)/);
  const priorityMatch = content.match(/\*\*Priority:\*\*\s*(.+)/);
  const createdMatch = content.match(/\*\*Created:\*\*\s*(.+)/);

  return {
    id: filename,
    filename,
    title: title.trim(),
    source: sourceMatch?.[1]?.trim() || "Unknown",
    priority: priorityMatch?.[1]?.trim() || "P3",
    created: createdMatch?.[1]?.trim() || new Date().toISOString().split("T")[0],
    content,
  };
}

// Parse proposed action from task content
export function parseProposedAction(content: string): ProposedAction | null {
  // Check if there's a proposed action section
  if (!content.includes("Proposed Action")) {
    return null;
  }

  // Extract action ID
  const actionIdMatch = content.match(/\*\*Action ID:\*\*\s*(\S+)/);
  const actionId = actionIdMatch?.[1] || `action_${Date.now()}`;

  // Extract type
  const typeMatch = content.match(/\*\*Type:\*\*\s*(.+)/);
  const type = typeMatch?.[1]?.trim() || "Unknown";

  // Extract confidence
  const confidenceMatch = content.match(/\*\*Confidence:\*\*\s*(\d+)/);
  const confidence = confidenceMatch ? parseInt(confidenceMatch[1], 10) : 0;

  // Extract reasoning section
  const reasoningMatch = content.match(/### Reasoning\s*([\s\S]*?)(?=###|---|\n\n\*\*)/);
  const reasoning = reasoningMatch?.[1]?.trim() || "";

  // Extract JSON details
  let details: Record<string, unknown> = {};
  const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
  if (jsonMatch) {
    try {
      details = JSON.parse(jsonMatch[1]);
    } catch {
      details = {};
    }
  }

  // Extract handbook references
  const referencesMatch = content.match(/### Handbook References\s*([\s\S]*?)(?=---|$)/);
  const handbookReferences: string[] = [];
  if (referencesMatch) {
    const lines = referencesMatch[1].split("\n");
    for (const line of lines) {
      const trimmed = line.replace(/^-\s*/, "").trim();
      if (trimmed) handbookReferences.push(trimmed);
    }
  }

  return {
    actionId,
    type,
    confidence,
    reasoning,
    details,
    handbookReferences,
  };
}

// Get pending approvals with full details
export function getPendingApprovals(): PendingApproval[] {
  const files = listTaskFiles("Pending_Approval");
  const approvals: PendingApproval[] = [];

  for (const filePath of files) {
    const task = parseTaskFile(filePath);
    const action = parseProposedAction(task.content);

    if (action) {
      approvals.push({ task, action });
    } else {
      // Even without a parsed action, include the task
      approvals.push({
        task,
        action: {
          actionId: `action_${task.id}`,
          type: "Unknown",
          confidence: 0,
          reasoning: "Action details not found",
          details: {},
          handbookReferences: [],
        },
      });
    }
  }

  return approvals;
}

// Read audit log entries
export function readAuditLogs(limit: number = 50): AuditEntry[] {
  const vaultPath = getVaultPath();
  const logsPath = path.join(vaultPath, "Logs");

  try {
    // Find the most recent audit log file
    const files = fs
      .readdirSync(logsPath)
      .filter((f) => f.startsWith("audit_") && f.endsWith(".jsonl"))
      .sort()
      .reverse();

    if (files.length === 0) {
      return [];
    }

    const logFile = path.join(logsPath, files[0]);
    const content = fs.readFileSync(logFile, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);

    // Parse entries and return most recent first
    const entries: AuditEntry[] = [];
    for (const line of lines.slice(-limit * 2)) {
      try {
        const entry = JSON.parse(line) as AuditEntry;
        entries.push(entry);
      } catch {
        continue;
      }
    }

    // Sort by timestamp descending and limit
    return entries
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit);
  } catch {
    return [];
  }
}

// Move a task file between folders
export function moveTaskFile(
  taskId: string,
  fromFolder: string,
  toFolder: string
): { success: boolean; error?: string } {
  const vaultPath = getVaultPath();
  const fromPath = path.join(vaultPath, fromFolder, `${taskId}.md`);
  const toPath = path.join(vaultPath, toFolder, `${taskId}.md`);

  try {
    // Check source exists
    if (!fs.existsSync(fromPath)) {
      return { success: false, error: `Task file not found: ${taskId}` };
    }

    // Ensure destination folder exists
    const toDir = path.join(vaultPath, toFolder);
    if (!fs.existsSync(toDir)) {
      fs.mkdirSync(toDir, { recursive: true });
    }

    // Move the file
    fs.renameSync(fromPath, toPath);
    return { success: true };
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

// Get daily metrics for the last N days
export function getDailyMetrics(days: number = 7): DailyMetrics[] {
  const entries = readAuditLogs(500);
  const metricsMap = new Map<string, DailyMetrics>();

  // Initialize last N days
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split("T")[0];
    metricsMap.set(dateStr, { date: dateStr, completed: 0, approved: 0, rejected: 0 });
  }

  // Count events by day
  for (const entry of entries) {
    const dateStr = entry.timestamp.split("T")[0];
    const metrics = metricsMap.get(dateStr);
    if (!metrics) continue;

    if (entry.event_type === "task_completed") {
      metrics.completed++;
    } else if (entry.event_type === "action_approved") {
      metrics.approved++;
    } else if (entry.event_type === "action_rejected") {
      metrics.rejected++;
    }
  }

  // Return sorted by date ascending
  return Array.from(metricsMap.values()).sort((a, b) => a.date.localeCompare(b.date));
}
