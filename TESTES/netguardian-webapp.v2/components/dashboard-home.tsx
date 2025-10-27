"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, Activity, Database, TrendingUp } from "lucide-react"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const activityData = [
  { time: "00:00", requests: 450 },
  { time: "03:00", requests: 380 },
  { time: "06:00", requests: 520 },
  { time: "09:00", requests: 780 },
  { time: "12:00", requests: 920 },
  { time: "15:00", requests: 918 },
  { time: "18:00", requests: 850 },
  { time: "21:00", requests: 680 },
]

interface DashboardHomeProps {
  user: {
    id: number
    name: string
    email: string
    group_id: number
  }
}

export function DashboardHome({ user }: DashboardHomeProps) {
  const [stats, setStats] = useState({
    totalRequests: 0,
    activeUsers: 0,
    storageUsed: "0 GB",
    uptime: "0%",
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("/api/dashboard/stats")
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error("Failed to fetch stats:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <div className="text-sm text-zinc-400">{user.email}</div>
        </div>
        <p className="text-zinc-400 text-sm">Monitor your cloud infrastructure and application performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Total Requests</CardTitle>
            <Activity className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold text-zinc-600">Loading...</div>
            ) : (
              <>
                <div className="text-3xl font-bold text-white">{stats.totalRequests.toLocaleString()}</div>
                <p className="text-xs text-emerald-500 mt-1">+12.5% from last month</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Active Users</CardTitle>
            <Users className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold text-zinc-600">Loading...</div>
            ) : (
              <>
                <div className="text-3xl font-bold text-white">{stats.activeUsers}</div>
                <p className="text-xs text-emerald-500 mt-1">+8.2% from last month</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Storage Used</CardTitle>
            <Database className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold text-zinc-600">Loading...</div>
            ) : (
              <>
                <div className="text-3xl font-bold text-white">{stats.storageUsed}</div>
                <p className="text-xs text-emerald-500 mt-1">+4.1% from last month</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Uptime</CardTitle>
            <TrendingUp className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold text-zinc-600">Loading...</div>
            ) : (
              <>
                <div className="text-3xl font-bold text-white">{stats.uptime}</div>
                <p className="text-xs text-emerald-500 mt-1">+0.3% from last month</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Overview */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">Activity Overview</CardTitle>
            <CardDescription className="text-zinc-400">
              Request volume and error rate over the last 24 hours
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                requests: {
                  label: "Requests",
                  color: "hsl(217, 91%, 60%)",
                },
              }}
              className="h-[300px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="time" stroke="#71717a" />
                  <YAxis stroke="#71717a" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Resource Usage */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">Resource Usage</CardTitle>
            <CardDescription className="text-zinc-400">Current system resource utilization</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">CPU Usage</span>
                <span className="text-white font-medium">63%</span>
              </div>
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full" style={{ width: "63%" }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Memory Usage</span>
                <span className="text-white font-medium">77%</span>
              </div>
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full" style={{ width: "77%" }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Bandwidth</span>
                <span className="text-white font-medium">44%</span>
              </div>
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full" style={{ width: "44%" }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
