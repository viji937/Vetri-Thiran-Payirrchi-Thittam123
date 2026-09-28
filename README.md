# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy project documentation.

## Features

- User form for name, User ID, age, weight, goal and workout intensity
- AI-generated 7-day workout plan using Gemini
- AI-generated nutrition/recovery tip
- Feedback-based plan revision
- SQLite persistence with SQLAlchemy
- Admin dashboard for viewing and deleting users
- FastAPI Swagger docs
- Demo mode for testing without an API key
- Automated tests

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_flash_generator.py
│   ├── gemini_generator.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   └── updated_plan.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── admin_login.html
│   ├── all_users.html
│   ├── index.html
│   └── result.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Important Gemini note

The original documentation used `google-generativeai` and Gemini 1.5 model names. This implementation uses Google's current `google-genai` Python SDK and configurable current model IDs instead.

## Windows / VS Code setup

Open the FitBuddy folder in VS Code.

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate it

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
.venv\Scripts\activate
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create your environment file

Copy `.env.example` to `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Then open `.env` and put your Gemini API key in:

```env
GEMINI_API_KEY=your_real_key_here
```

Keep `.env` private. It is ignored by Git.

### 5. Start the application

```powershell
uvicorn app.main:app --reload
```

Open:

- Home: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Admin: http://127.0.0.1:8000/view-all-users?key=YOUR_ADMIN_KEY

## Test without Gemini first

For the first run, this is recommended.

In `.env`:

```env
DEMO_MODE=true
ADMIN_KEY=test-key
```

Then:

```powershell
uvicorn app.main:app --reload
```

The app will generate deterministic demo plans without calling Gemini.

After the UI works, change:

```env
DEMO_MODE=false
GEMINI_API_KEY=your_real_key
```

Restart Uvicorn.

## Automated tests

Run:

```powershell
pytest -q
```

The tests force demo mode and do not consume Gemini API calls.

## Manual test checklist

1. Open `/`.
2. Enter a name and unique User ID.
3. Select a goal and intensity.
4. Click **Generate 7-Day Plan**.
5. Confirm the result page shows the profile, plan and nutrition/recovery tip.
6. Enter feedback such as `Add more mobility and keep the sessions comfortable`.
7. Confirm the updated plan appears.
8. Open the admin page with the configured admin key.
9. Confirm the user and plan are listed.
10. Test the delete button.
11. Open `/docs` and inspect the FastAPI endpoints.

## Notes

This project is a demonstration/reference implementation. The AI output is general wellness guidance and should not be treated as medical diagnosis or treatment. For injuries, persistent symptoms, or health conditions, use qualified professional guidance.
