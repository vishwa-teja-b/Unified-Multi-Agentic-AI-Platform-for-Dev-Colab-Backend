# 🚀 Unified Multi-Agent AI Platform — Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

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

### 📂 Projects (Phase 3) ✨ NEW
- **Create Project** — Define project with skills, features, team size
- **Get My Projects** — List all user's projects
- **Get Project by ID** — Retrieve single project details
- **Update Project** — Modify project fields
- **Delete Project** — Remove project

### 🏗️ Architecture
- **Framework:** FastAPI with async/await support
- **Auth Database:** MySQL (Aiven Cloud) with SQLModel ORM
- **App Database:** MongoDB (Atlas) with PyMongo async
- **Vector Store:** Pinecone with HuggingFace embeddings
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
│   │   └── project_schema.py   # Project request/response DTOs
│   │
│   ├── models/
│   │   ├── user.py             # User model (MySQL)
│   │   ├── profiles.py         # Profile model (MongoDB)
│   │   ├── projects.py         # Project model (MongoDB)
│   │   ├── password_reset_token.py  # OTP storage
│   │   └── schemas.py          # Auth request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── profiles.py         # Profile CRUD endpoints
│   │   └── projects.py         # Project CRUD endpoints
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
| `POST` | `/api/projects/create-project` | 🔒 | Create new project |
| `GET` | `/api/projects/my-projects` | 🔒 | List user's projects |
| `GET` | `/api/projects/project/{id}` | 🔒 | Get single project |
| `PATCH` | `/api/projects/project/{id}` | 🔒 | Update project |
| `DELETE` | `/api/projects/project/{id}` | 🔒 | Delete project |

### Example: Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123"
  }'
```

### Example: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
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

The application includes a background worker that automatically cleans up:
- ✅ Used OTP tokens
- ✅ Expired OTP tokens

**Runs every 15 minutes** using `asyncio.create_task()` in the FastAPI lifespan.

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
  "team_members": [],
  "created_at": "2026-02-03T13:50:33Z"
}
```

---

## 🚧 Roadmap

- [x] Phase 1: Authentication system
- [x] Phase 2: User profiles + Pinecone skill indexing ✅
- [x] Phase 3: Projects CRUD ✅ NEW
- [ ] Phase 4: AI Agent — Skill Matcher (find developers)
- [ ] Phase 4: AI Agent — Team Formation
- [ ] Phase 5: AI Agent — Project Planner
- [ ] Phase 6: Real-time collaboration (WebSocket)
- [ ] Phase 7: Code editor integration
- [ ] Phase 7: Whiteboard (tldraw)

---

## 📝 License

MIT © 2026

---

<div align="center">

**Built with ❤️ using FastAPI**

</div>
