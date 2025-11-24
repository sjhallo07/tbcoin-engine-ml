"""Scikit-Learn utilities for learning platform."""
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SklearnUtilities:
    """Utilities for Scikit-Learn operations."""
    
    @staticmethod
    def get_available_models() -> Dict[str, List[str]]:
        """Get available Scikit-Learn models by category."""
        return {
            "classification": [
                "LogisticRegression",
                "DecisionTreeClassifier",
                "RandomForestClassifier",
                "GradientBoostingClassifier",
                "SVC",
                "KNeighborsClassifier"
            ],
            "regression": [
                "LinearRegression",
                "Ridge",
                "Lasso",
                "ElasticNet",
                "DecisionTreeRegressor",
                "RandomForestRegressor",
                "GradientBoostingRegressor",
                "SVR"
            ],
            "clustering": [
                "KMeans",
                "DBSCAN",
                "AgglomerativeClustering",
                "GaussianMixture"
            ],
            "dimensionality_reduction": [
                "PCA",
                "TSNE",
                "TruncatedSVD"
            ]
        }
    
    @staticmethod
    def create_model(model_type: str, **kwargs) -> Any:
        """Create a Scikit-Learn model instance."""
        try:
            from sklearn.linear_model import (
                LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet
            )
            from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
            from sklearn.ensemble import (
                RandomForestClassifier, RandomForestRegressor,
                GradientBoostingClassifier, GradientBoostingRegressor
            )
            from sklearn.svm import SVC, SVR
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
            from sklearn.mixture import GaussianMixture
            from sklearn.decomposition import PCA, TruncatedSVD
            
            models = {
                "LogisticRegression": LogisticRegression,
                "LinearRegression": LinearRegression,
                "Ridge": Ridge,
                "Lasso": Lasso,
                "ElasticNet": ElasticNet,
                "DecisionTreeClassifier": DecisionTreeClassifier,
                "DecisionTreeRegressor": DecisionTreeRegressor,
                "RandomForestClassifier": RandomForestClassifier,
                "RandomForestRegressor": RandomForestRegressor,
                "GradientBoostingClassifier": GradientBoostingClassifier,
                "GradientBoostingRegressor": GradientBoostingRegressor,
                "SVC": SVC,
                "SVR": SVR,
                "KNeighborsClassifier": KNeighborsClassifier,
                "KMeans": KMeans,
                "DBSCAN": DBSCAN,
                "AgglomerativeClustering": AgglomerativeClustering,
                "GaussianMixture": GaussianMixture,
                "PCA": PCA,
                "TruncatedSVD": TruncatedSVD,
            }
            
            if model_type not in models:
                raise ValueError(f"Unknown model type: {model_type}")
            
            return models[model_type](**kwargs)
        except ImportError:
            raise ImportError("scikit-learn is required")
    
    @staticmethod
    def train_model(model: Any, X_train: Any, y_train: Any) -> Any:
        """Train a Scikit-Learn model."""
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def evaluate_model(model: Any, X_test: Any, y_test: Any, task: str = "classification") -> Dict[str, float]:
        """Evaluate a trained model."""
        from learning_platform.utils.ml_utilities import MLUtilities
        
        y_pred = model.predict(X_test)
        return MLUtilities.calculate_metrics(y_test, y_pred, task)
    
    @staticmethod
    def cross_validate(model: Any, X: Any, y: Any, cv: int = 5) -> Dict[str, Any]:
        """Perform cross-validation."""
        try:
            from sklearn.model_selection import cross_val_score
            import numpy as np
            
            scores = cross_val_score(model, X, y, cv=cv)
            return {
                "mean_score": float(np.mean(scores)),
                "std_score": float(np.std(scores)),
                "scores": scores.tolist()
            }
        except ImportError:
            raise ImportError("scikit-learn is required")
    
    @staticmethod
    def grid_search(model: Any, X: Any, y: Any, param_grid: Dict, cv: int = 5) -> Dict[str, Any]:
        """Perform grid search for hyperparameter tuning."""
        try:
            from sklearn.model_selection import GridSearchCV
            
            grid_search = GridSearchCV(model, param_grid, cv=cv, scoring='accuracy')
            grid_search.fit(X, y)
            
            return {
                "best_params": grid_search.best_params_,
                "best_score": float(grid_search.best_score_),
                "best_estimator": grid_search.best_estimator_
            }
        except ImportError:
            raise ImportError("scikit-learn is required")
    
    @staticmethod
    def get_feature_importance(model: Any, feature_names: Optional[List[str]] = None) -> Dict[str, float]:
        """Get feature importances from a tree-based model."""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                if feature_names is None:
                    feature_names = [f"feature_{i}" for i in range(len(importances))]
                return dict(zip(feature_names, importances.tolist()))
            elif hasattr(model, 'coef_'):
                coefs = model.coef_.flatten()
                if feature_names is None:
                    feature_names = [f"feature_{i}" for i in range(len(coefs))]
                return dict(zip(feature_names, coefs.tolist()))
            else:
                return {"error": "Model does not have feature importances"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def example_linear_regression() -> str:
        """Return example code for linear regression."""
        return '''
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Generate sample data
X = np.random.randn(100, 3)
y = 2 * X[:, 0] + 3 * X[:, 1] - X[:, 2] + np.random.randn(100) * 0.5

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Coefficients: {model.coef_}")
print(f"MSE: {mse:.4f}")
print(f"R2 Score: {r2:.4f}")
'''
    
    @staticmethod
    def example_decision_tree() -> str:
        """Return example code for decision tree."""
        return '''
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import load_iris

# Load data
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train model
model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# Feature importance
for name, importance in zip(iris.feature_names, model.feature_importances_):
    print(f"{name}: {importance:.4f}")
'''
