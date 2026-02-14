# 🚀 Unified Multi-Agent AI Platform — Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=graph&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

**A modern, scalable backend for developer collaboration with AI-powered multi-agent capabilities.**

</div>

---

## ✨ Features

### 🔐 Authentication System (Phase 1)
- **User Registration** — Secure signup with email validation
- **User Login** — JWT-based access & refresh tokens
- **Password Reset** — OTP via email with expiry
- **Token Refresh** — Seamless session management
- **Background Cleanup** — Auto-purges expired OTPs every 15 minutes

### 👤 Profile Management (Phase 2)
- **Create Profile** — Multi-step profile wizard with skills & interests
- **Get Profile** — Retrieve authenticated user's profile
- **Update Profile** — Partial profile updates
- **Skill Indexing** — Profiles indexed in Pinecone for semantic search

### 📂 Projects (Phase 3)
- **Create Project** — Define project with skills, features, team size; atomically creates a team with owner as first member
- **Get My Projects** — List all user's projects
- **Get All Projects** — Browse projects from other users (Explore view)
- **Get Project by ID** — Retrieve single project details
- **Update Project** — Modify project fields
- **Delete Project** — Remove project

### 🤖 AI Team Formation Agent (Phase 4)
- **Role Analysis** — LLM identifies required team roles from project requirements
- **Skill Matching** — Semantic search finds candidates via Pinecone vectors
- **Candidate Evaluation** — LLM scores candidates with reasoning
- **LangGraph Workflow** — Multi-node agent orchestration with MongoDB checkpoints

### 📨 Invitations & Join Requests (Phase 5) ✨ NEW
- **Send Invitation** — Project owner invites recommended teammates
- **Get My Invitations** — Retrieve all invitations received by the user
- **Update Invitation** — Accept or reject an invitation
- **Request to Join** — Non-owner users can request to join a project with a role and optional message
- **Get Join Requests** — Project owner views all pending join requests
- **Respond to Join Request** — Owner accepts or rejects; on accept, the requester is added to the team
- **Background Cleanup** — Auto-deletes old invitations daily (older than 7 days)

### 👥 Teams (Phase 5) ✨ NEW
- **Auto-creation** — Team is created atomically when a project is created (owner as first member)
- **team_id Reference** — Projects store a `team_id` reference; team data lives in the `teams` collection (single source of truth)
- **Get Team by ID** — Retrieve team details by team document ID
- **Get Team by Project ID** — Retrieve team details by associated project ID
- **Member Management** — New members are added via join request acceptance

### 🗓️ AI Project Planner Agent (Phase 6) ✨ NEW
- **Feature Extraction** — LLM analyzes project description to identify key features
- **Milestone Definition** — Breaks down features into logical sprints/milestones
- **Task Generation** — Creates detailed actionable tasks for each sprint
- **Async Execution** — LangGraph workflow runs asynchronously to prevent timeouts
- **Structured Output** — Returns JSON-compliant roadmaps using `LLMParser`

### 🏗️ Architecture
- **Framework:** FastAPI with async/await support
- **Auth Database:** MySQL (Aiven Cloud) with SQLModel ORM
- **App Database:** MongoDB (Atlas) with PyMongo async
- **Vector Store:** Pinecone with HuggingFace embeddings
- **AI Agents:** LangGraph + OpenRouter (free LLMs)
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
│   │   └── email_config.py     # SMTP configuration
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
│   │   └── schemas.py          # Auth request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── profiles.py         # Profile CRUD endpoints
│   │   ├── projects.py         # Project CRUD endpoints
│   │   ├── agents.py           # AI Agent endpoints
│   │   ├── invitations.py      # Invitation & Join Request endpoints
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
| `GET` | `/api/teams/team/{team_id}` | 🔒 | Get team by team ID |
| `GET` | `/api/teams/project/{project_id}` | 🔒 | Get team by project ID |

### AI Agents (🔒 Protected)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/agents/team-formation` | 🔒 | Find & evaluate team candidates |
| `POST` | `/api/agents/project-planner` | 🔒 | Generate project roadmap & tasks |

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

## 🚧 Roadmap

- [x] Phase 1: Authentication system ✅
- [x] Phase 2: User profiles + Pinecone skill indexing ✅
- [x] Phase 3: Projects CRUD ✅
- [x] Phase 4: AI Agent — Team Formation (LangGraph) ✅
- [x] Phase 5: Invitations, Join Requests & Teams ✅
- [x] Phase 6: AI Agent — Project Planner ✅ NEW
- [ ] Phase 7: Real-time collaboration (WebSocket)
- [ ] Phase 8: Code editor integration
- [ ] Phase 9: Whiteboard (tldraw)

---

## 📝 License

MIT © 2026

---

<div align="center">

**Built with ❤️ using FastAPI**

</div>
