# AI Learning Platform for Python Machine Learning

A comprehensive backend system for AI learning modules focused on Python Machine Learning. This platform provides structured learning paths with Scikit-Learn, TensorFlow, PyTorch, XGBoost, LightGBM, and advanced topics like Ensemble Learning and Reinforcement Learning.

## Features

### 1. Backend Architecture
- Modular backend architecture using Python and FastAPI
- RESTful API design principles for communication between components
- Microservices approach for each learning module

### 2. Database Design
- Relational database schema to store:
  - User profiles (username, email, progress tracking)
  - Learning modules (title, description, library, prerequisites)
  - Assessment data (quiz scores, completion status)
- Proper indexing for fast retrieval of learning content

### 3. Module Organization
Structured learning modules by topic and complexity:

**Beginner:**
- Scikit-Learn Basics
- Linear Regression
- Decision Trees

**Intermediate:**
- TensorFlow Introduction
- PyTorch Fundamentals
- Overfitting vs Underfitting

**Advanced:**
- Ensemble Learning (XGBoost, LightGBM)
- Hyperparameter Tuning
- Reinforcement Learning

### 4. Content Delivery
- Text, videos, and interactive quizzes support
- Markdown/HTML formatting for learning materials
- Version control for module updates and revisions

### 5. User Interaction
- Module selection and progress tracking
- Authentication and authorization
- Personalized learning recommendations

### 6. Assessment and Feedback
- Quizzes with multiple question types
- Adaptive learning based on user performance
- Detailed feedback and learning suggestions

### 7. Integration with ML Libraries
Utility functions for:
- Scikit-Learn for classical ML
- TensorFlow for deep learning
- PyTorch for deep learning
- XGBoost and LightGBM for gradient boosting

## Installation

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic pyjwt

# Initialize the database
python -c "from learning_platform.models.base import init_db; init_db()"
```

## API Endpoints

### Users
- `POST /learning/users/register` - Register a new user
- `POST /learning/users/login` - Authenticate and get token
- `GET /learning/users/me` - Get current user profile
- `PUT /learning/users/me` - Update user profile
- `GET /learning/users/me/progress` - Get learning progress

### Modules
- `GET /learning/modules/` - List all modules
- `GET /learning/modules/by-difficulty/{level}` - Filter by difficulty
- `GET /learning/modules/by-library/{library}` - Filter by ML library
- `GET /learning/modules/{slug}` - Get module details
- `GET /learning/modules/{slug}/contents` - Get module content
- `GET /learning/modules/recommended` - Get personalized recommendations

### Assessments
- `GET /learning/assessments/module/{slug}/quizzes` - Get quizzes for module
- `POST /learning/assessments/quiz/{id}/start` - Start a quiz
- `POST /learning/assessments/submit` - Submit quiz answers
- `GET /learning/assessments/my-results` - Get assessment history
- `GET /learning/assessments/adaptive-feedback` - Get personalized feedback

### Progress
- `POST /learning/progress/module/{slug}/update` - Update module progress
- `GET /learning/progress/module/{slug}` - Get specific module progress
- `GET /learning/progress/next-module` - Get next recommended module
- `GET /learning/progress/skill-progression` - Get skill progression data
- `POST /learning/progress/level-up` - Request skill level upgrade

## Project Structure

```
learning_platform/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Database and auth dependencies
│   ├── router.py             # Main API router
│   └── endpoints/
│       ├── users.py          # User endpoints
│       ├── modules.py        # Module endpoints
│       ├── assessments.py    # Quiz endpoints
│       └── progress.py       # Progress endpoints
├── models/
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy base
│   ├── user.py               # User models
│   ├── module.py             # Learning module models
│   ├── assessment.py         # Quiz and assessment models
│   └── learning_schema.sql   # Database schema
├── schemas/
│   ├── __init__.py
│   ├── user.py               # User Pydantic schemas
│   ├── module.py             # Module schemas
│   └── assessment.py         # Assessment schemas
├── services/
│   ├── __init__.py
│   ├── user_service.py       # User operations
│   ├── module_service.py     # Module operations
│   ├── assessment_service.py # Assessment operations
│   └── adaptive_learning_service.py  # ML-based recommendations
├── utils/
│   ├── __init__.py
│   ├── ml_utilities.py       # Base ML utilities
│   ├── sklearn_utils.py      # Scikit-Learn utilities
│   ├── tensorflow_utils.py   # TensorFlow utilities
│   ├── pytorch_utils.py      # PyTorch utilities
│   └── xgboost_utils.py      # XGBoost/LightGBM utilities
├── content/
│   ├── __init__.py
│   └── sample_data.py        # Sample module content
└── tests/
    ├── __init__.py
    └── test_learning_platform.py  # Unit tests
```

## Running the Application

```python
# Add learning platform router to main FastAPI app
from fastapi import FastAPI
from learning_platform.api import router as learning_router

app = FastAPI()
app.include_router(learning_router)

# Run with uvicorn
# uvicorn main:app --reload
```

## Testing

```bash
# Run all tests
pytest learning_platform/tests/ -v

# Run with coverage
pytest learning_platform/tests/ --cov=learning_platform
```

## ML Library Utilities

The platform includes utility functions for working with ML libraries:

```python
from learning_platform.utils import (
    MLUtilities,
    SklearnUtilities,
    TensorFlowUtilities,
    PyTorchUtilities,
    XGBoostUtilities
)

# Check available libraries
MLUtilities.get_available_libraries()

# Create a Scikit-Learn model
model = SklearnUtilities.create_model("RandomForestClassifier")

# Get example code
print(SklearnUtilities.example_linear_regression())
```

## Adaptive Learning

The platform includes adaptive learning features:

1. **Performance Analysis**: Analyzes quiz results to identify strengths and weaknesses
2. **Personalized Recommendations**: Suggests modules based on user's skill level and progress
3. **Skill Progression**: Tracks improvement over time
4. **Level Upgrades**: Automatically suggests level upgrades based on performance

## License

MIT License
