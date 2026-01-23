import { NextResponse } from "next/server";
import { getSocialChannelsStatus } from "@/lib/vault";

export async function GET() {
  try {
    const data = getSocialChannelsStatus();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to get social channels status", details: String(error) },
      { status: 500 }
    );
  }
}
