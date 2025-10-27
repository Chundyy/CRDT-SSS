import { type NextRequest, NextResponse } from "next/server"
import { getSql } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function GET() {
  try {
    const sql = getSql()
    const result = await sql`
      SELECT u.id, u.name, u.email, u.group_id, g.name as group_name
      FROM users u
      LEFT JOIN groups g ON u.group_id = g.id
      ORDER BY u.id ASC
    `

    return NextResponse.json(result)
  } catch (error) {
    console.error("Database error:", error)
    return NextResponse.json({ error: "Failed to fetch users" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const { name, email, password, group_id } = await request.json()

    const sql = getSql()
    const existingUser = await sql`
      SELECT id FROM users WHERE email = ${email}
    `

    if (existingUser.length > 0) {
      return NextResponse.json({ error: "User with this email already exists" }, { status: 409 })
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10)

    const result = await sql`
      INSERT INTO users (name, email, password, group_id) 
      VALUES (${name}, ${email}, ${hashedPassword}, ${group_id}) 
      RETURNING id, name, email, group_id
    `

    return NextResponse.json(result[0])
  } catch (error) {
    console.error("Database error:", error)
    return NextResponse.json({ error: "Failed to create user" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get("id")

    if (!id) {
      return NextResponse.json({ error: "User ID required" }, { status: 400 })
    }

    const sql = getSql()
    await sql`DELETE FROM users WHERE id = ${id}`

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Database error:", error)
    return NextResponse.json({ error: "Failed to delete user" }, { status: 500 })
  }
}
