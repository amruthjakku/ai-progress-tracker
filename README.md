# Assignment Submission & Review Platform

A web platform where students submit assignments and admins review them with in-browser file preview.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | Supabase (PostgreSQL) |
| Auth | JWT tokens |

## Features

- ✅ **Student Portal**: Submit assignments (PDF, DOCX, PPTX)
- ✅ **Admin Portal**: Review submissions with inline file preview
- ✅ **Web Preview**: View files directly in browser (no download needed)
- ✅ **Grading**: Assign marks and provide feedback
- ✅ **Role-based Access**: Students and Admins have different views

## Quick Start

### 1. Database Setup
1. Create a [Supabase](https://supabase.com) project
2. Run the SQL schema in `database/schema.sql`
3. Copy your project URL and anon key

### 2. Setup Virtual Environment (Universal)
```bash
cd d:\ai-progress-tracker
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/Mac

# If venv doesn't exist:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Edit backend/.env with your Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Run Frontend (new terminal)
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 6. Access the App
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # Supabase client
│   ├── schemas.py           # Pydantic models
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── assignments.py
│   │   ├── submissions.py
│   │   ├── reviews.py
│   │   └── files.py
│   ├── services/
│   │   └── file_preview.py  # Document conversion
│   └── utils/
│       └── auth.py          # JWT helpers
│
├── frontend/
│   ├── app.py               # Main Streamlit app
│   ├── config.py            # API settings
│   ├── components/          # UI components
│   │   ├── auth.py
│   │   ├── file_preview.py
│   │   └── grading.py
│   ├── pages/               # Streamlit pages
│   │   ├── 1_Student_Dashboard.py
│   │   ├── 2_Submit_Assignment.py
│   │   ├── 3_My_Grades.py
│   │   ├── 1_Admin_Dashboard.py
│   │   ├── 2_Manage_Assignments.py
│   │   └── 3_Review_Submissions.py
│   └── utils/
│       └── api.py           # Backend client
│
└── database/
    └── schema.sql           # Supabase SQL schema
```

## Configuration

### Backend (.env)
```
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
JWT_SECRET=your-secret-key
```

### Frontend (.env)
```
API_URL=http://localhost:8000
```

## Supported File Types

| Type | Preview Method |
|------|----------------|
| PDF | Embedded iframe |
| DOCX | Converted to HTML |
| PPTX | Slide images |
