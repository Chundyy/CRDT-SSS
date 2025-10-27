"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { File, Folder, HardDrive, Download } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileInfo {
  name: string
  size: number
  type: "file" | "directory"
  modified: string
}

interface StorageStats {
  totalSize: number
  fileCount: number
  folderCount: number
  availableSpace: number
}

export function StoragePage() {
  const [files, setFiles] = useState<FileInfo[]>([])
  const [stats, setStats] = useState<StorageStats>({
    totalSize: 0,
    fileCount: 0,
    folderCount: 0,
    availableSpace: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStorageData()
  }, [])

  const fetchStorageData = async () => {
    try {
      const response = await fetch("/api/storage")
      const data = await response.json()
      setFiles(data.files || [])
      setStats(data.stats || stats)
    } catch (error) {
      console.error("Failed to fetch storage data:", error)
    } finally {
      setLoading(false)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Storage</h1>
        <p className="text-zinc-400 text-sm">Manage your cloud storage files and folders</p>
      </div>

      {/* Storage Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Total Size</CardTitle>
            <HardDrive className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{formatBytes(stats.totalSize)}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Files</CardTitle>
            <File className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.fileCount}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Folders</CardTitle>
            <Folder className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.folderCount}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Available</CardTitle>
            <HardDrive className="w-4 h-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{formatBytes(stats.availableSpace)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Files Table */}
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white">Files & Folders</CardTitle>
          <CardDescription className="text-zinc-400">Browse and manage your storage contents</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-zinc-400">Loading storage data...</div>
          ) : files.length === 0 ? (
            <div className="text-center py-8 text-zinc-400">No files found</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                  <TableHead className="text-zinc-400">Name</TableHead>
                  <TableHead className="text-zinc-400">Type</TableHead>
                  <TableHead className="text-zinc-400">Size</TableHead>
                  <TableHead className="text-zinc-400">Modified</TableHead>
                  <TableHead className="text-zinc-400 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {files.map((file, index) => (
                  <TableRow key={index} className="border-zinc-800 hover:bg-zinc-800/50">
                    <TableCell className="text-white">
                      <div className="flex items-center gap-2">
                        {file.type === "directory" ? (
                          <Folder className="w-4 h-4 text-blue-500" />
                        ) : (
                          <File className="w-4 h-4 text-zinc-400" />
                        )}
                        {file.name}
                      </div>
                    </TableCell>
                    <TableCell className="text-zinc-400 capitalize">{file.type}</TableCell>
                    <TableCell className="text-zinc-400">
                      {file.type === "file" ? formatBytes(file.size) : "-"}
                    </TableCell>
                    <TableCell className="text-zinc-400">{formatDate(file.modified)}</TableCell>
                    <TableCell className="text-right">
                      {file.type === "file" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-blue-500 hover:text-blue-400 hover:bg-blue-950/50"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
