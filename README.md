# Touch Grass — AI-Powered Offline Activity Companion

A full-stack web application designed to help users spend less time behind digital screens and more time engaging with the physical, offline world. Activities are dynamically crafted and evaluated by a local open-weight Gemma model running via `llama.cpp`.

---

## 1. Project Structure

```text
week_1/
├── backend/
│   ├── .venv/               # Python virtual environment
│   ├── ai.py                # Local llama.cpp Gemma integration, prompt templates & curated fallback catalog
│   ├── database.py          # SQLAlchemy SQLite connection & session setup
│   ├── main.py              # FastAPI application, CORS, routers & business logic
│   ├── models.py            # SQLAlchemy models (UserPreference, UserStats, Challenge)
│   ├── requirement.txt      # Python dependencies
│   ├── schemas.py           # Pydantic data validation schemas
│   ├── test_backend.py      # Core unit tests
│   └── test_e2e_llama.py    # End-to-end integration test with mock llama.cpp server
├── frontend/
│   ├── public/
│   │   └── favicon.svg      # Sprout favicon
│   ├── src/
│   │   ├── components/
│   │   │   ├── AIStatusBanner.jsx   # Live connection indicator for local AI
│   │   │   ├── ChallengeDetails.jsx # Detailed activity review, materials & start CTA
│   │   │   ├── ChallengeMode.jsx    # Persistent focus countdown timer & offline mode
│   │   │   ├── Dashboard.jsx        # Stats, streaks, active challenge, recent activity
│   │   │   ├── HistoryView.jsx      # Historical activities, scores & reflections
│   │   │   ├── InterestsPicker.jsx  # Multi-interest, duration & difficulty selector
│   │   │   ├── Navbar.jsx           # App branding & status navigation
│   │   │   ├── ProofSubmission.jsx  # Dynamic Q&A reflection & optional photo upload
│   │   │   └── ResultsView.jsx      # AI score out of 100, rubric breakdown & feedback
│   │   ├── api.js           # REST API client
│   │   ├── App.css          # Responsive styling (calm sage green nature palette)
│   │   ├── App.jsx          # Main application orchestrator & refresh state recovery
│   │   ├── index.css        # Typography and base reset
│   │   └── main.jsx         # React 19 entry point
│   ├── index.html           # HTML template
│   ├── package.json         # Frontend dependencies and build scripts
│   └── vite.config.js       # Vite configuration
└── README.md
```

---

## 2. Technology Stack

- **Frontend:** React 19 + Vite (JavaScript)
- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Database:** SQLite (`touchgrass.db`) via SQLAlchemy
- **AI Model Server:** Local Gemma model served through `llama.cpp` at `http://127.0.0.1:8081`
- **Communication:** REST API via HTTP JSON requests
- **Persistence:** User preferences, stats, active timer timestamps, proof answers, and evaluations stored in SQLite

---

## 3. Installation & Startup (Windows)

Open two PowerShell windows:

### Terminal 1: Backend Setup & Launch

```powershell
cd c:\hacktoberfest\week_1\backend

# 1. Create and activate virtual environment (already set up)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install requirements
pip install -r requirement.txt

# 3. Start the FastAPI backend
uvicorn main:app --reload --port 8000
```

The API is now running at `http://127.0.0.1:8000`. Interactive documentation is accessible at `http://127.0.0.1:8000/docs`.

### Terminal 2: Frontend Setup & Launch

```powershell
cd c:\hacktoberfest\week_1\frontend

# 1. Install npm dependencies
npm install

# 2. Start the Vite development server
npm run dev
```

Open the printed URL (typically `http://localhost:5173`) in your browser.

---

## 4. Local `llama.cpp` Server Setup

The app connects to your local `llama.cpp` server serving Gemma on port `8081`:

```powershell
# Example startup command for llama.cpp server
./llama-server.exe -m path/to/gemma-model.gguf --port 8081 -c 2048
```

- Endpoint utilized: `POST http://127.0.0.1:8081/completion`
- If the model server is offline:
  - **Challenge Generation:** The application automatically serves curated, high-quality fallback offline challenges covering all interests and durations, labeled clearly with `📦 Curated Challenge`.
  - **Proof Evaluation:** The application safely preserves your submitted text and photo in SQLite and returns a descriptive `503 Service Unavailable` message asking you to launch `llama.cpp` and click **Retry Evaluation** (preventing fake or fabricated scores).

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and root greeting |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/api/ai/status` | Checks connectivity to local llama.cpp server |
| `GET` | `/api/preferences` | Retrieve user preferences and selected interests |
| `PUT` | `/api/preferences` | Update user preferences |
| `GET` | `/api/stats` | Retrieve current streak, longest streak, and total completed count |
| `POST` | `/api/challenges/generate` | Generate personalized offline activity using Gemma or fallback |
| `POST` | `/api/challenges` | Create a challenge record manually |
| `GET` | `/api/challenges` | List challenges (optional `?status=active\|completed`) |
| `GET` | `/api/challenges/active` | Get currently running challenge (enables timer persistence on refresh) |
| `GET` | `/api/challenges/{id}` | Get specific challenge details |
| `POST` | `/api/challenges/{id}/start` | Start countdown timer; records `started_at` & `target_end_at` |
| `POST` | `/api/challenges/{id}/submit` | Submit reflection answers & optional image; evaluate with Gemma |
| `POST` | `/api/challenges/{id}/abandon` | Abandon/cancel an active challenge |
| `GET` | `/api/history` | List all completed challenges with scores and feedback |

---

## 6. Verification and Tests Performed

The project was validated through multiple automated test suites:

1. **Unit & Logic Tests (`test_backend.py`):**
   - Health checks and AI status detection.
   - Preference reading and updating.
   - Challenge generation and timestamp calculation (`started_at`, `target_end_at`, `remaining_seconds`).
   - Browser refresh resilience (verifying that active timer continues accurately from timestamps).
   - Proof preservation on AI offline (ensures 503 is returned and user answers remain intact).
   - Duplicate submission protection (prevents double-scoring of completed tasks).
   - Challenge abandonment logic.
2. **E2E Local AI Mock Test (`test_e2e_llama.py`):**
   - Spun up a mock `llama.cpp` completion server on port 8081.
   - Performed real HTTP challenge generation, start, submission, score calculation out of 100, daily calendar streak calculation, and history persistence.
3. **Frontend Production Build:**
   - Ran `npm run build` using Vite 8 + React 19; bundles transformed and compiled in under 1 second with 0 errors.
