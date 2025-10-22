"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Database, Users, TrendingUp } from "lucide-react"

interface Stats {
  totalRequests: number
  activeUsers: number
  storageUsed: number
  uptime: number
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("/api/stats")
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error("[v0] Error fetching stats:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 w-24 bg-muted rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-32 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: "Total Requests",
      value: stats?.totalRequests.toLocaleString() || "0",
      icon: Activity,
      change: "+12.5%",
    },
    {
      title: "Active Users",
      value: stats?.activeUsers.toLocaleString() || "0",
      icon: Users,
      change: "+8.2%",
    },
    {
      title: "Storage Used",
      value: `${stats?.storageUsed || 0} GB`,
      icon: Database,
      change: "+4.1%",
    },
    {
      title: "Uptime",
      value: `${stats?.uptime || 0}%`,
      icon: TrendingUp,
      change: "+0.3%",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-accent mt-1">{card.change} from last month</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
