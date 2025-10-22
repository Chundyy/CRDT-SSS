import { DashboardLayout } from "@/components/dashboard-layout"
import { StatsCards } from "@/components/stats-cards"
import { ActivityChart } from "@/components/activity-chart"
import { RecentActivity } from "@/components/recent-activity"
import { UsageMetrics } from "@/components/usage-metrics"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">Monitor your cloud infrastructure and application performance</p>
        </div>

        <StatsCards />

        <div className="grid gap-6 lg:grid-cols-7">
          <div className="lg:col-span-4">
            <ActivityChart />
          </div>
          <div className="lg:col-span-3">
            <UsageMetrics />
          </div>
        </div>

        <RecentActivity />
      </div>
    </DashboardLayout>
  )
}
