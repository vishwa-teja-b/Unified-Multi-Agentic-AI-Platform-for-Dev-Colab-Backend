# 🚀 Unified Multi-Agent AI Platform — Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=graph&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=for-the-badge&logo=socketdotio&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

**A modern, scalable backend for developer collaboration with AI-powered multi-agent capabilities.**

</div>

---

## ✨ Features

### 🔐 Authentication System
- **User Registration** — Secure signup with email validation & auto-profile stub
- **User Login** — JWT-based access & refresh tokens
- **Password Reset** — OTP via email with 30-minute expiry
- **Token Refresh** — Seamless session management with 21-day refresh tokens
- **Background Cleanup** — Auto-purges expired OTPs every 15 minutes

### 👤 Profile Management
- **Create Profile** — Multi-step profile wizard with skills, interests, languages & timezone
- **Get Profile** — Retrieve authenticated user's profile
- **Get Profile by Username** — View other users' public profiles
- **Update Profile** — Full profile updates with Pinecone re-indexing
- **Skill Indexing** — Profiles indexed in Pinecone for semantic search
- **Social URL Construction** — Auto-builds full GitHub/LinkedIn/Portfolio URLs from usernames
- **Profile Completeness Check** — Frontend redirects to profile creation if incomplete

### 📂 Project Management
- **Create Project** — Define project with skills, features, team size; atomically creates a team with owner as first member
- **Get My Projects** — List all user's projects
- **Get All Projects** — Browse projects from other users (Explore view)
- **Get Project by ID** — Retrieve single project details
- **Update Project** — Modify project fields
- **Delete Project** — Remove project & clean up Pinecone index
- **Semantic Search** — Find projects by natural language (e.g., "AI chat app") using Pinecone embeddings

### 🤖 AI Team Formation Agent
- **Role Analysis** — LLM identifies required team roles from project requirements
- **Skill Matching** — Semantic search finds candidates via Pinecone vectors
- **Candidate Evaluation** — LLM scores candidates with reasoning
- **LangGraph Workflow** — Multi-node agent orchestration with MongoDB checkpoints

### 🗓️ AI Project Planner Agent
- **Feature Extraction** — LLM analyzes project description to identify key features
- **Milestone Definition** — Breaks down features into logical sprints/milestones
- **Task Generation** — Creates detailed actionable tasks for each sprint
- **Sprint Date Computation** — Auto-calculates start/end dates for sprints based on project duration
- **Sprint Locking** — Sprints auto-lock when their end date passes; tasks in locked sprints are read-only
- **Current Sprint Detection** — Backend computes the current sprint number based on date ranges
- **Task Status Updates** — Update individual task statuses (To Do → In Progress → Done)
- **Manual Task Management** — Add, edit, and delete custom tasks within any sprint
- **Async Execution** — LangGraph workflow runs asynchronously to prevent timeouts
- **Structured Output** — Returns JSON-compliant roadmaps using `LLMParser`

### 📨 Invitations & Join Requests
- **Send Invitation** — Project owner invites recommended teammates
- **Get My Invitations** — Retrieve all invitations received by the user
- **Accept/Reject Invitation** — Accept adds user to team automatically
- **Request to Join** — Non-owner users can request to join a project with a role and optional message
- **Get Join Requests** — Project owner views all pending join requests
- **Respond to Join Request** — Owner accepts or rejects; on accept, the requester is added to the team
- **Background Cleanup** — Auto-deletes old invitations daily (older than 7 days)

### 👥 Team Management
- **Auto-creation** — Team is created atomically when a project is created (owner as first member)
- **Get My Teams** — List all teams the authenticated user belongs to
- **Get Team by ID** — Retrieve team details by team document ID
- **Get Team by Project ID** — Retrieve team details by associated project ID
- **Username Resolution** — Batch SQL lookup to enrich team member data with usernames
- **Member Management** — New members are added via invitation acceptance or join request approval

### 💻 Collaboration Rooms (Sessions)
- **Create/Get Room** — One room per project; requires a project plan to exist
- **List My Rooms** — Shows all rooms where user is owner or team member
- **Workspace Persistence** — Save & restore file structure and whiteboard state per room
- **Room-Project Linking** — Rooms are enriched with project titles for display

