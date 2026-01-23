import { NextResponse } from "next/server";
import { getSystemStatus } from "@/lib/vault";

export async function GET() {
  try {
    const status = getSystemStatus();
    return NextResponse.json(status);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get system status", details: String(error) },
      { status: 500 }
    );
  }
}
