# Cloud Storage Dashboard

A Next.js cloud storage dashboard with PostgreSQL authentication.

## Setup Instructions

### 1. Environment Variables

Create a `.env.local` file in the root directory with your PostgreSQL connection:

\`\`\`env
DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
\`\`\`

Replace the values with your actual PostgreSQL credentials:
- `username`: Your PostgreSQL username
- `password`: Your PostgreSQL password
- `localhost:5432`: Your PostgreSQL host and port
- `your_database_name`: Your database name

### 2. Install Dependencies

\`\`\`bash
npm install
\`\`\`

### 3. Run Development Server

\`\`\`bash
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) to see the application.

## Database Schema

The application expects the following tables (already created):

### USERS Table
- `id` - User ID (primary key)
- `name` - User name
- `group_id` - Group ID (1 = admin, other = regular user)
- `email` - User email
- `password` - User password

### GROUPS Table
- `id` - Group ID (primary key)
- `name` - Group name

## User Roles

- **Admin (group_id = 1)**: Redirected to the dashboard with full analytics
- **Regular Users (group_id ≠ 1)**: Redirected to the download page

## Features

- ✅ PostgreSQL authentication
- ✅ Role-based routing (admin vs regular users)
- ✅ Dark-themed UI matching your design
- ✅ Admin dashboard with stats and charts
- ✅ Download page for regular users
- ✅ Secure session management with HTTP-only cookies
