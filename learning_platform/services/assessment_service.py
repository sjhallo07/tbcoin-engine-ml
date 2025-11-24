"""Assessment service for quizzes and evaluations."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from learning_platform.models.assessment import Quiz, QuizQuestion, UserAssessment, AssessmentResult
from learning_platform.schemas.assessment import (
    QuizCreate,
    QuestionCreate,
    AssessmentSubmission,
    AnswerSubmission,
)


class AssessmentService:
    """Service for assessment operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_quiz(self, module_id: int, quiz_data: QuizCreate) -> Quiz:
        """Create a new quiz for a module."""
        quiz = Quiz(
            module_id=module_id,
            title=quiz_data.title,
            description=quiz_data.description,
            quiz_type=quiz_data.quiz_type,
            time_limit_minutes=quiz_data.time_limit_minutes,
            passing_score=quiz_data.passing_score,
            max_attempts=quiz_data.max_attempts,
            shuffle_questions=quiz_data.shuffle_questions,
            show_answers=quiz_data.show_answers,
            is_final_exam=quiz_data.is_final_exam,
            order_index=quiz_data.order_index,
        )
        
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz
    
    def get_quiz_by_id(self, quiz_id: int) -> Optional[Quiz]:
        """Get a quiz by ID."""
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    def get_quizzes_for_module(self, module_id: int) -> List[Quiz]:
        """Get all quizzes for a module."""
        return self.db.query(Quiz).filter(
            Quiz.module_id == module_id,
            Quiz.is_published == True
        ).order_by(Quiz.order_index).all()
    
    def add_question(self, quiz_id: int, question_data: QuestionCreate) -> Optional[QuizQuestion]:
        """Add a question to a quiz."""
        quiz = self.get_quiz_by_id(quiz_id)
        if not quiz:
            return None
        
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            code_template=question_data.code_template,
            expected_output=question_data.expected_output,
            test_cases=question_data.test_cases,
            explanation=question_data.explanation,
            points=question_data.points,
            difficulty=question_data.difficulty,
            order_index=question_data.order_index,
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def get_quiz_questions(self, quiz_id: int) -> List[QuizQuestion]:
        """Get all questions for a quiz."""
        return self.db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).order_by(QuizQuestion.order_index).all()
    
    def start_assessment(self, user_id: int, quiz_id: int) -> Optional[UserAssessment]:
        """Start a new assessment attempt."""
        quiz = self.get_quiz_by_id(quiz_id)
        if not quiz:
            return None
        
        # Check attempt count
        existing_attempts = self.db.query(UserAssessment).filter(
            UserAssessment.user_id == user_id,
            UserAssessment.quiz_id == quiz_id
        ).count()
        
        if quiz.max_attempts > 0 and existing_attempts >= quiz.max_attempts:
            return None
        
        # Calculate total points
        questions = self.get_quiz_questions(quiz_id)
        total_points = sum(q.points for q in questions)
        
        assessment = UserAssessment(
            user_id=user_id,
            quiz_id=quiz_id,
            attempt_number=existing_attempts + 1,
            status="in_progress",
            points_possible=total_points,
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment
    
    def submit_assessment(
        self,
        assessment_id: int,
        submission: AssessmentSubmission
    ) -> Optional[UserAssessment]:
        """Submit answers for an assessment."""
        assessment = self.db.query(UserAssessment).filter(
            UserAssessment.id == assessment_id
        ).first()
        
        if not assessment or assessment.status != "in_progress":
            return None
        
        quiz = self.get_quiz_by_id(assessment.quiz_id)
        questions = {q.id: q for q in self.get_quiz_questions(assessment.quiz_id)}
        
        total_points = 0
        earned_points = 0
        answers_dict = {}
        
        for answer in submission.answers:
            question = questions.get(answer.question_id)
            if not question:
                continue
            
            is_correct = self._check_answer(question, answer.answer)
            points = question.points if is_correct else 0
            earned_points += points
            total_points += question.points
            
            # Create result record
            result = AssessmentResult(
                assessment_id=assessment_id,
                question_id=answer.question_id,
                user_answer=answer.answer,
                is_correct=is_correct,
                points_earned=points,
                points_possible=question.points,
            )
            self.db.add(result)
            answers_dict[str(answer.question_id)] = answer.answer
        
        # Update assessment
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        assessment.status = "completed"
        assessment.score = score
        assessment.points_earned = earned_points
        assessment.points_possible = total_points
        assessment.is_passed = score >= quiz.passing_score
        assessment.time_spent_seconds = submission.time_spent_seconds
        assessment.completed_at = datetime.utcnow()
        assessment.answers = answers_dict
        
        self.db.commit()
        self.db.refresh(assessment)
        return assessment
    
    def _check_answer(self, question: QuizQuestion, user_answer: Any) -> bool:
        """Check if an answer is correct.
        
        Handles various question types and answer formats robustly.
        """
        correct = question.correct_answer
        
        if question.question_type == "multiple_choice":
            # Handle single choice (int index) and multi-select (list of indices)
            if isinstance(correct, int):
                # Single correct answer (index)
                if isinstance(user_answer, list):
                    # User provided list but question has single answer
                    return len(user_answer) == 1 and user_answer[0] == correct
                return user_answer == correct
            elif isinstance(correct, list):
                # Multiple correct answers
                if not isinstance(user_answer, list):
                    user_answer = [user_answer]
                return set(user_answer) == set(correct)
            else:
                # String comparison fallback
                return str(user_answer).lower() == str(correct).lower()
        
        elif question.question_type == "true_false":
            # Normalize to boolean
            if isinstance(user_answer, str):
                user_answer = user_answer.lower() in ('true', 'yes', '1')
            return bool(user_answer) == bool(correct)
        
        elif question.question_type == "short_answer":
            # Case-insensitive comparison
            if isinstance(correct, list):
                return str(user_answer).lower().strip() in [str(c).lower().strip() for c in correct]
            return str(user_answer).lower().strip() == str(correct).lower().strip()
        
        elif question.question_type == "code":
            # For code questions, we would run test cases
            # This is a simplified check
            return str(user_answer).strip() == str(question.expected_output).strip()
        
        return False
    
    def get_user_assessments(self, user_id: int, quiz_id: Optional[int] = None) -> List[UserAssessment]:
        """Get all assessments for a user."""
        query = self.db.query(UserAssessment).filter(UserAssessment.user_id == user_id)
        if quiz_id:
            query = query.filter(UserAssessment.quiz_id == quiz_id)
        return query.order_by(UserAssessment.started_at.desc()).all()
    
    def get_assessment_results(self, assessment_id: int) -> List[AssessmentResult]:
        """Get all results for an assessment."""
        return self.db.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id
        ).all()
    
    def get_user_quiz_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for a user's quiz performance."""
        assessments = self.get_user_assessments(user_id)
        
        completed = [a for a in assessments if a.status == "completed"]
        if not completed:
            return {
                "total_quizzes_attempted": 0,
                "total_quizzes_passed": 0,
                "average_score": None,
                "best_score": None,
                "total_time_spent_seconds": 0,
            }
        
        scores = [a.score for a in completed if a.score is not None]
        passed = sum(1 for a in completed if a.is_passed)
        total_time = sum(a.time_spent_seconds or 0 for a in completed)
        
        return {
            "total_quizzes_attempted": len(completed),
            "total_quizzes_passed": passed,
            "average_score": sum(scores) / len(scores) if scores else None,
            "best_score": max(scores) if scores else None,
            "total_time_spent_seconds": total_time,
        }
