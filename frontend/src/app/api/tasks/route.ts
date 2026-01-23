import { NextResponse } from "next/server";
import { getTaskCounts } from "@/lib/vault";

export async function GET() {
  try {
    const counts = getTaskCounts();
    return NextResponse.json(counts);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get task counts", details: String(error) },
      { status: 500 }
    );
  }
}