### ⚡ Real-time Collaboration (Socket.IO)
- **Room Join/Leave** — Users join rooms with username; presence is broadcast to all participants
- **Live User Tracking** — In-memory user store tracks connected users per room with online/offline status
- **File Sync** — Broadcast file structure changes (create, update, rename, delete) to all room members
- **Directory Sync** — Broadcast directory operations (create, update, rename, delete) across clients
- **Real-time Code Editing** — `file_updated` events sync code changes character-by-character
- **Team Chat** — `send_message` / `receive_message` events for in-room team messaging
- **Whiteboard** — `drawing_update` / `sync_drawing` / `request_drawing` events for shared tldraw canvas
- **Cursor Tracking** — `typing_start` / `typing_pause` events with live cursor position indicators

### 🖥️ Code Execution Engine
- **Multi-language Support** — Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, PHP, Ruby, Kotlin, Swift
- **Self-hosted Piston** — Sandboxed code execution via Docker container (local Piston API)
- **Compile & Run** — Separate compile and run stages with configurable timeouts
- **stdin Support** — Pass input to programs via standard input
- **Error Handling** — Graceful error messages for compilation errors, runtime errors, and service unavailability

### 🏗️ Architecture
- **Framework:** FastAPI with async/await support
- **Auth Database:** MySQL (Aiven Cloud) with SQLModel ORM
- **App Database:** MongoDB (Atlas) with PyMongo async
- **Vector Store:** Pinecone with HuggingFace embeddings
- **AI Agents:** LangGraph + OpenRouter (free LLMs)
- **Real-time:** Socket.IO (python-socketio) with in-memory room management
- **Code Execution:** Self-hosted Piston (Docker) with multi-language support
- **Security:** HS256 JWT tokens, bcrypt password hashing, OAuth2PasswordBearer
- **Email:** FastAPI-Mail with Gmail SMTP

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── config/
│   │   ├── jwt_config.py       # JWT token creation & verification
│   │   ├── security.py         # Password hashing (bcrypt)
│   │   ├── email_config.py     # SMTP configuration
│   │   └── external_services.py # Piston API URL & external service config
│   │
│   ├── db/
│   │   ├── mysql_connection.py # MySQL engine & session
│   │   ├── mongo.py            # MongoDB async client
│   │   └── init_db.py          # Table creation on startup
│   │
│   ├── dependencies/
│   │   ├── auth.py             # JWT auth dependency (shared)
│   │   └── collections.py      # MongoDB collection getters
│   │
│   ├── dto/
│   │   ├── profile_schema.py   # Profile request/response DTOs
│   │   ├── project_schema.py   # Project request/response DTOs
│   │   ├── invitation_schema.py # Invitation & JoinRequest DTOs
│   │   ├── team_schema.py      # TeamResponse & TeamMemberResponse DTOs
│   │   ├── team_formation_schema.py # AI agent request DTOs
│   │   └── project_planner_schema.py # Planner request/response DTOs
│   │
│   ├── models/
│   │   ├── User.py             # User model (MySQL)
│   │   ├── profiles.py         # Profile model (MongoDB)
│   │   ├── projects.py         # Project model (MongoDB)
│   │   ├── invitations.py      # Invitation model (MongoDB)
│   │   ├── teams.py            # Team & TeamMember models (MongoDB)
│   │   ├── password_reset_token.py  # OTP storage
│   │   ├── project_plan.py     # Project Plan model (MongoDB)
│   │   └── schemas.py          # Auth request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── profiles.py         # Profile CRUD endpoints
│   │   ├── projects.py         # Project CRUD endpoints
│   │   ├── agents.py           # AI Agent endpoints
│   │   ├── invitations.py      # Invitation & Join Request endpoints
│   │   ├── planned_projects.py # Planned Project endpoints
│   │   └── teams.py            # Team endpoints
│   │
│   ├── tasks/
│   │   └── background_tasks.py # Scheduled cleanup tasks
│   │
│   ├── agents/
│   │   ├── llm_config.py       # OpenRouter LLM configuration
│   │   ├── utils.py            # JSON extraction utilities
│   │   ├── llm_parser.py       # Safe LLM response parsing
│   │   └── team_formation/
│   │       ├── state.py        # LangGraph state definition
│   │       ├── team_formation_graph.py  # Graph builder
│   │       └── nodes/
│   │           ├── role_analyzer.py     # LLM role analysis
│   │           ├── skill_matcher.py     # Pinecone search
│   │           └── llm_evaluator.py     # Candidate scoring
│   │
│   │       └── project_planner/
│   │           ├── nodes/               # Planner logic nodes
│   │           ├── graph.py             # Planner graph definition
│   │           └── state.py             # Planner state schema
│   │
│   ├── sockets/
│   │   ├── events.py           # Socket.IO event registration
│   │   └── handlers.py         # Socket.IO event handlers (join, file sync, chat, whiteboard, cursor)
│   │
│   ├── utils/
│   │   ├── llm_parser.py       # Safe LLM response parsing
│   │   └── timezone_utils.py   # Sprint date computation & timezone support
│   │
│   ├── services/
│   │   └── mail_service.py     # Email sending & OTP generation
│   │
│   ├── vector_stores/
│   │   └── pinecone_db.py      # Pinecone vector store integration
│   │
│   └── main.py                 # FastAPI app & lifespan events
│
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | ❌ | Create new user account |
| `POST` | `/api/auth/login` | ❌ | Authenticate & get tokens |
| `POST` | `/api/auth/refresh-token` | ❌ | Refresh access token |
| `POST` | `/api/auth/forgot-password` | ❌ | Request OTP via email |
| `POST` | `/api/auth/reset-password` | ❌ | Reset password with OTP |

