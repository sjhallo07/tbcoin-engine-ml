"""Sample content data for initializing the learning platform."""

BEGINNER_MODULES = [
    {
        "title": "Scikit-Learn Basics",
        "slug": "scikit-learn-basics",
        "description": "Introduction to machine learning with Scikit-Learn. Learn the fundamentals of ML pipelines, data preprocessing, and model training.",
        "category": "ml-basics",
        "difficulty_level": "beginner",
        "library": "scikit-learn",
        "prerequisites": [],
        "estimated_duration_minutes": 90,
        "topics": ["machine learning", "scikit-learn", "data preprocessing", "model training"],
        "learning_objectives": [
            "Understand the Scikit-Learn API structure",
            "Learn to preprocess data for ML",
            "Train your first ML model",
            "Evaluate model performance"
        ],
        "order_index": 1
    },
    {
        "title": "Linear Regression",
        "slug": "linear-regression",
        "description": "Master the fundamentals of linear regression, from simple to multiple regression analysis.",
        "category": "supervised-learning",
        "difficulty_level": "beginner",
        "library": "scikit-learn",
        "prerequisites": ["scikit-learn-basics"],
        "estimated_duration_minutes": 75,
        "topics": ["regression", "linear models", "gradient descent", "least squares"],
        "learning_objectives": [
            "Understand the mathematics behind linear regression",
            "Implement simple and multiple linear regression",
            "Interpret regression coefficients",
            "Handle common regression problems"
        ],
        "order_index": 2
    },
    {
        "title": "Decision Trees",
        "slug": "decision-trees",
        "description": "Learn classification and regression with decision trees. Understand tree-based algorithms and their applications.",
        "category": "supervised-learning",
        "difficulty_level": "beginner",
        "library": "scikit-learn",
        "prerequisites": ["scikit-learn-basics"],
        "estimated_duration_minutes": 60,
        "topics": ["decision trees", "classification", "entropy", "information gain"],
        "learning_objectives": [
            "Understand how decision trees work",
            "Build classification and regression trees",
            "Prevent overfitting with pruning",
            "Visualize and interpret tree structures"
        ],
        "order_index": 3
    }
]

INTERMEDIATE_MODULES = [
    {
        "title": "TensorFlow Introduction",
        "slug": "tensorflow-intro",
        "description": "Get started with TensorFlow for deep learning. Build and train neural networks using Keras.",
        "category": "deep-learning",
        "difficulty_level": "intermediate",
        "library": "tensorflow",
        "prerequisites": ["scikit-learn-basics", "linear-regression"],
        "estimated_duration_minutes": 120,
        "topics": ["tensorflow", "keras", "neural networks", "deep learning"],
        "learning_objectives": [
            "Understand TensorFlow and Keras architecture",
            "Build sequential and functional models",
            "Train deep neural networks",
            "Use callbacks for training optimization"
        ],
        "order_index": 4
    },
    {
        "title": "PyTorch Fundamentals",
        "slug": "pytorch-fundamentals",
        "description": "Learn deep learning with PyTorch. Master tensors, autograd, and neural network construction.",
        "category": "deep-learning",
        "difficulty_level": "intermediate",
        "library": "pytorch",
        "prerequisites": ["scikit-learn-basics"],
        "estimated_duration_minutes": 120,
        "topics": ["pytorch", "tensors", "autograd", "neural networks"],
        "learning_objectives": [
            "Work with PyTorch tensors",
            "Understand automatic differentiation",
            "Build custom neural networks",
            "Implement training loops"
        ],
        "order_index": 5
    },
    {
        "title": "Overfitting vs Underfitting",
        "slug": "overfitting-underfitting",
        "description": "Master the concepts of model complexity, bias-variance tradeoff, and regularization techniques.",
        "category": "ml-fundamentals",
        "difficulty_level": "intermediate",
        "library": "general",
        "prerequisites": ["linear-regression", "decision-trees"],
        "estimated_duration_minutes": 90,
        "topics": ["overfitting", "underfitting", "regularization", "cross-validation"],
        "learning_objectives": [
            "Understand bias-variance tradeoff",
            "Identify overfitting and underfitting",
            "Apply regularization techniques",
            "Use cross-validation effectively"
        ],
        "order_index": 6
    }
]

