"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Building2, MapPin, Mail, Phone, Save } from "lucide-react"

export function SettingsPage() {
  const [settings, setSettings] = useState({
    companyName: "CloudApp Inc.",
    companyLocation: "San Francisco, CA",
    companyEmail: "contact@cloudapp.com",
    companyPhone: "+1 (555) 123-4567",
    storageLimit: "500",
    maxUsers: "100",
  })

  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    try {
      const response = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      })

      if (response.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      }
    } catch (error) {
      console.error("Failed to save settings:", error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-zinc-400 text-sm">Manage your application settings and preferences</p>
      </div>

      <div className="grid gap-6 max-w-4xl">
        {/* Company Information */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Company Information
            </CardTitle>
            <CardDescription className="text-zinc-400">
              Update your company details and contact information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="companyName" className="text-zinc-300">
                  Company Name
                </Label>
                <Input
                  id="companyName"
                  value={settings.companyName}
                  onChange={(e) => setSettings({ ...settings, companyName: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="companyLocation" className="text-zinc-300 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Location
                </Label>
                <Input
                  id="companyLocation"
                  value={settings.companyLocation}
                  onChange={(e) => setSettings({ ...settings, companyLocation: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="companyEmail" className="text-zinc-300 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </Label>
                <Input
                  id="companyEmail"
                  type="email"
                  value={settings.companyEmail}
                  onChange={(e) => setSettings({ ...settings, companyEmail: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="companyPhone" className="text-zinc-300 flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  Phone
                </Label>
                <Input
                  id="companyPhone"
                  value={settings.companyPhone}
                  onChange={(e) => setSettings({ ...settings, companyPhone: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Limits */}
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">System Limits</CardTitle>
            <CardDescription className="text-zinc-400">
              Configure storage and user limits for your application
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="storageLimit" className="text-zinc-300">
                  Storage Limit (GB)
                </Label>
                <Input
                  id="storageLimit"
                  type="number"
                  value={settings.storageLimit}
                  onChange={(e) => setSettings({ ...settings, storageLimit: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="maxUsers" className="text-zinc-300">
                  Maximum Users
                </Label>
                <Input
                  id="maxUsers"
                  type="number"
                  value={settings.maxUsers}
                  onChange={(e) => setSettings({ ...settings, maxUsers: e.target.value })}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex items-center gap-4">
          <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
          {saved && <span className="text-emerald-500 text-sm">Settings saved successfully!</span>}
        </div>
      </div>
    </div>
  )
}
