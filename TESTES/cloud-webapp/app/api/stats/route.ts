import { NextResponse } from "next/server"

export async function GET() {
  // Simulate API call - replace with real data source
  const stats = {
    totalRequests: Math.floor(Math.random() * 100000) + 50000,
    activeUsers: Math.floor(Math.random() * 1000) + 500,
    storageUsed: Math.floor(Math.random() * 100) + 50,
    uptime: 99.9,
  }

  return NextResponse.json(stats)
}
