import { NextResponse } from "next/server";
import { moveTaskFile } from "@/lib/vault";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { taskId, action } = body;

    if (!taskId || !action) {
      return NextResponse.json(
        { error: "Missing taskId or action" },
        { status: 400 }
      );
    }

    if (action !== "approve" && action !== "reject") {
      return NextResponse.json(
        { error: "Action must be 'approve' or 'reject'" },
        { status: 400 }
      );
    }

    const targetFolder = action === "approve" ? "Approved" : "Rejected";
    const result = moveTaskFile(taskId, "Pending_Approval", targetFolder);

    if (result.success) {
      return NextResponse.json({
        success: true,
        message: `Task ${taskId} has been ${action}d`,
      });
    } else {
      return NextResponse.json(
        { error: result.error || "Failed to process action" },
        { status: 500 }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to process approval", details: String(error) },
      { status: 500 }
    );
  }
}
