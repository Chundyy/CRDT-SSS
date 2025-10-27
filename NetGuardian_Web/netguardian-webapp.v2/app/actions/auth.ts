"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import bcrypt from "bcryptjs"
import { getSql } from "@/lib/db"

export async function loginAction(email: string, password: string) {
  try {
    const sql = getSql()

    const result = await sql`
      SELECT id, name, group_id, email, password 
      FROM users 
      WHERE email = ${email}
    `

    if (result.length === 0) {
      return { success: false, error: "Invalid email or password" }
    }

    const user = result[0]

    const passwordMatch = await bcrypt.compare(password, user.password)

    if (!passwordMatch) {
      return { success: false, error: "Invalid email or password" }
    }

    // Set cookie with user ID
    const cookieStore = await cookies()
    cookieStore.set("userId", user.id.toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
    })

    if (user.group_id === 1) {
      redirect("/dashboard")
    } else {
      redirect("/download")
    }
  } catch (error: any) {
    if (error?.digest?.includes("NEXT_REDIRECT")) {
      throw error
    }
    console.error("Login error:", error)
    return { success: false, error: "Database connection error" }
  }
}

export async function logoutAction() {
  const cookieStore = await cookies()
  cookieStore.delete("userId")
  return { success: true }
}

export async function getCurrentUser() {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return null
    }

    const sql = getSql()
    const result = await sql`
      SELECT id, name, group_id, email 
      FROM users 
      WHERE id = ${userId}
    `

    if (result.length === 0) {
      return null
    }

    return result[0]
  } catch (error) {
    console.error("Get user error:", error)
    return null
  }
}
