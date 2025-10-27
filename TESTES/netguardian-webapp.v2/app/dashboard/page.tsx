import { redirect } from "next/navigation"
import { getCurrentUser } from "@/app/actions/auth"
import { DashboardContent } from "@/components/dashboard-content"

export const dynamic = "force-dynamic"

export default async function DashboardPage() {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/login")
  }

  if (user.group_id !== 1) {
    redirect("/download")
  }

  return <DashboardContent user={user} />
}
