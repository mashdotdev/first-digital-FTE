import { NextResponse } from "next/server";
import { getPendingApprovals } from "@/lib/vault";

export async function GET() {
  try {
    const approvals = getPendingApprovals();
    return NextResponse.json(approvals);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get pending approvals", details: String(error) },
      { status: 500 }
    );
  }
}
