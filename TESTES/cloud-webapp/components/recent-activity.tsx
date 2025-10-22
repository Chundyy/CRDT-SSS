"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react"

interface Activity {
  id: string
  type: "success" | "error" | "warning"
  message: string
  timestamp: string
}

export function RecentActivity() {
  const [activities, setActivities] = useState<Activity[]>([])

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await fetch("/api/activities")
        const data = await response.json()
        setActivities(data)
      } catch (error) {
        console.error("[v0] Error fetching activities:", error)
      }
    }

    fetchActivities()
  }, [])

  const getIcon = (type: Activity["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-accent" />
      case "error":
        return <XCircle className="h-4 w-4 text-destructive" />
      case "warning":
        return <AlertCircle className="h-4 w-4 text-chart-3" />
    }
  }

  const getBadgeVariant = (type: Activity["type"]) => {
    switch (type) {
      case "success":
        return "default"
      case "error":
        return "destructive"
      case "warning":
        return "secondary"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest events and system notifications</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-start gap-4 pb-4 border-b border-border last:border-0 last:pb-0"
            >
              <div className="mt-0.5">{getIcon(activity.type)}</div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium leading-relaxed">{activity.message}</p>
                <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
              </div>
              <Badge variant={getBadgeVariant(activity.type)} className="capitalize">
                {activity.type}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
