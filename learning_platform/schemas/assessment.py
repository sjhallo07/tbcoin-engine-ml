"""Assessment-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    """Schema for creating a quiz question."""
    question_text: str
    question_type: str = Field(default="multiple_choice", pattern="^(multiple_choice|true_false|code|short_answer)$")
    options: List[str] = Field(default_factory=list)
    correct_answer: Any = None
    code_template: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    order_index: int = Field(default=0)


class QuestionResponse(BaseModel):
    """Schema for quiz question response (without answers for learners)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    quiz_id: int
    question_text: str
    question_type: str
    options: List[str] = Field(default_factory=list)
    code_template: Optional[str] = None
    points: int
    difficulty: str
    order_index: int


class QuestionWithAnswer(QuestionResponse):
    """Schema for question with answers (for review)."""
    correct_answer: Any = None
    expected_output: Optional[str] = None
    explanation: Optional[str] = None


class QuizCreate(BaseModel):
    """Schema for creating a quiz."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    quiz_type: str = Field(default="standard", pattern="^(standard|coding|practice)$")
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    passing_score: float = Field(default=70.0, ge=0, le=100)
    max_attempts: int = Field(default=3, ge=0)
    shuffle_questions: bool = True
    show_answers: bool = True
    is_final_exam: bool = False
    order_index: int = Field(default=0)


class QuizResponse(BaseModel):
    """Schema for quiz response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    module_id: int
    title: str
    description: Optional[str] = None
    quiz_type: str
    time_limit_minutes: Optional[int] = None
    passing_score: float
    max_attempts: int
    shuffle_questions: bool
    show_answers: bool
    is_final_exam: bool
    is_published: bool
    order_index: int
    question_count: int = 0
    created_at: datetime


class AnswerSubmission(BaseModel):
    """Single answer submission within an assessment."""
    question_id: int
    answer: Any  # Can be index, string, or code depending on question type


class AssessmentSubmission(BaseModel):
    """Schema for submitting assessment answers."""
    quiz_id: int
    answers: List[AnswerSubmission]
    time_spent_seconds: Optional[int] = None


class QuestionResult(BaseModel):
    """Result for a single question."""
    question_id: int
    is_correct: bool
    points_earned: int
    points_possible: int
    user_answer: Any
    correct_answer: Optional[Any] = None
    explanation: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    """Schema for assessment result response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    quiz_id: int
    quiz_title: str
    attempt_number: int
    status: str
    score: Optional[float] = None
    points_earned: int
    points_possible: int
    is_passed: Optional[bool] = None
    time_spent_seconds: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    question_results: List[QuestionResult] = Field(default_factory=list)
    feedback: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)


class AdaptiveLearningFeedback(BaseModel):
    """Adaptive learning feedback based on assessment results."""
    overall_performance: str  # excellent, good, needs_improvement, struggling
    strength_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    recommended_modules: List[str] = Field(default_factory=list)
    suggested_review_topics: List[str] = Field(default_factory=list)
    personalized_message: str
