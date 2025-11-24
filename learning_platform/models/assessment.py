"""Assessment models for quizzes and evaluations."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from learning_platform.models.base import Base


class Quiz(Base):
    """Quiz model for module assessments."""
    
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False, index=True)
    
    # Quiz details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quiz_type = Column(String(20), default="standard")  # standard, coding, practice
    
    # Settings
    time_limit_minutes = Column(Integer, nullable=True)  # None means no limit
    passing_score = Column(Float, default=70.0)  # Minimum percentage to pass
    max_attempts = Column(Integer, default=3)  # 0 means unlimited
    shuffle_questions = Column(Boolean, default=True)
    show_answers = Column(Boolean, default=True)  # Show correct answers after completion
    
    # Placement
    order_index = Column(Integer, default=0)
    is_final_exam = Column(Boolean, default=False)
    
    # Status
    is_published = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = relationship("LearningModule", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    assessments = relationship("UserAssessment", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    """Individual questions within a quiz."""
    
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, true_false, code, short_answer
    
    # For multiple choice/true-false
    options = Column(JSON, default=list)  # List of option strings
    correct_answer = Column(JSON, nullable=True)  # Index(es) or string depending on type
    
    # For code questions
    code_template = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    test_cases = Column(JSON, default=list)  # List of test case dicts
    
    # Explanation
    explanation = Column(Text, nullable=True)  # Shown after answering
    
    # Scoring
    points = Column(Integer, default=1)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    
    # Ordering
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class UserAssessment(Base):
    """Track user quiz attempts."""
    
    __tablename__ = "user_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    
    # Attempt info
    attempt_number = Column(Integer, default=1)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    
    # Scoring
    score = Column(Float, nullable=True)  # Percentage score
    points_earned = Column(Integer, default=0)
    points_possible = Column(Integer, default=0)
    is_passed = Column(Boolean, nullable=True)
    
    # Timing
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Answers (stored as JSON for flexibility)
    answers = Column(JSON, default=dict)  # {question_id: user_answer}
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    quiz = relationship("Quiz", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResult(Base):
    """Individual question results within an assessment."""
    
    __tablename__ = "assessment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("user_assessments.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False, index=True)
    
    # Answer
    user_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    # Scoring
    points_earned = Column(Integer, default=0)
    points_possible = Column(Integer, default=1)
    
    # For code questions
    code_output = Column(Text, nullable=True)
    test_results = Column(JSON, default=dict)  # {test_name: passed/failed}
    
    # Timestamps
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("UserAssessment", back_populates="results")
