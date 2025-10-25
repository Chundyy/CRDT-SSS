import { redirect } from "next/navigation"
import { getCurrentUser } from "@/app/actions/auth"
import { DownloadContent } from "@/components/download-content"

export const dynamic = "force-dynamic"

export default async function DownloadPage() {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/login")
  }

  if (user.group_id === 1) {
    redirect("/dashboard")
  }

  return <DownloadContent user={user} />
}
