import { NextResponse } from "next/server";
import { readAuditLogs } from "@/lib/vault";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "50", 10);

    const entries = readAuditLogs(Math.min(limit, 100));
    return NextResponse.json(entries);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get activity feed", details: String(error) },
      { status: 500 }
    );
  }
}
