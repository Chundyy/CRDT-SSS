import { NextResponse } from "next/server"
import { promises as fs } from "fs"
import path from "path"

// Configure your storage folder path here
const STORAGE_PATH = process.env.STORAGE_PATH || path.join(process.cwd(), "storage")

export async function GET() {
  try {
    // Ensure storage directory exists
    try {
      await fs.access(STORAGE_PATH)
    } catch {
      await fs.mkdir(STORAGE_PATH, { recursive: true })
    }

    const files = await fs.readdir(STORAGE_PATH)
    const fileInfos = await Promise.all(
      files.map(async (file) => {
        const filePath = path.join(STORAGE_PATH, file)
        const stats = await fs.stat(filePath)
        return {
          name: file,
          size: stats.size,
          type: stats.isDirectory() ? "directory" : "file",
          modified: stats.mtime.toISOString(),
        }
      }),
    )

    // Calculate storage stats
    const totalSize = fileInfos.reduce((acc, file) => acc + (file.type === "file" ? file.size : 0), 0)
    const fileCount = fileInfos.filter((f) => f.type === "file").length
    const folderCount = fileInfos.filter((f) => f.type === "directory").length

    // Get available space (this is a simplified example)
    const availableSpace = 500 * 1024 * 1024 * 1024 - totalSize // 500GB - used

    return NextResponse.json({
      files: fileInfos,
      stats: {
        totalSize,
        fileCount,
        folderCount,
        availableSpace,
      },
    })
  } catch (error) {
    console.error("Storage error:", error)
    return NextResponse.json({ error: "Failed to read storage" }, { status: 500 })
  }
}
