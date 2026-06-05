# Workflow Management System (WMS)

A FastAPI-based REST API for managing internal users, external clients, and their projects with role-based access control.

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/wms_testing
   ```

### Running the Application

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation (auto-generated):**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Setup

**Automatic Setup:** The application automatically:
- ✅ Creates the database if it doesn't exist
- ✅ Creates all required tables on startup
- ✅ Creates a default admin user (`admin` / `admin123`)

No manual database setup needed!

### Database Tables

| Table | Purpose |
|-------|---------|
| `roles_master` | Lookup table for user roles per team |
| `users` | Internal system users with role-based access |
| `clients` | External client organizations |
| `projects` | Client projects |
| `stage_master` | Workflow stages |
| `stage_activity_master` | Activities within each stage |
| `chapter_details` | Chapter information |
| `stages_details` | Detailed stage information |
| `workflow_master` | Workflow definitions |

## Logging

### View Logs in Real-Time (Console)

When you run the app, logs appear in the terminal:

```bash
uvicorn main:app --reload
```

**Output example:**
```
2026-06-05 14:23:45 | app.init_db | INFO     | Database connected
2026-06-05 14:23:46 | app.init_db | INFO     | Creating missing tables
2026-06-05 14:23:46 | app.init_db | INFO     | Created tables: users, clients, projects, ...
2026-06-05 14:23:46 | app.init_db | INFO     | Tables ready
```

### View Logs in File

Logs are automatically saved to `app.log` in the backend directory:

```bash
# View recent logs
cat app.log  # PowerShell: type app.log

# Watch logs in real-time
tail -f app.log  # PowerShell: Get-Content app.log -Tail 20 -Wait
```

**Log Rotation:** Logs automatically rotate daily at midnight and old logs are deleted after 1 day.

### Log Levels

- **INFO** - Important events (database operations, user creation, etc.)
- **DEBUG** - Detailed information (registered models, existing tables)
- **WARNING** - Warning messages (missing resources, etc.)
- **ERROR** - Error messages (connection failures, exceptions)

## Key Features

### Automatic Database Operations

On startup, the application:
1. Connects to PostgreSQL (creates database if needed)
2. Creates all tables if missing
3. Initializes default admin user
4. Logs all operations

### Authentication & Authorization

- Role-based access control (RBAC)
- User authentication with bcrypt password hashing
- Team-based role management
- Customer access configuration

### API Endpoints

Available routers:
- `/auth` - Authentication
- `/users` - User management
- `/roles` - Role management
- `/clients` - Client management
- `/projects` - Project management
- `/stages` - Stage management
- `/chapters` - Chapter information
- `/workflows` - Workflow management
- `/upload` - File upload

## Troubleshooting

### Database Connection Fails

**Error:** `psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed`

**Solution:** Make sure PostgreSQL is running and accessible. The application will try to create the database automatically if it doesn't exist.

### Tables Not Created

The application logs the creation process. Check the logs:
```bash
cat app.log | grep "Tables"
```

Should see:
```
2026-06-05 14:23:46 | app.init_db | INFO     | Creating missing tables
2026-06-05 14:23:46 | app.init_db | INFO     | Created tables: ...
2026-06-05 14:23:46 | app.init_db | INFO     | Tables ready
```

### Default Admin User Not Created

Check logs for warnings:
```bash
cat app.log | grep -i "admin"
```

The admin user is created on first startup with:
- Username: `admin`
- Password: `admin123`

## Development

### Database Schema

The application uses SQLAlchemy ORM with the following models:
- `RolesMaster` - User roles (unique per team)
- `User` - System users with bcrypt-hashed passwords
- `Client` - External client organizations
- `Project` - Client projects
- `StageMaster` - Workflow stages
- `StageActivityMaster` - Stage activities
- `ChapterInfo` - Chapter information
- `StageDetail` - Stage details
- `WorkflowMaster` - Workflow definitions

All models inherit from `Base` and are defined in `app/models/`.

### Adding New Models

1. Create a new file in `app/models/`
2. Inherit from `Base` (from `app.init_db`)
3. Define `__tablename__` and columns
4. Import the model in `app/init_db.py` → `create_tables()` function

Example:
```python
from sqlalchemy import Column, Integer, String
from app.init_db import Base

class NewModel(Base):
    __tablename__ = "new_model"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

## Project Structure

```
backend/
├── main.py                    # Application entry point
├── app/
│   ├── __init__.py
│   ├── init_db.py            # Database setup & logging
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── crud/                 # Database operations
│   ├── routers/              # API route handlers
│   ├── auth/                 # Authentication logic
│   └── config/               # Configuration files
├── .env                      # Environment variables
└── app.log                   # Application logs (auto-created)
```

## CORS Configuration

Currently allows requests from `http://localhost:5173` (frontend dev server).

To modify:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-url"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Support

For issues or questions, check:
1. Application logs in `app.log`
2. Console output from `uvicorn`
3. PostgreSQL logs

---

**Status:** ✅ Database auto-initialization | ✅ Automatic table creation | ✅ Comprehensive logging
