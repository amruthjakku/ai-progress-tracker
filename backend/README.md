# Backend (Legacy)

> ⚠️ **Note**: This backend is no longer required. The frontend now calls Supabase directly.

This folder contains the original FastAPI backend that was used before the refactor. It's kept for reference only.

## Original Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | Supabase (PostgreSQL) |
| Auth | JWT + Argon2 |
| File Storage | Local filesystem |

## If You Need the Backend

If you want to use the backend (for advanced customization):

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Then update `frontend/config.py` to use `API_URL = "http://localhost:8000"` and switch imports back to `utils.api`.
