# services/feature_engineering.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
import asyncio
from datetime import datetime, timedelta
import logging

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(score_func=f_classif, k=20)
        self.logger = logging.getLogger(__name__)
        
    async def create_transaction_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create ML-ready features from raw transaction data"""
        
        # Basic transaction features
        features = pd.DataFrame()
        
        # Time-based features
        features['hour_of_day'] = pd.to_datetime(transactions_df['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(transactions_df['timestamp']).dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Transaction amount features
        features['log_amount'] = np.log1p(transactions_df['value'])
        features['amount_zscore'] = self.calculate_zscore(transactions_df['value'])
        
        # Wallet behavior features
        features = await self.add_wallet_behavior_features(features, transactions_df)
        
        # Market context features
        features = await self.add_market_context_features(features, transactions_df)
        
        return features
    
    async def add_wallet_behavior_features(self, features: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
        """Add wallet-specific behavioral features"""
        
        wallet_stats = transactions.groupby('wallet_address').agg({
            'value': ['count', 'mean', 'std', 'sum'],
            'timestamp': ['min', 'max']
        }).reset_index()
        
        wallet_stats.columns = ['wallet_address', 'tx_count', 'avg_tx_size', 
                               'tx_size_std', 'total_volume', 'first_tx', 'last_tx']
        
        # Calculate wallet age
        wallet_stats['wallet_age_days'] = (
            pd.to_datetime(wallet_stats['last_tx']) - 
            pd.to_datetime(wallet_stats['first_tx'])
        ).dt.days
        
        # Merge wallet features
        features = features.merge(wallet_stats, on='wallet_address', how='left')
        
        return features
    
    async def add_market_context_features(self, features: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
        """Add market and ecosystem context features"""
        
        # Transaction frequency features
        hourly_tx_count = transactions.groupby(
            pd.to_datetime(transactions['timestamp']).dt.floor('H')
        ).size()
        
        features['hourly_tx_volume'] = features['timestamp'].map(
            pd.to_datetime(hourly_tx_count.index).hour
        )
        
        # Price volatility features (if price data available)
        features['price_volatility'] = await self.calculate_volatility(transactions)
        
        return features
    
    def calculate_zscore(self, values: pd.Series) -> pd.Series:
        """Calculate Z-score for outlier detection"""
        return (values - values.mean()) / values.std()