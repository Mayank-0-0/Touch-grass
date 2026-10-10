import json
import logging
from datetime import datetime, timedelta, date, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
import models
from schemas import (
    PreferenceUpdate, PreferenceResponse,
    StatsResponse,
    ChallengeGenerateRequest, ChallengeCreate, ChallengeResponse,
    ProofSubmitRequest, EvaluationResponse,
    AIStatusResponse
)
from ai import (
    generate_challenge_with_gemma,
    evaluate_proof_with_gemma,
    check_ai_status,
    AIServerUnavailableError
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Touch Grass — AI-Powered Offline Activity Companion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create_prefs(db: Session) -> models.UserPreference:
    prefs = db.query(models.UserPreference).filter(models.UserPreference.id == 1).first()
    if not prefs:
        prefs = models.UserPreference(
            id=1,
            selected_interests=json.dumps(["Walking", "Reading", "Gardening", "Drawing"]),
            default_duration=30,
            default_difficulty="Medium"
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


def _get_or_create_stats(db: Session) -> models.UserStats:
    stats = db.query(models.UserStats).filter(models.UserStats.id == 1).first()
    if not stats:
        stats = models.UserStats(
            id=1,
            current_streak=0,
            longest_streak=0,
            total_completed=0,
            last_completed_date=None
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


def _format_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _calc_remaining_seconds(target_end_at) -> int:
    if not target_end_at:
        return 0
    now = datetime.now(timezone.utc)
    if target_end_at.tzinfo is None:
        target_end_at = target_end_at.replace(tzinfo=timezone.utc)
    if target_end_at > now:
        return int((target_end_at - now).total_seconds())
    return 0


def _serialize_challenge(c: models.Challenge) -> dict:
    materials_list = []
    if c.materials:
        try:
            materials_list = json.loads(c.materials) if c.materials.startswith("[") else [c.materials]
        except Exception:
            materials_list = [c.materials]

    questions_list = []
    if c.follow_up_questions:
        try:
            questions_list = json.loads(c.follow_up_questions) if c.follow_up_questions.startswith("[") else [c.follow_up_questions]
        except Exception:
            questions_list = [c.follow_up_questions]

    proof_answers_val = None
    if c.proof_answers:
        try:
            proof_answers_val = json.loads(c.proof_answers)
        except Exception:
            proof_answers_val = c.proof_answers

    eval_details_val = None
    if c.evaluation_details:
        try:
            eval_details_val = json.loads(c.evaluation_details)
        except Exception:
            eval_details_val = c.evaluation_details

    remaining_seconds = 0
    if c.status == "active":
        remaining_seconds = _calc_remaining_seconds(c.target_end_at)

    return {
        "id": c.id,
        "title": c.title,
        "interest": c.interest,
        "duration_minutes": c.duration_minutes,
        "difficulty": c.difficulty,
        "instructions": c.instructions,
        "materials": materials_list,
        "expected_result": c.expected_result,
        "proof_instructions": c.proof_instructions,
        "follow_up_questions": questions_list,
        "rubric": c.rubric,
        "is_fallback": bool(c.is_fallback),
        "status": c.status,
        "created_at": _format_iso_utc(c.created_at),
        "started_at": _format_iso_utc(c.started_at),
        "target_end_at": _format_iso_utc(c.target_end_at),
        "submitted_at": _format_iso_utc(c.submitted_at),
        "proof_answers": proof_answers_val,
        "proof_image": c.proof_image,
        "score": c.score,
        "feedback": c.feedback,
        "evaluation_details": eval_details_val,
        "remaining_seconds": remaining_seconds
    }


# Routes
@app.get("/")
def root():
    return {
        "message": "Touch Grass API is running",
        "app": "Touch Grass",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/ai/status", response_model=AIStatusResponse)
def get_ai_status():
    """Check connectivity to local llama.cpp Gemma server."""
    status_info = check_ai_status()
    return status_info


@app.get("/api/preferences", response_model=PreferenceResponse)
def get_preferences(db: Session = Depends(get_db)):
    prefs = _get_or_create_prefs(db)
    interests = json.loads(prefs.selected_interests) if prefs.selected_interests else []
    return {
        "id": prefs.id,
        "selected_interests": interests,
        "default_duration": prefs.default_duration,
        "default_difficulty": prefs.default_difficulty
    }


@app.put("/api/preferences", response_model=PreferenceResponse)
def update_preferences(data: PreferenceUpdate, db: Session = Depends(get_db)):
    prefs = _get_or_create_prefs(db)
    prefs.selected_interests = json.dumps(data.selected_interests)
    prefs.default_duration = data.default_duration
    prefs.default_difficulty = data.default_difficulty
    db.commit()
    db.refresh(prefs)
    return {
        "id": prefs.id,
        "selected_interests": data.selected_interests,
        "default_duration": prefs.default_duration,
        "default_difficulty": prefs.default_difficulty
    }


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    stats = _get_or_create_stats(db)
    return {
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
        "total_completed": stats.total_completed,
        "last_completed_date": stats.last_completed_date
    }


@app.post("/api/challenges/generate", response_model=ChallengeResponse)
def generate_challenge(req: ChallengeGenerateRequest, db: Session = Depends(get_db)):
    # Retrieve recent challenge titles to avoid repetitive tasks
    recent = db.query(models.Challenge.title).order_by(models.Challenge.id.desc()).limit(5).all()
    recent_titles = [r[0] for r in recent]

    target_interest = req.interest
    if req.surprise_me or not target_interest:
        target_interest = None

    raw_challenge = generate_challenge_with_gemma(
        interest=target_interest,
        duration_minutes=req.duration_minutes,
        difficulty=req.difficulty,
        recent_titles=recent_titles
    )

    new_challenge = models.Challenge(
        title=raw_challenge.get("title", "Offline Exploration"),
        interest=raw_challenge.get("interest", target_interest or "General"),
        duration_minutes=raw_challenge.get("duration_minutes", req.duration_minutes),
        difficulty=raw_challenge.get("difficulty", req.difficulty),
        instructions=raw_challenge.get("instructions", "Engage in an offline activity."),
        materials=json.dumps(raw_challenge.get("materials", [])),
        expected_result=raw_challenge.get("expected_result", ""),
        proof_instructions=raw_challenge.get("proof_instructions", "Reflect on your experience."),
        follow_up_questions=json.dumps(raw_challenge.get("follow_up_questions", [])),
        rubric=raw_challenge.get("rubric", "Reflective depth and observational effort."),
        is_fallback=bool(raw_challenge.get("is_fallback", False)),
        status="draft"
    )

    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

    return _serialize_challenge(new_challenge)


@app.post("/api/challenges", response_model=ChallengeResponse)
def create_challenge(c: ChallengeCreate, db: Session = Depends(get_db)):
    new_challenge = models.Challenge(
        title=c.title,
        interest=c.interest,
        duration_minutes=c.duration_minutes,
        difficulty=c.difficulty,
        instructions=c.instructions,
        materials=json.dumps(c.materials or []),
        expected_result=c.expected_result,
        proof_instructions=c.proof_instructions,
        follow_up_questions=json.dumps(c.follow_up_questions or []),
        rubric=c.rubric,
        is_fallback=c.is_fallback,
        status="draft"
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    return _serialize_challenge(new_challenge)


@app.get("/api/challenges", response_model=List[ChallengeResponse])
def get_challenges(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Challenge)
    if status:
        query = query.filter(models.Challenge.status == status)
    challenges = query.order_by(models.Challenge.id.desc()).all()
    return [_serialize_challenge(c) for c in challenges]


@app.get("/api/challenges/active", response_model=Optional[ChallengeResponse])
def get_active_challenge(db: Session = Depends(get_db)):
    """Fetch currently active challenge to restore state after browser refresh."""
    active = db.query(models.Challenge).filter(models.Challenge.status == "active").order_by(models.Challenge.id.desc()).first()
    if not active:
        return None
    return _serialize_challenge(active)


@app.get("/api/challenges/{challenge_id}", response_model=ChallengeResponse)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return _serialize_challenge(c)


@app.post("/api/challenges/{challenge_id}/start", response_model=ChallengeResponse)
def start_challenge(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if c.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot restart a completed challenge")

    # If another challenge is currently active, mark it abandoned so there's no conflict
    other_actives = db.query(models.Challenge).filter(
        models.Challenge.status == "active",
        models.Challenge.id != challenge_id
    ).all()
    for item in other_actives:
        item.status = "abandoned"

    now = datetime.now(timezone.utc)
    c.status = "active"
    c.started_at = now
    c.target_end_at = now + timedelta(minutes=c.duration_minutes)

    db.commit()
    db.refresh(c)
    return _serialize_challenge(c)


@app.post("/api/challenges/{challenge_id}/abandon", response_model=ChallengeResponse)
def abandon_challenge(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if c.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot abandon an already completed challenge")

    c.status = "abandoned"
    db.commit()
    db.refresh(c)
    return _serialize_challenge(c)


@app.post("/api/challenges/{challenge_id}/submit", response_model=EvaluationResponse)
def submit_proof(challenge_id: int, req: ProofSubmitRequest, db: Session = Depends(get_db)):
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Prevent duplicate submissions and scoring
    if c.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Challenge has already been submitted and scored."
        )

    # Immediately preserve user's proof in DB so answers are never lost
    c.submitted_at = datetime.now(timezone.utc)
    c.proof_answers = json.dumps(req.proof_answers) if isinstance(req.proof_answers, (dict, list)) else str(req.proof_answers)
    if req.proof_image:
        c.proof_image = req.proof_image
    db.commit()

    # Extract dynamic questions list
    questions_list = []
    if c.follow_up_questions:
        try:
            questions_list = json.loads(c.follow_up_questions) if c.follow_up_questions.startswith("[") else [c.follow_up_questions]
        except Exception:
            questions_list = [c.follow_up_questions]

    # Evaluate proof with local Gemma via llama.cpp
    try:
        evaluation = evaluate_proof_with_gemma(
            challenge_title=c.title,
            interest=c.interest,
            duration_minutes=c.duration_minutes,
            difficulty=c.difficulty,
            instructions=c.instructions,
            rubric=c.rubric or "",
            follow_up_questions=questions_list,
            proof_answers=req.proof_answers,
            has_image=bool(req.proof_image)
        )
    except AIServerUnavailableError as e:
        # Prompt rule: Do not silently fabricate AI scores if local server is down. Preserve user data and return 503 error.
        logger.warning("Local AI evaluation server unavailable: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Local AI model server (llama.cpp at http://127.0.0.1:8081) is not running or unreachable. Your proof has been saved. Please start llama.cpp and retry evaluation."
        )

    # Evaluation succeeded: update challenge record
    c.score = evaluation["final_score"]
    c.feedback = evaluation["feedback"]
    c.evaluation_details = json.dumps({
        "relevance": evaluation["relevance"],
        "quality": evaluation["quality"],
        "completion_score": evaluation["completion_score"]
    })
    c.status = "completed"

    # Update UserStats and Daily Streak
    stats = _get_or_create_stats(db)
    today_str = date.today().isoformat()  # YYYY-MM-DD

    if stats.last_completed_date == today_str:
        # Already completed a challenge today; do not increment streak again
        stats.total_completed += 1
    else:
        if stats.last_completed_date:
            try:
                last_d = date.fromisoformat(stats.last_completed_date)
                day_diff = (date.today() - last_d).days
                if day_diff == 1:
                    # Consecutive calendar day streak
                    stats.current_streak += 1
                else:
                    # Streak broken (gap of more than 1 day)
                    stats.current_streak = 1
            except Exception:
                stats.current_streak = 1
        else:
            # First ever completed challenge
            stats.current_streak = 1

        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak

        stats.last_completed_date = today_str
        stats.total_completed += 1

    db.commit()
    db.refresh(stats)

    return {
        "challenge_id": c.id,
        "score": evaluation["final_score"],
        "feedback": evaluation["feedback"],
        "relevance": evaluation["relevance"],
        "quality": evaluation["quality"],
        "completion_score": evaluation["completion_score"],
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
        "total_completed": stats.total_completed
    }


@app.get("/api/history", response_model=List[ChallengeResponse])
def get_history(db: Session = Depends(get_db)):
    """Fetch completed challenges ordered by completion date descending."""
    completed = db.query(models.Challenge).filter(
        models.Challenge.status == "completed"
    ).order_by(models.Challenge.submitted_at.desc()).all()

    return [_serialize_challenge(c) for c in completed]
