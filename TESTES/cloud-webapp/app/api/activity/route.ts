import { NextResponse } from "next/server"

export async function GET() {
  // Generate sample chart data for the last 24 hours
  const data = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    requests: Math.floor(Math.random() * 1000) + 500,
    errors: Math.floor(Math.random() * 50),
  }))

  return NextResponse.json(data)
}
