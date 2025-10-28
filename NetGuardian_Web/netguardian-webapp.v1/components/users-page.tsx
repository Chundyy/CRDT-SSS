"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Trash2, Shield, UserIcon } from "lucide-react"

interface User {
  id: number
  name: string
  email: string
  group_id: number
  group_name?: string
}

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [error, setError] = useState("")
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    password: "",
    group_id: "",
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/users")
      const data = await response.json()
      setUsers(data)
    } catch (error) {
      console.error("Failed to fetch users:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async () => {
    setError("")

    if (!newUser.name || !newUser.email || !newUser.password) {
      setError("All fields are required")
      return
    }

    try {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 409) {
          setError("A user with this email already exists")
        } else {
          setError(data.error || "Failed to create user")
        }
        return
      }

      setIsAddDialogOpen(false)
      setNewUser({ name: "", email: "", password: "", group_id: "" })
      setError("")
      fetchUsers()
    } catch (error) {
      console.error("Failed to add user:", error)
      setError("Network error. Please try again.")
    }
  }

  const handleDeleteUser = async (id: number) => {
    if (!confirm("Are you sure you want to delete this user?")) return

    try {
      const response = await fetch(`/api/users?id=${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        fetchUsers()
      }
    } catch (error) {
      console.error("Failed to delete user:", error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Users</h1>
            <p className="text-zinc-400 text-sm">Manage user accounts and permissions</p>
          </div>
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Add User
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800 text-white">
              <DialogHeader>
                <DialogTitle>Add New User</DialogTitle>
                <DialogDescription className="text-zinc-400">
                  Create a new user account with email and password
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={newUser.name}
                    onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="group">User Group</Label>
                  <select
                    id="group"
                    value={newUser.group_id}
                    onChange={(e) => setNewUser({ ...newUser, group_id: Number.parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white"
                  >
                    <option value={1}>Admin</option>
                    <option value={2}>Porto</option>
                    <option value={3}>Lisboa</option>
                  </select>
                </div>
                {error && (
                  <div className="bg-red-950/50 border border-red-900 text-red-400 px-4 py-3 rounded-lg text-sm">
                    {error}
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsAddDialogOpen(false)
                    setError("")
                  }}
                  className="border-zinc-700"
                >
                  Cancel
                </Button>
                <Button onClick={handleAddUser} className="bg-blue-600 hover:bg-blue-700">
                  Add User
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white">All Users</CardTitle>
          <CardDescription className="text-zinc-400">Total users: {users.length}</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-zinc-400">Loading users...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                  <TableHead className="text-zinc-400">ID</TableHead>
                  <TableHead className="text-zinc-400">Name</TableHead>
                  <TableHead className="text-zinc-400">Email</TableHead>
                  <TableHead className="text-zinc-400">Group</TableHead>
                  <TableHead className="text-zinc-400 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} className="border-zinc-800 hover:bg-zinc-800/50">
                    <TableCell className="text-white font-medium">{user.id}</TableCell>
                    <TableCell className="text-white">{user.name}</TableCell>
                    <TableCell className="text-zinc-400">{user.email}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {user.group_id === 1 ? (
                          <>
                            <Shield className="w-4 h-4 text-blue-500" />
                            <span className="text-blue-500 font-medium">Admin</span>
                          </>
                        ) : user.group_id === 2 ? (
                          <>
                            <UserIcon className="w-4 h-4 text-zinc-400" />
                            <span className="text-zinc-400">Porto</span>
                          </>
                        ) : user.group_id === 3 ? (
                          <>
                            <UserIcon className="w-4 h-4 text-zinc-400" />
                            <span className="text-zinc-400">Lisboa</span>
                          </>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-500 hover:text-red-400 hover:bg-red-950/50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
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
