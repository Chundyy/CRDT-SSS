import { NextResponse } from "next/server"

export async function GET() {
  // Simulate real-time metrics
  const metrics = {
    cpu: Math.floor(Math.random() * 40) + 30,
    memory: Math.floor(Math.random() * 30) + 50,
    bandwidth: Math.floor(Math.random() * 50) + 20,
  }

  return NextResponse.json(metrics)
}
