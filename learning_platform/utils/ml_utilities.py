"""Base ML utilities and common functions."""
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MLUtilities:
    """Base utilities for machine learning operations."""
    
    @staticmethod
    def get_available_libraries() -> Dict[str, bool]:
        """Check which ML libraries are available."""
        libraries = {}
        
        try:
            import sklearn
            libraries["scikit-learn"] = True
            libraries["sklearn_version"] = sklearn.__version__
        except ImportError:
            libraries["scikit-learn"] = False
        
        try:
            import tensorflow
            libraries["tensorflow"] = True
            libraries["tensorflow_version"] = tensorflow.__version__
        except ImportError:
            libraries["tensorflow"] = False
        
        try:
            import torch
            libraries["pytorch"] = True
            libraries["pytorch_version"] = torch.__version__
        except ImportError:
            libraries["pytorch"] = False
        
        try:
            import xgboost
            libraries["xgboost"] = True
            libraries["xgboost_version"] = xgboost.__version__
        except ImportError:
            libraries["xgboost"] = False
        
        try:
            import lightgbm
            libraries["lightgbm"] = True
            libraries["lightgbm_version"] = lightgbm.__version__
        except ImportError:
            libraries["lightgbm"] = False
        
        return libraries
    
    @staticmethod
    def validate_data_shape(data: Any, expected_shape: Optional[Tuple] = None) -> Dict[str, Any]:
        """Validate data shape and return info."""
        try:
            import numpy as np
            
            if isinstance(data, list):
                data = np.array(data)
            
            result = {
                "shape": data.shape if hasattr(data, "shape") else None,
                "dtype": str(data.dtype) if hasattr(data, "dtype") else type(data).__name__,
                "size": data.size if hasattr(data, "size") else len(data) if hasattr(data, "__len__") else 1,
                "is_valid": True,
                "error": None
            }
            
            if expected_shape and result["shape"] != expected_shape:
                result["is_valid"] = False
                result["error"] = f"Expected shape {expected_shape}, got {result['shape']}"
            
            return result
        except Exception as e:
            return {
                "shape": None,
                "dtype": None,
                "size": None,
                "is_valid": False,
                "error": str(e)
            }
    
    @staticmethod
    def calculate_metrics(y_true: List, y_pred: List, task: str = "classification") -> Dict[str, float]:
        """Calculate common ML metrics."""
        try:
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                mean_squared_error, mean_absolute_error, r2_score
            )
            import numpy as np
            
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)
            
            if task == "classification":
                return {
                    "accuracy": accuracy_score(y_true, y_pred),
                    "precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
                    "recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
                    "f1_score": f1_score(y_true, y_pred, average="weighted", zero_division=0)
                }
            elif task == "regression":
                return {
                    "mse": mean_squared_error(y_true, y_pred),
                    "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
                    "mae": mean_absolute_error(y_true, y_pred),
                    "r2": r2_score(y_true, y_pred)
                }
            else:
                return {"error": f"Unknown task type: {task}"}
        except ImportError:
            return {"error": "scikit-learn not available"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def split_data(X: Any, y: Any, test_size: float = 0.2, random_state: int = 42) -> Tuple:
        """Split data into train and test sets."""
        try:
            from sklearn.model_selection import train_test_split
            return train_test_split(X, y, test_size=test_size, random_state=random_state)
        except ImportError:
            raise ImportError("scikit-learn is required for data splitting")
    
    @staticmethod
    def normalize_data(data: Any, method: str = "standard") -> Tuple[Any, Any]:
        """Normalize data using specified method."""
        try:
            from sklearn.preprocessing import StandardScaler, MinMaxScaler
            import numpy as np
            
            data = np.array(data)
            
            if method == "standard":
                scaler = StandardScaler()
            elif method == "minmax":
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            
            normalized = scaler.fit_transform(data.reshape(-1, 1) if data.ndim == 1 else data)
            return normalized, scaler
        except ImportError:
            raise ImportError("scikit-learn is required for normalization")
