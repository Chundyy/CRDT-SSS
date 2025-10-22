import { NextResponse } from "next/server"

export async function GET() {
  const activities = [
    {
      id: "1",
      type: "success" as const,
      message: "Database backup completed successfully",
      timestamp: "2 minutes ago",
    },
    {
      id: "2",
      type: "warning" as const,
      message: "High memory usage detected on server-02",
      timestamp: "15 minutes ago",
    },
    {
      id: "3",
      type: "success" as const,
      message: "New user registration: john@example.com",
      timestamp: "1 hour ago",
    },
    {
      id: "4",
      type: "error" as const,
      message: "API rate limit exceeded for endpoint /api/data",
      timestamp: "2 hours ago",
    },
    {
      id: "5",
      type: "success" as const,
      message: "SSL certificate renewed successfully",
      timestamp: "3 hours ago",
    },
  ]

  return NextResponse.json(activities)
}
