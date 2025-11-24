"""Tests for learning platform models and services."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from learning_platform.models.base import Base, init_db
from learning_platform.models.user import User, UserProgress
from learning_platform.models.module import LearningModule, ModuleContent
from learning_platform.models.assessment import Quiz, QuizQuestion, UserAssessment

from learning_platform.schemas.user import UserCreate, UserUpdate
from learning_platform.schemas.module import LearningModuleCreate, ModuleContentCreate
from learning_platform.schemas.assessment import QuizCreate, QuestionCreate, AssessmentSubmission, AnswerSubmission

from learning_platform.services.user_service import UserService
from learning_platform.services.module_service import ModuleService
from learning_platform.services.assessment_service import AssessmentService
from learning_platform.services.adaptive_learning_service import AdaptiveLearningService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestUserService:
    """Test user service functionality."""
    
    def test_create_user(self, db_session):
        """Test user creation."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            skill_level="beginner"
        )
        
        user = service.create_user(user_data)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.skill_level == "beginner"
        assert user.hashed_password != "password123"  # Password should be hashed
    
    def test_get_user_by_username(self, db_session):
        """Test retrieving user by username."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="findme",
            email="findme@example.com",
            password="password123"
        )
        service.create_user(user_data)
        
        found_user = service.get_user_by_username("findme")
        
        assert found_user is not None
        assert found_user.username == "findme"
    
    def test_authenticate_user(self, db_session):
        """Test user authentication."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="authuser",
            email="auth@example.com",
            password="secretpass"
        )
        service.create_user(user_data)
        
        # Test correct credentials
        auth_user = service.authenticate_user("authuser", "secretpass")
        assert auth_user is not None
        assert auth_user.username == "authuser"
        
        # Test wrong password
        wrong_auth = service.authenticate_user("authuser", "wrongpass")
        assert wrong_auth is None
    
    def test_update_user(self, db_session):
        """Test user profile update."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="updateuser",
            email="update@example.com",
            password="password123"
        )
        user = service.create_user(user_data)
        
        update_data = UserUpdate(
            full_name="Updated Name",
            skill_level="intermediate"
        )
        
        updated_user = service.update_user(user.id, update_data)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.skill_level == "intermediate"


class TestModuleService:
    """Test module service functionality."""
    
    def test_create_module(self, db_session):
        """Test module creation."""
        service = ModuleService(db_session)
        
        module_data = LearningModuleCreate(
            title="Test Module",
            slug="test-module",
            description="A test learning module",
            category="ml-basics",
            difficulty_level="beginner",
            library="scikit-learn",
            estimated_duration_minutes=60,
            topics=["machine learning", "basics"],
            learning_objectives=["Learn ML basics"]
        )
        
        module = service.create_module(module_data)
        
        assert module.id is not None
        assert module.title == "Test Module"
        assert module.slug == "test-module"
        assert module.difficulty_level == "beginner"
    
    def test_get_module_by_slug(self, db_session):
        """Test retrieving module by slug."""
        service = ModuleService(db_session)
        
        module_data = LearningModuleCreate(
            title="Find Module",
            slug="find-module",
            category="deep-learning",
            difficulty_level="intermediate"
        )
        service.create_module(module_data)
        
        found = service.get_module_by_slug("find-module")
        
        assert found is not None
        assert found.title == "Find Module"
    
    def test_get_modules_by_difficulty(self, db_session):
        """Test filtering modules by difficulty."""
        service = ModuleService(db_session)
        
        # Create modules at different levels
        for i, level in enumerate(["beginner", "beginner", "intermediate"]):
            module_data = LearningModuleCreate(
                title=f"Module {i}",
                slug=f"module-{i}",
                category="ml-basics",
                difficulty_level=level
            )
            module = service.create_module(module_data)
            service.publish_module(module.id)
        
        beginner_modules = service.get_modules_by_difficulty("beginner")
        assert len(beginner_modules) == 2
    
    def test_add_content_to_module(self, db_session):
        """Test adding content to a module."""
        service = ModuleService(db_session)
        
        module_data = LearningModuleCreate(
            title="Content Module",
            slug="content-module",
            category="ml-basics",
            difficulty_level="beginner"
        )
        module = service.create_module(module_data)
        
        content_data = ModuleContentCreate(
            title="Introduction",
            content_type="text",
            content_body="# Welcome\n\nThis is the introduction.",
            order_index=0
        )
        
        content = service.add_content(module.id, content_data)
        
        assert content is not None
        assert content.title == "Introduction"
        assert content.content_type == "text"


class TestAssessmentService:
    """Test assessment service functionality."""
    
    def test_create_quiz(self, db_session):
        """Test quiz creation."""
        # First create a module
        module_service = ModuleService(db_session)
        module_data = LearningModuleCreate(
            title="Quiz Module",
            slug="quiz-module",
            category="ml-basics",
            difficulty_level="beginner"
        )
        module = module_service.create_module(module_data)
        
        # Create quiz
        assessment_service = AssessmentService(db_session)
        quiz_data = QuizCreate(
            title="Test Quiz",
            description="A test quiz",
            passing_score=70.0,
            max_attempts=3
        )
        
        quiz = assessment_service.create_quiz(module.id, quiz_data)
        
        assert quiz.id is not None
        assert quiz.title == "Test Quiz"
        assert quiz.passing_score == 70.0
    
    def test_add_question(self, db_session):
        """Test adding questions to a quiz."""
        # Setup
        module_service = ModuleService(db_session)
        module = module_service.create_module(LearningModuleCreate(
            title="Q Module",
            slug="q-module",
            category="ml-basics",
            difficulty_level="beginner"
        ))
        
        assessment_service = AssessmentService(db_session)
        quiz = assessment_service.create_quiz(module.id, QuizCreate(
            title="Question Quiz"
        ))
        
        question_data = QuestionCreate(
            question_text="What is 2 + 2?",
            question_type="multiple_choice",
            options=["3", "4", "5", "6"],
            correct_answer=1,
            points=1
        )
        
        question = assessment_service.add_question(quiz.id, question_data)
        
        assert question is not None
        assert question.question_text == "What is 2 + 2?"
        assert question.correct_answer == 1
    
    def test_start_and_submit_assessment(self, db_session):
        """Test starting and submitting an assessment."""
        # Setup user
        user_service = UserService(db_session)
        user = user_service.create_user(UserCreate(
            username="quiztaker",
            email="quiz@example.com",
            password="password123"
        ))
        
        # Setup module and quiz
        module_service = ModuleService(db_session)
        module = module_service.create_module(LearningModuleCreate(
            title="Assessment Module",
            slug="assessment-module",
            category="ml-basics",
            difficulty_level="beginner"
        ))
        
        assessment_service = AssessmentService(db_session)
        quiz = assessment_service.create_quiz(module.id, QuizCreate(
            title="Assessment Quiz",
            passing_score=50.0
        ))
        
        # Add questions
        q1 = assessment_service.add_question(quiz.id, QuestionCreate(
            question_text="Q1?",
            options=["A", "B", "C"],
            correct_answer=0,
            points=1
        ))
        q2 = assessment_service.add_question(quiz.id, QuestionCreate(
            question_text="Q2?",
            options=["X", "Y", "Z"],
            correct_answer=1,
            points=1
        ))
        
        # Start assessment
        assessment = assessment_service.start_assessment(user.id, quiz.id)
        assert assessment is not None
        assert assessment.status == "in_progress"
        
        # Submit answers
        submission = AssessmentSubmission(
            quiz_id=quiz.id,
            answers=[
                AnswerSubmission(question_id=q1.id, answer=0),  # Correct
                AnswerSubmission(question_id=q2.id, answer=2)   # Wrong
            ]
        )
        
        result = assessment_service.submit_assessment(assessment.id, submission)
        
        assert result is not None
        assert result.status == "completed"
        assert result.score == 50.0  # 1 out of 2 correct
        assert result.is_passed == True  # 50% >= 50% passing


class TestAdaptiveLearningService:
    """Test adaptive learning service."""
    
    def test_analyze_performance_no_data(self, db_session):
        """Test analyzing performance with no assessment data."""
        user_service = UserService(db_session)
        user = user_service.create_user(UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123"
        ))
        
        adaptive_service = AdaptiveLearningService(db_session)
        feedback = adaptive_service.analyze_performance(user.id)
        
        assert feedback.overall_performance == "needs_improvement"
        assert len(feedback.recommended_modules) == 0
    
    def test_suggest_next_module(self, db_session):
        """Test module suggestion."""
        # Create user
        user_service = UserService(db_session)
        user = user_service.create_user(UserCreate(
            username="moduleuser",
            email="module@example.com",
            password="password123",
            skill_level="beginner"
        ))
        
        # Create module
        module_service = ModuleService(db_session)
        module = module_service.create_module(LearningModuleCreate(
            title="Suggested Module",
            slug="suggested-module",
            category="ml-basics",
            difficulty_level="beginner"
        ))
        module_service.publish_module(module.id)
        
        adaptive_service = AdaptiveLearningService(db_session)
        next_module = adaptive_service.suggest_next_module(user.id)
        
        assert next_module == "suggested-module"


class TestMLUtilities:
    """Test ML utility functions."""
    
    def test_get_available_libraries(self):
        """Test library availability check."""
        from learning_platform.utils.ml_utilities import MLUtilities
        
        libraries = MLUtilities.get_available_libraries()
        
        assert "scikit-learn" in libraries
        assert "tensorflow" in libraries
        assert "pytorch" in libraries
    
    def test_validate_data_shape(self):
        """Test data shape validation."""
        from learning_platform.utils.ml_utilities import MLUtilities
        
        data = [[1, 2, 3], [4, 5, 6]]
        result = MLUtilities.validate_data_shape(data)
        
        assert result["is_valid"] == True
        assert result["shape"] == (2, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
