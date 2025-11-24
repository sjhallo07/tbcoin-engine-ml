"""Adaptive learning service for personalized recommendations."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from learning_platform.models.user import User, UserProgress
from learning_platform.models.assessment import UserAssessment, Quiz
from learning_platform.models.module import LearningModule
from learning_platform.schemas.assessment import AdaptiveLearningFeedback


class AdaptiveLearningService:
    """Service for adaptive learning and personalized recommendations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_performance(self, user_id: int) -> AdaptiveLearningFeedback:
        """Analyze user's performance and generate adaptive feedback."""
        # Get user's assessments
        assessments = self.db.query(UserAssessment).filter(
            UserAssessment.user_id == user_id,
            UserAssessment.status == "completed"
        ).all()
        
        if not assessments:
            return AdaptiveLearningFeedback(
                overall_performance="needs_improvement",
                strength_areas=[],
                weak_areas=[],
                recommended_modules=[],
                suggested_review_topics=[],
                personalized_message="Welcome! Start your first module to begin learning."
            )
        
        # Calculate overall performance
        scores = [a.score for a in assessments if a.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 90:
            performance = "excellent"
            message = "Outstanding performance! You're mastering the material quickly."
        elif avg_score >= 75:
            performance = "good"
            message = "Great job! You have a solid understanding of the concepts."
        elif avg_score >= 60:
            performance = "needs_improvement"
            message = "You're making progress. Focus on the weak areas to improve."
        else:
            performance = "struggling"
            message = "Consider reviewing the fundamentals and practicing more."
        
        # Analyze strength and weak areas by module category
        module_scores = {}
        for assessment in assessments:
            quiz = self.db.query(Quiz).filter(Quiz.id == assessment.quiz_id).first()
            if quiz:
                module = self.db.query(LearningModule).filter(
                    LearningModule.id == quiz.module_id
                ).first()
                if module:
                    category = module.category
                    if category not in module_scores:
                        module_scores[category] = []
                    module_scores[category].append(assessment.score or 0)
        
        strengths = []
        weaknesses = []
        
        for category, cat_scores in module_scores.items():
            avg = sum(cat_scores) / len(cat_scores)
            if avg >= 80:
                strengths.append(category)
            elif avg < 60:
                weaknesses.append(category)
        
        # Get recommended modules
        recommended = self._get_recommendations(user_id, weaknesses)
        
        # Suggested review topics based on weak areas
        review_topics = self._get_review_topics(weaknesses)
        
        return AdaptiveLearningFeedback(
            overall_performance=performance,
            strength_areas=strengths,
            weak_areas=weaknesses,
            recommended_modules=recommended,
            suggested_review_topics=review_topics,
            personalized_message=message
        )
    
    def _get_recommendations(self, user_id: int, weak_areas: List[str]) -> List[str]:
        """Get module recommendations based on weak areas."""
        recommendations = []
        
        # Get modules in weak areas that haven't been completed
        completed = self.db.query(UserProgress.module_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True
        ).all()
        completed_ids = [c[0] for c in completed]
        
        for category in weak_areas:
            modules = self.db.query(LearningModule).filter(
                LearningModule.category == category,
                LearningModule.is_published == True,
                ~LearningModule.id.in_(completed_ids) if completed_ids else True
            ).limit(2).all()
            
            recommendations.extend([m.title for m in modules])
        
        # Add general recommendations if not enough
        if len(recommendations) < 3:
            user = self.db.query(User).filter(User.id == user_id).first()
            skill_level = user.skill_level if user else "beginner"
            
            general = self.db.query(LearningModule).filter(
                LearningModule.difficulty_level == skill_level,
                LearningModule.is_published == True,
                ~LearningModule.id.in_(completed_ids) if completed_ids else True
            ).limit(3 - len(recommendations)).all()
            
            recommendations.extend([m.title for m in general])
        
        return recommendations[:5]
    
    def _get_review_topics(self, weak_areas: List[str]) -> List[str]:
        """Get suggested review topics based on weak areas."""
        topic_map = {
            "ml-basics": ["Linear Algebra fundamentals", "Statistics basics", "Data preprocessing"],
            "supervised-learning": ["Regression concepts", "Classification algorithms", "Model evaluation"],
            "deep-learning": ["Neural network architecture", "Backpropagation", "Activation functions"],
            "reinforcement-learning": ["Markov Decision Process", "Q-Learning", "Policy gradients"],
            "ensemble-methods": ["Bagging vs Boosting", "Random Forests", "Gradient Boosting"],
        }
        
        topics = []
        for area in weak_areas:
            if area in topic_map:
                topics.extend(topic_map[area][:2])
        
        return topics[:5]
    
    def suggest_next_module(self, user_id: int) -> Optional[str]:
        """Suggest the next module for a user based on their progress."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get completed modules
        completed = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True
        ).all()
        completed_ids = [p.module_id for p in completed]
        
        # Get in-progress modules first
        in_progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == False,
            UserProgress.completion_percentage > 0
        ).first()
        
        if in_progress:
            module = self.db.query(LearningModule).filter(
                LearningModule.id == in_progress.module_id
            ).first()
            if module:
                return module.slug
        
        # Find next module at user's level
        next_module = self.db.query(LearningModule).filter(
            LearningModule.difficulty_level == user.skill_level,
            LearningModule.is_published == True,
            ~LearningModule.id.in_(completed_ids) if completed_ids else True
        ).order_by(LearningModule.order_index).first()
        
        if next_module:
            return next_module.slug
        
        # Suggest moving to next level
        level_order = {"beginner": "intermediate", "intermediate": "advanced"}
        next_level = level_order.get(user.skill_level)
        
        if next_level:
            next_module = self.db.query(LearningModule).filter(
                LearningModule.difficulty_level == next_level,
                LearningModule.is_published == True,
                ~LearningModule.id.in_(completed_ids) if completed_ids else True
            ).order_by(LearningModule.order_index).first()
            
            if next_module:
                return next_module.slug
        
        return None
    
    def calculate_skill_progression(self, user_id: int) -> Dict[str, Any]:
        """Calculate user's skill progression over time."""
        progress_records = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).order_by(UserProgress.started_at).all()
        
        assessments = self.db.query(UserAssessment).filter(
            UserAssessment.user_id == user_id,
            UserAssessment.status == "completed"
        ).order_by(UserAssessment.completed_at).all()
        
        # Track score progression
        score_history = []
        for a in assessments:
            if a.score is not None and a.completed_at:
                score_history.append({
                    "date": a.completed_at.isoformat(),
                    "score": a.score
                })
        
        # Calculate completion rate
        total_modules = self.db.query(LearningModule).filter(
            LearningModule.is_published == True
        ).count()
        
        completed_modules = len([p for p in progress_records if p.is_completed])
        completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        # Determine suggested level upgrade
        user = self.db.query(User).filter(User.id == user_id).first()
        current_level = user.skill_level if user else "beginner"
        
        recent_scores = [a.score for a in assessments[-5:] if a.score is not None]
        avg_recent = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        should_upgrade = avg_recent >= 85 and completed_modules >= 3
        
        return {
            "current_level": current_level,
            "completion_rate": completion_rate,
            "total_modules_completed": completed_modules,
            "total_modules_available": total_modules,
            "score_history": score_history,
            "average_recent_score": avg_recent,
            "ready_for_level_upgrade": should_upgrade
        }