ADVANCED_MODULES = [
    {
        "title": "Ensemble Learning",
        "slug": "ensemble-learning",
        "description": "Master ensemble methods including bagging, boosting, and stacking with XGBoost and LightGBM.",
        "category": "ensemble-methods",
        "difficulty_level": "advanced",
        "library": "xgboost",
        "prerequisites": ["decision-trees", "overfitting-underfitting"],
        "estimated_duration_minutes": 150,
        "topics": ["ensemble methods", "bagging", "boosting", "xgboost", "lightgbm"],
        "learning_objectives": [
            "Understand ensemble learning principles",
            "Implement bagging and boosting algorithms",
            "Master XGBoost and LightGBM",
            "Combine models with stacking"
        ],
        "order_index": 7
    },
    {
        "title": "Hyperparameter Tuning",
        "slug": "hyperparameter-tuning",
        "description": "Learn advanced techniques for optimizing model hyperparameters using grid search, random search, and Bayesian optimization.",
        "category": "ml-optimization",
        "difficulty_level": "advanced",
        "library": "scikit-learn",
        "prerequisites": ["ensemble-learning"],
        "estimated_duration_minutes": 120,
        "topics": ["hyperparameter tuning", "grid search", "random search", "bayesian optimization"],
        "learning_objectives": [
            "Understand hyperparameter optimization",
            "Implement grid and random search",
            "Use Bayesian optimization techniques",
            "Build automated ML pipelines"
        ],
        "order_index": 8
    },
    {
        "title": "Reinforcement Learning",
        "slug": "reinforcement-learning",
        "description": "Explore reinforcement learning algorithms including Q-Learning, Policy Gradients, and Deep RL.",
        "category": "reinforcement-learning",
        "difficulty_level": "advanced",
        "library": "stable-baselines3",
        "prerequisites": ["tensorflow-intro", "pytorch-fundamentals"],
        "estimated_duration_minutes": 180,
        "topics": ["reinforcement learning", "q-learning", "policy gradients", "deep rl"],
        "learning_objectives": [
            "Understand RL fundamentals and MDPs",
            "Implement Q-Learning algorithms",
            "Apply policy gradient methods",
            "Use Deep RL with Stable Baselines3"
        ],
        "order_index": 9
    }
]

ALL_MODULES = BEGINNER_MODULES + INTERMEDIATE_MODULES + ADVANCED_MODULES


SAMPLE_QUIZZES = {
    "scikit-learn-basics": {
        "title": "Scikit-Learn Basics Quiz",
        "description": "Test your understanding of Scikit-Learn fundamentals.",
        "passing_score": 70.0,
        "questions": [
            {
                "question_text": "What is the standard method for training a model in Scikit-Learn?",
                "question_type": "multiple_choice",
                "options": ["train()", "fit()", "learn()", "build()"],
                "correct_answer": 1,
                "explanation": "The fit() method is the standard way to train models in Scikit-Learn.",
                "points": 1
            },
            {
                "question_text": "Which of the following is NOT a preprocessing step?",
                "question_type": "multiple_choice",
                "options": ["Normalization", "One-hot encoding", "Model evaluation", "Feature scaling"],
                "correct_answer": 2,
                "explanation": "Model evaluation is not a preprocessing step; it comes after training.",
                "points": 1
            },
            {
                "question_text": "Scikit-Learn uses the fit/transform pattern for data preprocessing.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": True,
                "explanation": "Scikit-Learn transformers use fit() to learn parameters and transform() to apply them.",
                "points": 1
            }
        ]
    },
    "linear-regression": {
        "title": "Linear Regression Assessment",
        "description": "Evaluate your understanding of linear regression concepts.",
        "passing_score": 70.0,
        "questions": [
            {
                "question_text": "What does the coefficient (slope) in linear regression represent?",
                "question_type": "multiple_choice",
                "options": [
                    "The y-intercept",
                    "The change in y for a one-unit change in x",
                    "The variance of the data",
                    "The correlation coefficient"
                ],
                "correct_answer": 1,
                "explanation": "The slope represents how much y changes for each unit increase in x.",
                "points": 2
            },
            {
                "question_text": "Which metric is commonly used to evaluate linear regression models?",
                "question_type": "multiple_choice",
                "options": ["Accuracy", "F1 Score", "R-squared (R²)", "Precision"],
                "correct_answer": 2,
                "explanation": "R-squared measures how well the regression line fits the data.",
                "points": 1
            }
        ]
    },
    "decision-trees": {
        "title": "Decision Trees Quiz",
        "description": "Test your knowledge of decision tree algorithms.",
        "passing_score": 70.0,
        "questions": [
            {
                "question_text": "What is the main measure used to split nodes in a classification tree?",
                "question_type": "multiple_choice",
                "options": ["Mean squared error", "Information gain", "R-squared", "Correlation"],
                "correct_answer": 1,
                "explanation": "Information gain (or Gini impurity) is used to determine the best splits.",
                "points": 1
            },
            {
                "question_text": "Pruning helps prevent overfitting in decision trees.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": True,
                "explanation": "Pruning reduces tree complexity to prevent overfitting.",
                "points": 1
            }
        ]
    }
}


def get_all_sample_content():
    """Get all sample content for initialization."""
    return {
        "modules": ALL_MODULES,
        "quizzes": SAMPLE_QUIZZES
    }