### Profiles (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/profiles/create-profile` | 🔒 | Create user profile |
| `GET` | `/api/profiles/profile` | 🔒 | Get authenticated user's profile |
| `PATCH` | `/api/profiles/profile-update` | 🔒 | Update profile fields |
| `GET` | `/api/profiles/test-auth` | 🔒 | Test authentication |

### Projects (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/projects/create-project` | 🔒 | Create project + team (atomic) |
| `GET` | `/api/projects/my-projects` | 🔒 | List user's projects |
| `GET` | `/api/projects/all-projects` | 🔒 | Browse other users' projects |
| `GET` | `/api/projects/project/{id}` | 🔒 | Get single project |
| `PATCH` | `/api/projects/project/{id}` | 🔒 | Update project |
| `DELETE` | `/api/projects/project/{id}` | 🔒 | Delete project |

### Invitations & Join Requests (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/projects/send-invitation` | 🔒 | Owner invites a teammate |
| `GET` | `/api/projects/get-my-invitations` | 🔒 | Get invitations received |
| `PATCH` | `/api/projects/update-invitation` | 🔒 | Accept/reject an invitation |
| `POST` | `/api/projects/request-to-join` | 🔒 | Request to join a project |
| `GET` | `/api/projects/get-join-requests` | 🔒 | Owner views pending requests |
| `POST` | `/api/projects/respond-join-request` | 🔒 | Owner accepts/rejects request |

### Teams (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/teams/my-teams` | 🔒 | List all teams the user belongs to |
| `GET` | `/api/teams/team/{team_id}` | 🔒 | Get team by team ID |
| `GET` | `/api/teams/project/{project_id}` | 🔒 | Get team by project ID |

### AI Agents (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/agents/team-formation` | 🔒 | Find & evaluate team candidates |
| `POST` | `/api/agents/project-planner` | 🔒 | Generate project roadmap & tasks |

### Planned Projects (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/planned-projects/project/{project_id}` | 🔒 | Get generated roadmap |
| `POST` | `/api/planned-projects/tasks` | 🔒 | Add a new manual task |
| `PUT` | `/api/planned-projects/tasks` | 🔒 | Update/Edit an existing task |
| `PATCH` | `/api/planned-projects/tasks` | 🔒 | Update task status |
| `DELETE` | `/api/planned-projects/tasks` | 🔒 | Delete a task |

### Sessions (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/rooms` | 🔒 | List active coding sessions for user |
| `POST` | `/api/rooms` | 🔒 | Create/Get a session for a project |
| `GET` | `/api/rooms/{project_id}` | 🔒 | Get room details by project ID |
| `GET` | `/api/rooms/{project_id}/workspace` | 🔒 | Get workspace state |
| `PUT` | `/api/rooms/{project_id}/workspace` | 🔒 | Save workspace state |

