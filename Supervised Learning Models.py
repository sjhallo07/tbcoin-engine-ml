# services/supervised_learning.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score
import xgboost as xgb
import lightgbm as lgb
import joblib
import asyncio
from typing import Dict, Tuple, Any
import logging

class SupervisedLearningEngine:
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.model_metrics = {}
        self.logger = logging.getLogger(__name__)
        
    async def train_price_movement_model(self, features: pd.DataFrame, labels: pd.Series) -> Dict:
        """Train model to predict price movement direction"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Define models to train
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBClassifier(n_estimators=100, random_state=42),
            'lightgbm': lgb.LGBMClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42)
        }
        
        best_model = None
        best_score = 0
        
        # Train and evaluate each model
        for name, model in models.items():
            self.logger.info(f"Training {name}...")
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            
            self.model_metrics[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall
            }
            
            # Store feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(
                    features.columns, model.feature_importances_
                ))
            
            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                
            self.logger.info(f"{name} - Accuracy: {accuracy:.4f}")
        
        # Save best model
        self.models['price_movement'] = best_model
        await self.save_model(best_model, 'price_movement_model.pkl')
        
        return {
            'best_model': 'price_movement',
            'best_accuracy': best_score,
            'all_metrics': self.model_metrics
        }
    
    async def train_anomaly_detection_model(self, features: pd.DataFrame) -> Dict:
        """Train model to detect anomalous transactions"""
        
        # For anomaly detection, we'll use unsupervised approach first
        from sklearn.ensemble import IsolationForest
        from sklearn.svm import OneClassSVM
        
        anomaly_models = {
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'one_class_svm': OneClassSVM(nu=0.1)
        }
        
        anomaly_scores = {}
        
        for name, model in anomaly_models.items():
            scores = model.fit_predict(features)
            anomaly_scores[name] = scores
            
            self.logger.info(f"Anomaly detection {name} completed")
        
        self.models['anomaly_detection'] = anomaly_models
        return anomaly_scores
    
    async def save_model(self, model, filename: str):
        """Save trained model to disk"""
        joblib.dump(model, f'models/{filename}')
        self.logger.info(f"Model saved: {filename}")
    
    async def predict_price_movement(self, features: pd.DataFrame) -> Dict:
        """Make predictions using trained model"""
        if 'price_movement' not in self.models:
            raise ValueError("Price movement model not trained")
            
        predictions = self.models['price_movement'].predict(features)
        probabilities = self.models['price_movement'].predict_proba(features)
        
        return {
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'confidence': np.max(probabilities, axis=1).tolist()
        }