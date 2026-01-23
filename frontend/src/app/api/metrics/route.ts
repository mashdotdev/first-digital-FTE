import { NextResponse } from "next/server";
import { getDailyMetrics } from "@/lib/vault";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get("days") || "7", 10);

    const metrics = getDailyMetrics(Math.min(days, 30));
    return NextResponse.json(metrics);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get metrics", details: String(error) },
      { status: 500 }
    );
  }
}
