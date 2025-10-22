"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface Metrics {
  cpu: number
  memory: number
  bandwidth: number
}

export function UsageMetrics() {
  const [metrics, setMetrics] = useState<Metrics>({ cpu: 0, memory: 0, bandwidth: 0 })

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch("/api/metrics")
        const data = await response.json()
        setMetrics(data)
      } catch (error) {
        console.error("[v0] Error fetching metrics:", error)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  const metricsList = [
    { label: "CPU Usage", value: metrics.cpu, color: "bg-primary" },
    { label: "Memory Usage", value: metrics.memory, color: "bg-accent" },
    { label: "Bandwidth", value: metrics.bandwidth, color: "bg-chart-3" },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resource Usage</CardTitle>
        <CardDescription>Current system resource utilization</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {metricsList.map((metric) => (
          <div key={metric.label} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{metric.label}</span>
              <span className="text-muted-foreground">{metric.value}%</span>
            </div>
            <Progress value={metric.value} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
