"use client"

import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Cloud, Download, LogOut } from "lucide-react"
import { logoutAction } from "@/app/actions/auth"

interface DownloadContentProps {
  user: {
    id: number
    name: string
    email: string
    group_id: number
  }
}

export function DownloadContent({ user }: DownloadContentProps) {
  const router = useRouter()

  const handleLogout = async () => {
    await logoutAction()
    router.push("/login")
    router.refresh()
  }

  // Client-side download handler — builds the URL at runtime so static analyzers don't try to resolve the file at build time.
  const handleDownload = (e: any) => {
    e.preventDefault()
    if (typeof window === "undefined") return
    const url = "netguardian_app.exe" // public/aa.txt — replace with your installer name when ready
    const a = document.createElement("a")
    a.href = url
    a.download = "netguardian_app.exe"
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-800 p-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold">NetGuardian</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-zinc-400">{user.email}</span>
            <Button onClick={handleLogout} variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <Card className="w-full max-w-2xl bg-zinc-900 border-zinc-800">
          <CardHeader className="text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-blue-600/10 flex items-center justify-center mx-auto">
              <Download className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-3xl font-bold text-white mb-2">Welcome, {user.name}!</CardTitle>
              <CardDescription className="text-zinc-400 text-lg">
                Download our cloud storage application to get started
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-zinc-800 rounded-lg p-6 space-y-4">
              <h3 className="text-lg font-semibold text-white">NetGuardian Desktop Client</h3>
              <p className="text-zinc-400 text-sm">
                Access your files from anywhere with our desktop application. Sync your data seamlessly across all your
                devices.
              </p>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                  Automatic file synchronization
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                  End-to-end encryption
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                  Offline access to your files
                </li>
              </ul>
            </div>

            <div className="grid-cols-1 md:grid-cols-3 gap-4">
              <button
                type="button"
                onClick={handleDownload}
                aria-label="Download for Windows"
                className="w-full inline-flex items-center justify-center py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded"
              >
                <Download className="w-4 h-4 mr-2" />
                Windows
              </button>
            </div>

            <div className="text-center text-sm text-zinc-500">Version 2.4.1 • Released October 2025</div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
