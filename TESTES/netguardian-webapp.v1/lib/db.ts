import postgres from "postgres"

import "server-only"

let sql: ReturnType<typeof postgres> | null = null

function getSql() {
  if (!sql) {
    sql = postgres(process.env.DATABASE_URL || "", {
      max: 10,
      idle_timeout: 20,
      connect_timeout: 10,
    })
  }
  return sql
}

export async function query(text: string, params?: any[]) {
  const sql = getSql()

  // Convert $1, $2 style placeholders to postgres.js style
  let queryText = text
  if (params && params.length > 0) {
    params.forEach((_, index) => {
      queryText = queryText.replace(`$${index + 1}`, `$${index + 1}`)
    })
  }

  const result = await sql.unsafe(queryText, params || [])

  // Return in pg-compatible format
  return { rows: result }
}

export { getSql }
