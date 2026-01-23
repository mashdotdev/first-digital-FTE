import { NextResponse } from "next/server";
import { cleanupJunkTasks } from "@/lib/vault";

// POST - Run cleanup of junk tasks
export async function POST() {
  try {
    const result = cleanupJunkTasks();
    return NextResponse.json({
      success: true,
      deleted: result.deleted,
      deletedTasks: result.deletedTasks,
      message: result.deleted > 0
        ? `Cleaned up ${result.deleted} junk task(s)`
        : "No junk tasks found",
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to cleanup tasks", details: String(error) },
      { status: 500 }
    );
  }
}

// GET - Check what would be cleaned up (dry run)
export async function GET() {
  try {
    // For now, just run the actual cleanup
    // In future, could add a dry-run mode
    const result = cleanupJunkTasks();
    return NextResponse.json({
      success: true,
      deleted: result.deleted,
      deletedTasks: result.deletedTasks,
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to check for junk tasks", details: String(error) },
      { status: 500 }
    );
  }
}
