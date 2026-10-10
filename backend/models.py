from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    selected_interests = Column(Text, default='["Walking", "Reading", "Gardening"]')
    default_duration = Column(Integer, default=30)
    default_difficulty = Column(String, default="Medium")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
    last_completed_date = Column(String, nullable=True)  # YYYY-MM-DD
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    interest = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    materials = Column(Text, nullable=True)  # JSON-encoded array or plain text
    expected_result = Column(Text, nullable=True)
    proof_instructions = Column(Text, nullable=True)
    follow_up_questions = Column(Text, nullable=True)  # JSON-encoded array of questions
    rubric = Column(Text, nullable=True)
    is_fallback = Column(Boolean, default=False)
    status = Column(String, default="draft")  # draft, active, completed, abandoned
    created_at = Column(DateTime, default=get_utc_now)
    started_at = Column(DateTime, nullable=True)
    target_end_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    proof_answers = Column(Text, nullable=True)  # JSON-encoded answers or text
    proof_image = Column(Text, nullable=True)  # Base64 image data URI or relative path
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    evaluation_details = Column(Text, nullable=True)  # JSON {relevance, quality, completion_score}
