"""Assessment and quiz endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from learning_platform.api.dependencies import get_db, require_auth
from learning_platform.models.user import User
from learning_platform.schemas.assessment import (
    QuizCreate,
    QuizResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionWithAnswer,
    AssessmentSubmission,
    AssessmentResultResponse,
    AdaptiveLearningFeedback,
)
from learning_platform.services.assessment_service import AssessmentService
from learning_platform.services.adaptive_learning_service import AdaptiveLearningService
from learning_platform.services.module_service import ModuleService

router = APIRouter()


@router.get("/module/{module_slug}/quizzes", response_model=List[QuizResponse])
async def get_module_quizzes(module_slug: str, db: Session = Depends(get_db)):
    """Get all quizzes for a module."""
    module_service = ModuleService(db)
    module = module_service.get_module_by_slug(module_slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    assessment_service = AssessmentService(db)
    quizzes = assessment_service.get_quizzes_for_module(module.id)
    
    # Add question count
    result = []
    for quiz in quizzes:
        questions = assessment_service.get_quiz_questions(quiz.id)
        quiz_dict = {
            **quiz.__dict__,
            "question_count": len(questions)
        }
        result.append(quiz_dict)
    
    return result


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a specific quiz."""
    service = AssessmentService(db)
    quiz = service.get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    questions = service.get_quiz_questions(quiz_id)
    return {
        **quiz.__dict__,
        "question_count": len(questions)
    }


@router.get("/quiz/{quiz_id}/questions", response_model=List[QuestionResponse])
async def get_quiz_questions(
    quiz_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get questions for a quiz (without answers)."""
    service = AssessmentService(db)
    quiz = service.get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    questions = service.get_quiz_questions(quiz_id)
    return questions


@router.post("/quiz/{quiz_id}/start")
async def start_quiz(
    quiz_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Start a quiz attempt."""
    service = AssessmentService(db)
    quiz = service.get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    assessment = service.start_assessment(current_user.id, quiz_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum attempts reached for this quiz"
        )
    
    questions = service.get_quiz_questions(quiz_id)
    
    return {
        "assessment_id": assessment.id,
        "attempt_number": assessment.attempt_number,
        "time_limit_minutes": quiz.time_limit_minutes,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": q.options,
                "code_template": q.code_template,
                "points": q.points,
            }
            for q in questions
        ]
    }


@router.post("/submit", response_model=AssessmentResultResponse)
async def submit_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Submit quiz answers."""
    service = AssessmentService(db)
    
    # Get the assessment for this quiz by user
    assessments = service.get_user_assessments(current_user.id, submission.quiz_id)
    in_progress = next((a for a in assessments if a.status == "in_progress"), None)
    
    if not in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active assessment found. Start the quiz first."
        )
    
    result = service.submit_assessment(in_progress.id, submission)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit assessment"
        )
    
    quiz = service.get_quiz_by_id(submission.quiz_id)
    question_results = service.get_assessment_results(result.id)
    
    # Get questions for feedback
    questions = {q.id: q for q in service.get_quiz_questions(submission.quiz_id)}
    
    # Generate feedback
    adaptive_service = AdaptiveLearningService(db)
    feedback = adaptive_service.analyze_performance(current_user.id)
    
    return AssessmentResultResponse(
        id=result.id,
        quiz_id=result.quiz_id,
        quiz_title=quiz.title if quiz else "Unknown",
        attempt_number=result.attempt_number,
        status=result.status,
        score=result.score,
        points_earned=result.points_earned,
        points_possible=result.points_possible,
        is_passed=result.is_passed,
        time_spent_seconds=result.time_spent_seconds,
        started_at=result.started_at,
        completed_at=result.completed_at,
        question_results=[
            {
                "question_id": r.question_id,
                "is_correct": r.is_correct,
                "points_earned": r.points_earned,
                "points_possible": r.points_possible,
                "user_answer": r.user_answer,
                "correct_answer": questions[r.question_id].correct_answer if quiz.show_answers else None,
                "explanation": questions[r.question_id].explanation if quiz.show_answers else None,
            }
            for r in question_results
            if r.question_id in questions
        ],
        feedback=feedback.personalized_message,
        recommendations=feedback.recommended_modules
    )


@router.get("/my-results", response_model=List[AssessmentResultResponse])
async def get_my_results(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's assessment results."""
    service = AssessmentService(db)
    assessments = service.get_user_assessments(current_user.id)
    
    results = []
    for a in assessments:
        quiz = service.get_quiz_by_id(a.quiz_id)
        results.append(AssessmentResultResponse(
            id=a.id,
            quiz_id=a.quiz_id,
            quiz_title=quiz.title if quiz else "Unknown",
            attempt_number=a.attempt_number,
            status=a.status,
            score=a.score,
            points_earned=a.points_earned,
            points_possible=a.points_possible,
            is_passed=a.is_passed,
            time_spent_seconds=a.time_spent_seconds,
            started_at=a.started_at,
            completed_at=a.completed_at,
            question_results=[],
            feedback=None,
            recommendations=[]
        ))
    
    return results


@router.get("/statistics")
async def get_quiz_statistics(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's quiz statistics."""
    service = AssessmentService(db)
    stats = service.get_user_quiz_statistics(current_user.id)
    return stats


@router.get("/adaptive-feedback", response_model=AdaptiveLearningFeedback)
async def get_adaptive_feedback(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get personalized learning feedback based on performance."""
    service = AdaptiveLearningService(db)
    feedback = service.analyze_performance(current_user.id)
    return feedback


@router.post("/module/{module_slug}/quiz", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    module_slug: str,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    """Create a quiz for a module (admin only)."""
    module_service = ModuleService(db)
    module = module_service.get_module_by_slug(module_slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    service = AssessmentService(db)
    quiz = service.create_quiz(module.id, quiz_data)
    
    return {
        **quiz.__dict__,
        "question_count": 0
    }


@router.post("/quiz/{quiz_id}/question", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question(
    quiz_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db)
):
    """Add a question to a quiz (admin only)."""
    service = AssessmentService(db)
    question = service.add_question(quiz_id, question_data)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return question
