import { NextRequest, NextResponse } from "next/server";
import { listTaskFiles, parseTaskFile, getVaultPath } from "@/lib/vault";
import * as fs from "fs";
import * as path from "path";

// Extract a meaningful snippet from task content
function extractSnippet(content: string): string {
  // Try to find email subject
  const subjectMatch = content.match(/\*\*Subject:\*\*\s*(.+)/);
  if (subjectMatch) {
    return `Subject: ${subjectMatch[1].trim()}`;
  }

  // Try to find email snippet
  const snippetMatch = content.match(/\*\*Snippet:\*\*\s*\n?(.+)/);
  if (snippetMatch) {
    return snippetMatch[1].trim().slice(0, 150);
  }

  // Try to find sender
  const fromMatch = content.match(/from\s+([^\n]+)/i);
  if (fromMatch) {
    return `From: ${fromMatch[1].trim().slice(0, 100)}`;
  }

  // Try to find description section
  const descMatch = content.match(/## Description\s*\n+([^#\n][^\n]+)/);
  if (descMatch) {
    return descMatch[1].trim().slice(0, 150);
  }

  // Fallback: get first meaningful line (skip headers and frontmatter)
  const lines = content.split('\n')
    .filter(l => l.trim() && !l.startsWith('#') && !l.startsWith('---') && !l.includes(':'))
    .slice(0, 1);

  if (lines.length > 0) {
    return lines[0].trim().slice(0, 150);
  }

  return "";
}

// GET - List all tasks in Needs_Action
export async function GET() {
  try {
    const files = listTaskFiles("Needs_Action");
    const tasks = files.map((filePath) => {
      const task = parseTaskFile(filePath);
      const snippet = extractSnippet(task.content);

      return {
        id: task.id,
        filename: task.filename,
        title: task.title,
        source: task.source,
        priority: task.priority,
        created: task.created,
        snippet: snippet,
      };
    });

    // Sort by created date (newest first)
    tasks.sort((a, b) => b.created.localeCompare(a.created));

    return NextResponse.json(tasks);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get tasks", details: String(error) },
      { status: 500 }
    );
  }
}

// DELETE - Delete a task from Needs_Action
export async function DELETE(request: NextRequest) {
  try {
    const { taskId } = await request.json();

    if (!taskId) {
      return NextResponse.json(
        { error: "taskId is required" },
        { status: 400 }
      );
    }

    const vaultPath = getVaultPath();
    const taskPath = path.join(vaultPath, "Needs_Action", `${taskId}.md`);

    // Check if file exists
    if (!fs.existsSync(taskPath)) {
      return NextResponse.json(
        { error: "Task not found" },
        { status: 404 }
      );
    }

    // Delete the file
    fs.unlinkSync(taskPath);

    return NextResponse.json({ success: true, message: `Deleted task: ${taskId}` });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to delete task", details: String(error) },
      { status: 500 }
    );
  }
}
