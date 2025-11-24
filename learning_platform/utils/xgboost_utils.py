"""XGBoost and LightGBM utilities for learning platform."""
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class XGBoostUtilities:
    """Utilities for XGBoost and LightGBM operations."""
    
    @staticmethod
    def is_xgboost_available() -> bool:
        """Check if XGBoost is available."""
        try:
            import xgboost
            return True
        except ImportError:
            return False
    
    @staticmethod
    def is_lightgbm_available() -> bool:
        """Check if LightGBM is available."""
        try:
            import lightgbm
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_versions() -> Dict[str, Optional[str]]:
        """Get XGBoost and LightGBM versions."""
        versions = {}
        
        try:
            import xgboost
            versions["xgboost"] = xgboost.__version__
        except ImportError:
            versions["xgboost"] = None
        
        try:
            import lightgbm
            versions["lightgbm"] = lightgbm.__version__
        except ImportError:
            versions["lightgbm"] = None
        
        return versions
    
    @staticmethod
    def create_xgboost_model(
        task: str = "classification",
        **kwargs
    ) -> Any:
        """Create an XGBoost model."""
        try:
            import xgboost as xgb
            
            default_params = {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42,
            }
            default_params.update(kwargs)
            
            if task == "classification":
                return xgb.XGBClassifier(**default_params)
            elif task == "regression":
                return xgb.XGBRegressor(**default_params)
            else:
                raise ValueError(f"Unknown task: {task}")
        except ImportError:
            raise ImportError("XGBoost is required")
    
    @staticmethod
    def create_lightgbm_model(
        task: str = "classification",
        **kwargs
    ) -> Any:
        """Create a LightGBM model."""
        try:
            import lightgbm as lgb
            
            default_params = {
                "n_estimators": 100,
                "max_depth": -1,
                "learning_rate": 0.1,
                "random_state": 42,
                "verbose": -1,
            }
            default_params.update(kwargs)
            
            if task == "classification":
                return lgb.LGBMClassifier(**default_params)
            elif task == "regression":
                return lgb.LGBMRegressor(**default_params)
            else:
                raise ValueError(f"Unknown task: {task}")
        except ImportError:
            raise ImportError("LightGBM is required")
    
    @staticmethod
    def train_with_early_stopping(
        model: Any,
        X_train: Any,
        y_train: Any,
        X_val: Any,
        y_val: Any,
        early_stopping_rounds: int = 10
    ) -> Any:
        """Train model with early stopping."""
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        return model
    
    @staticmethod
    def get_feature_importance(model: Any, feature_names: Optional[List[str]] = None) -> Dict[str, float]:
        """Get feature importance from model."""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                if feature_names is None:
                    feature_names = [f"feature_{i}" for i in range(len(importances))]
                return dict(zip(feature_names, importances.tolist()))
            return {"error": "Model does not have feature importances"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def cross_validate_xgboost(
        X: Any,
        y: Any,
        params: Optional[Dict] = None,
        num_boost_round: int = 100,
        nfold: int = 5,
        early_stopping_rounds: int = 10
    ) -> Dict[str, Any]:
        """Perform cross-validation with XGBoost."""
        try:
            import xgboost as xgb
            import numpy as np
            
            if params is None:
                params = {
                    "objective": "binary:logistic",
                    "eval_metric": "logloss",
                    "max_depth": 6,
                    "learning_rate": 0.1,
                }
            
            dtrain = xgb.DMatrix(X, label=y)
            
            cv_results = xgb.cv(
                params,
                dtrain,
                num_boost_round=num_boost_round,
                nfold=nfold,
                early_stopping_rounds=early_stopping_rounds,
                verbose_eval=False
            )
            
            return {
                "best_iteration": len(cv_results),
                "best_score": float(cv_results.iloc[-1, 0]),
                "std": float(cv_results.iloc[-1, 1]),
                "results": cv_results.to_dict()
            }
        except ImportError:
            raise ImportError("XGBoost is required")
    
    @staticmethod
    def example_xgboost_classification() -> str:
        """Return example code for XGBoost classification."""
        return '''
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import load_breast_cancer
import numpy as np

# Load data
data = load_breast_cancer()
X, y = data.data, data.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train XGBoost model
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

# Train with validation set
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

# Predictions
y_pred = model.predict(X_test)

# Evaluate
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))

# Feature importance
importance = model.feature_importances_
indices = np.argsort(importance)[::-1][:10]
print("\\nTop 10 Feature Importances:")
for i in indices:
    print(f"{data.feature_names[i]}: {importance[i]:.4f}")
'''
    
    @staticmethod
    def example_lightgbm_regression() -> str:
        """Return example code for LightGBM regression."""
        return '''
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import load_diabetes
import numpy as np

# Load data
data = load_diabetes()
X, y = data.data, data.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create LightGBM dataset
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

# Parameters
params = {
    'objective': 'regression',
    'metric': 'mse',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1
}

# Train model
model = lgb.train(
    params,
    train_data,
    num_boost_round=100,
    valid_sets=[valid_data],
    callbacks=[lgb.early_stopping(10)]
)

# Predictions
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2 Score: {r2:.4f}")

# Feature importance
importance = model.feature_importance()
print("\\nFeature Importances:")
for name, imp in sorted(zip(data.feature_names, importance), key=lambda x: -x[1]):
    print(f"{name}: {imp}")
'''
    
    @staticmethod
    def example_ensemble_comparison() -> str:
        """Return example comparing ensemble methods."""
        return '''
import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_breast_cancer
import numpy as np

# Load data
data = load_breast_cancer()
X, y = data.data, data.target

# Define models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'XGBoost': xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss'),
    'LightGBM': lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
}

# Compare with cross-validation
print("Model Comparison (5-fold CV Accuracy):")
print("-" * 40)

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"{name}: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
'''