### Chat (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/chat/new-chat` | 🔒 | Create/Get a direct chat with a user |
| `POST` | `/api/chat/team-chat` | 🔒 | Create/Get a team chat for a project |
| `GET` | `/api/chat/get-chat-rooms` | 🔒 | List all chats the user is part of |
| `GET` | `/api/chat/search-dev` | 🔒 | Search for users by name/username |
| `GET` | `/api/chat/{room_id}/messages` | 🔒 | Get chat history for a room |
| `POST` | `/api/chat/{room_id}/messages` | 🔒 | Send a message to a room |
| `POST` | `/api/chat/{room_id}/mark-read` | 🔒 | Mark unread messages as read |

### Code Execution (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/execution` | 🔒 | Execute code via Piston (Docker) |

### ⚡ Real-time Collaboration (Socket.IO)
The backend uses `python-socketio` for real-time events.

| Event Category | Events | Description |
|----------------|--------|-------------|
| **Connection** | `join_request`, `user_joined`, `user_disconnected` | Room management & presence |
| **File System** | `sync_file_structure`, `file_created`, `file_updated`, `directory_created`, `directory_updated`, `directory_renamed`, `directory_deleted` | Sync files & folders across clients |
| **Chat** | `send_message`, `receive_message` | Team chat within coding rooms |
| **Whiteboard** | `drawing_update`, `sync_drawing` | Shared tldraw canvas state |
| **Cursor** | `cursor_move`, `typing_start` | Live cursor tracking & typing indicators |

### Example: Create Project (with atomic team creation)
```bash
curl -X POST http://localhost:8000/api/projects/create-project \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "title": "AI Study Planner",
    "category": "AI/ML",
    "description": "An intelligent study planner using AI for personalized schedules.",
    "features": ["Smart scheduling", "Progress tracking"],
    "required_skills": ["Python", "React", "TensorFlow"],
    "team_size": { "min": 2, "max": 4 },
    "complexity": "Medium",
    "estimated_duration": "2-3 months"
  }'
```

### Example: Request to Join a Project
```bash
curl -X POST http://localhost:8000/api/projects/request-to-join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "project_id": "<project_id>",
    "role": "Frontend Developer",
    "message": "I have 2 years of React experience!"
  }'
```

### Example: Generate Roadmap
```bash
curl -X POST http://localhost:8000/api/agents/project-planner \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "project_id": "<project_id>"
  }'
```

---

## 🛠️ Quick Start

### 1. Clone & Setup
```bash
cd backend
python -m venv virtual_env
virtual_env\Scripts\activate  # Windows
# source virtual_env/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file:
```env
# MySQL (Authentication)
MYSQL_DB_URL="mysql+pymysql://user:pass@host:port/dbname"

# MongoDB (Profiles & App Data)
MONGODB_URL="mongodb+srv://user:pass@cluster.mongodb.net/"
MONGODB_DB_NAME="devcollab"

# JWT Configuration
JWT_SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=21

# Email (SMTP)
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="your-app-password"
MAIL_FROM="your-email@gmail.com"
MAIL_PORT=587
MAIL_SERVER="smtp.gmail.com"

# Code Execution (Piston)
PISTON_API_URL="http://localhost:2000/api/v2"
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

### 5. Access API Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔒 Security Features

| Feature | Implementation |
|---------|---------------|
| Password Storage | bcrypt with salt (12 rounds) |
| Access Tokens | JWT HS256, 7-day expiry |
| Refresh Tokens | JWT HS256, 21-day expiry |
| OTP Codes | 6-digit, 30-minute expiry |
| SSL/TLS | Required for database connection |

---

## 🧹 Background Workers

The application includes background workers that automatically clean up:
- ✅ Used & expired OTP tokens — **every 15 minutes**
- ✅ Old invitations (> 7 days) — **daily**

Managed via `asyncio.create_task()` in the FastAPI lifespan.

---

## 📊 Database Schema

### MySQL: User Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| email | VARCHAR(255) | Unique, indexed |
| username | VARCHAR(255) | Unique, indexed |
| hashed_password | VARCHAR(255) | bcrypt hash |
| is_active | BOOLEAN | Account status |
| is_verified | BOOLEAN | Email verified |
| profile_complete | BOOLEAN | Profile wizard done |
| created_at | DATETIME | Registration timestamp |

### MySQL: PasswordResetToken Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK → user.id (CASCADE) |
| otp | VARCHAR(255) | 6-digit code |
| expires_at | DATETIME | Validity deadline |
| is_used | BOOLEAN | One-time use flag |

