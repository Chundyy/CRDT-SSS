"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Shield, LayoutDashboard, Users, Settings, LogOut, HardDrive } from "lucide-react"
import { logoutAction } from "@/app/actions/auth"
import { DashboardHome } from "@/components/dashboard-home"
import { UsersPage } from "@/components/users-page"
import { StoragePage } from "@/components/storage-page"
import { SettingsPage } from "@/components/settings-page"

interface DashboardContentProps {
  user: {
    id: number
    name: string
    email: string
    group_id: number
  }
}

export function DashboardContent({ user }: DashboardContentProps) {
  const [activeNav, setActiveNav] = useState("dashboard")
  const router = useRouter()

  const handleLogout = async () => {
    await logoutAction()
    router.push("/login")
    router.refresh()
  }

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Sidebar */}
      <aside className="w-60 bg-zinc-950 border-r border-zinc-800 flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold">NetGuardian</span>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          <button
            onClick={() => setActiveNav("dashboard")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              activeNav === "dashboard" ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            }`}
          >
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActiveNav("storage")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              activeNav === "storage" ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            }`}
          >
            <HardDrive className="w-5 h-5" />
            <span>Storage</span>
          </button>

          <button
            onClick={() => setActiveNav("users")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              activeNav === "users" ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            }`}
          >
            <Users className="w-5 h-5" />
            <span>Users</span>
          </button>

          <button
            onClick={() => setActiveNav("settings")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              activeNav === "settings" ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            }`}
          >
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
        </nav>

        <div className="p-3 border-t border-zinc-800">
          <Button
            onClick={handleLogout}
            variant="ghost"
            className="w-full justify-start text-zinc-400 hover:text-white hover:bg-zinc-900"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        {activeNav === "dashboard" && <DashboardHome user={user} />}
        {activeNav === "storage" && <StoragePage />}
        {activeNav === "users" && <UsersPage />}
        {activeNav === "settings" && <SettingsPage />}
      </main>
    </div>
  )
}
