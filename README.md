# 🚀 Unified Multi-Agent AI Platform — Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

**A modern, scalable backend for developer collaboration with AI-powered multi-agent capabilities.**

</div>

---

## ✨ Features

### 🔐 Authentication System
- **User Registration** — Secure signup with email validation
- **User Login** — JWT-based access & refresh tokens
- **Password Reset** — OTP via email with expiry
- **Token Refresh** — Seamless session management
- **Background Cleanup** — Auto-purges expired OTPs every 15 minutes

### 🏗️ Architecture
- **Framework:** FastAPI with async/await support
- **Database:** MySQL (Aiven Cloud) with SQLModel ORM
- **Security:** HS256 JWT tokens, bcrypt password hashing
- **Email:** FastAPI-Mail with Gmail SMTP

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── config/
│   │   ├── jwt_config.py      # JWT token creation & verification
│   │   ├── security.py        # Password hashing (bcrypt)
│   │   └── email_config.py    # SMTP configuration
│   │
│   ├── db/
│   │   ├── mysql_connection.py # Database engine & session
│   │   └── init_db.py          # Table creation on startup
│   │
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── password_reset_token.py  # OTP storage
│   │   └── schemas.py          # Pydantic request/response schemas
│   │
│   ├── routers/
│   │   └── auth.py             # Authentication endpoints
│   │
│   ├── services/
│   │   └── mail_service.py     # Email sending & OTP generation
│   │
│   └── main.py                 # FastAPI app & lifespan events
│
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create new user account |
| `POST` | `/api/auth/login` | Authenticate & get tokens |
| `POST` | `/api/auth/refresh-token` | Refresh access token |
| `POST` | `/api/auth/forgot-password` | Request OTP via email |
| `POST` | `/api/auth/reset-password` | Reset password with OTP |

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
MYSQL_DB_URL="mysql+pymysql://user:pass@host:port/dbname"

JWT_SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=21

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

### User Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| email | VARCHAR(255) | Unique, indexed |
| username | VARCHAR(255) | Unique, indexed |
| hashed_password | VARCHAR(255) | bcrypt hash |
| is_active | BOOLEAN | Account status |
| created_at | DATETIME | Registration timestamp |

### PasswordResetToken Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK → user.id (CASCADE) |
| otp | VARCHAR(255) | 6-digit code |
| expires_at | DATETIME | Validity deadline |
| is_used | BOOLEAN | One-time use flag |

---

## 🚧 Roadmap

- [x] Authentication system
- [ ] User profiles (MongoDB)
- [ ] AI Agent: Skill Matcher
- [ ] AI Agent: Team Formation
- [ ] AI Agent: Project Planner
- [ ] Real-time collaboration (WebSocket)
- [ ] Code editor integration
- [ ] Whiteboard (tldraw)

---

## 📝 License

MIT © 2026

---

<div align="center">

**Built with ❤️ using FastAPI**

</div>