### MongoDB: Profiles Collection
```json
{
  "_id": "ObjectId",
  "auth_user_id": 1,
  "name": "Ravi Kumar",
  "username": "ravikumar",
  "email": "ravi@example.com",
  "bio": "Full-stack developer",
  "primary_skills": ["React", "Python", "FastAPI"],
  "secondary_skills": ["Docker", "AWS"],
  "experience_level": "intermediate",
  "interests": ["AI/ML", "Web Dev"],
  "timezone": "IST",
  "github": "https://github.com/ravikumar",
  "created_at": "2026-02-03T10:00:00Z"
}
```

### MongoDB: Projects Collection
```json
{
  "_id": "ObjectId",
  "auth_user_id": 1,
  "title": "Mental Health Mood Tracker",
  "category": "Mobile",
  "description": "An app for daily mood logging...",
  "features": ["Mood logging", "Journaling", "Analytics"],
  "required_skills": ["React Native", "Node.js", "MongoDB"],
  "team_size": { "min": 2, "max": 4 },
  "complexity": "Medium",
  "estimated_duration": "2-3 months",
  "status": "Open",
  "team_id": "683456abc...",
  "created_at": "2026-02-03T13:50:33Z",
  "updated_at": null
}
```

### MongoDB: Teams Collection ✨ NEW
```json
{
  "_id": "ObjectId",
  "project_id": "682abc...",
  "project_title": "Mental Health Mood Tracker",
  "project_owner": 1,
  "team_members": [
    { "user_id": 1, "role": "Owner", "joined_at": "2026-02-03T13:50:33Z" },
    { "user_id": 4, "role": "Frontend Developer", "joined_at": "2026-02-04T09:20:00Z" }
  ],
  "created_at": "2026-02-03T13:50:33Z"
}
```

### MongoDB: Invitations Collection ✨ NEW
```json
{
  "_id": "ObjectId",
  "project_id": "682abc...",
  "project_title": "Mental Health Mood Tracker",
  "sender_id": 1,
  "receiver_id": 4,
  "role": "Frontend Developer",
  "message": "I'd love to contribute!",
  "type": "JOIN_REQUEST",
  "status": "PENDING",
  "created_at": "2026-02-04T08:00:00Z",
  "updated_at": null
}
```

---

### MongoDB: Project Plans Collection ✨ NEW
```json
{
  "_id": "ObjectId",
  "project_id": "682abc...",
  "roadmap": [
    {
      "sprint": "Sprint 1",
      "tasks": [
        { "id": "T1", "title": "Setup Repo", "status": "To Do" }
      ]
    }
  ],
  "extracted_features": ["Login", "Dashboard"],
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z"
}
```

---

### MongoDB: Chats Collection ✨ NEW
```json
{
  "_id": "ObjectId",
  "room_type": "team", // or "direct"
  "participants": [1, 4, 5],
  "team_id": "682abc...", // only for team rooms
  "last_message": {
    "_id": "ObjectId",
    "room_id": "ObjectId",
    "sender_id": 4,
    "text": "Hello everyone!",
    "timestamp": "2026-02-06T15:30:00Z",
    "is_read": false
  },
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-06T15:30:00Z"
}
```

### MongoDB: Messages Collection ✨ NEW
```json
{
  "_id": "ObjectId",
  "room_id": "ObjectId",
  "sender_id": 4,
  "text": "Hello everyone!",
  "timestamp": "2026-02-06T15:30:00Z",
  "is_read": false
}
```

---

## 🚧 Roadmap

- [x] Phase 1: Authentication system ✅
- [x] Phase 2: User profiles + Pinecone skill indexing ✅
- [x] Phase 3: Projects CRUD ✅
- [x] Phase 4: AI Agent — Team Formation (LangGraph) ✅
- [x] Phase 5: Invitations, Join Requests & Teams ✅
- [x] Phase 6: AI Agent — Project Planner ✅
- [x] Phase 7: Real-time collaboration (Sessions & Sockets) ✅
- [x] Phase 8: Code editor integration (Execution Engine) ✅
- [x] Phase 9: Whiteboard (tldraw) - Backend Ready ✅
- [x] Phase 10: Manual Task Management & UI Refinement ✅ NEW

---

## 📝 License

MIT © 2026

---

<div align="center">

**Built with ❤️ using FastAPI**

</div>
