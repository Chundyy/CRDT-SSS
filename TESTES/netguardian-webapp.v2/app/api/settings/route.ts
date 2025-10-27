import { type NextRequest, NextResponse } from "next/server"
import { promises as fs } from "fs"
import path from "path"

const SETTINGS_FILE = path.join(process.cwd(), "settings.json")

export async function GET() {
  try {
    const data = await fs.readFile(SETTINGS_FILE, "utf-8")
    return NextResponse.json(JSON.parse(data))
  } catch (error) {
    // Return default settings if file doesn't exist
    return NextResponse.json({
      companyName: "CloudApp Inc.",
      companyLocation: "San Francisco, CA",
      companyEmail: "contact@cloudapp.com",
      companyPhone: "+1 (555) 123-4567",
      storageLimit: "500",
      maxUsers: "100",
    })
  }
}

export async function POST(request: NextRequest) {
  try {
    const settings = await request.json()
    await fs.writeFile(SETTINGS_FILE, JSON.stringify(settings, null, 2))
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Settings error:", error)
    return NextResponse.json({ error: "Failed to save settings" }, { status: 500 })
  }
}
