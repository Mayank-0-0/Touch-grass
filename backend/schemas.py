from typing import Optional, Any
from pydantic import BaseModel, Field


class PreferenceUpdate(BaseModel):
    selected_interests: list[str]
    default_duration: int = 30
    default_difficulty: str = "Medium"


class PreferenceResponse(BaseModel):
    id: int
    selected_interests: list[str]
    default_duration: int
    default_difficulty: str


class StatsResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_completed: int
    last_completed_date: Optional[str] = None


class ChallengeGenerateRequest(BaseModel):
    interest: Optional[str] = None
    duration_minutes: int = 30
    difficulty: str = "Medium"
    surprise_me: bool = False


class ChallengeCreate(BaseModel):
    title: str
    interest: str
    duration_minutes: int
    difficulty: str
    instructions: str
    materials: Optional[list[str]] = None
    expected_result: Optional[str] = None
    proof_instructions: Optional[str] = None
    follow_up_questions: Optional[list[str]] = None
    rubric: Optional[str] = None
    is_fallback: bool = False


class ChallengeResponse(BaseModel):
    id: int
    title: str
    interest: str
    duration_minutes: int
    difficulty: str
    instructions: str
    materials: Optional[list[str]] = None
    expected_result: Optional[str] = None
    proof_instructions: Optional[str] = None
    follow_up_questions: Optional[list[str]] = None
    rubric: Optional[str] = None
    is_fallback: bool = False
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    target_end_at: Optional[str] = None
    submitted_at: Optional[str] = None
    proof_answers: Optional[Any] = None
    proof_image: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    evaluation_details: Optional[Any] = None
    remaining_seconds: Optional[int] = None


class ProofSubmitRequest(BaseModel):
    proof_answers: Any  # dict mapping question to answer or text string
    proof_image: Optional[str] = None  # Base64 data url or path


class EvaluationResponse(BaseModel):
    challenge_id: int
    score: int
    feedback: str
    relevance: str
    quality: str
    completion_score: int
    current_streak: int
    longest_streak: int
    total_completed: int


class AIStatusResponse(BaseModel):
    online: bool
    server_url: str
    model_name: str
    message: str
