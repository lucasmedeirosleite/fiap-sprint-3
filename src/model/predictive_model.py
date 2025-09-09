"""
Temperature Prediction Model for IoT Sensors

This module implements a Random Forest model to predict temperature readings
from IoT sensor data using temporal features and historical patterns.
"""

import logging
import warnings
from pathlib import Path
from typing import Tuple, List, Dict, Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
  """Handles feature engineering for sensor data."""
  
  @staticmethod
  def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create temporal features from timestamp column.
    
    Args:
      df: DataFrame with timestamp column
      
    Returns:
      DataFrame with additional temporal features
    """
    df = df.copy()
    
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['day_of_month'] = df['timestamp'].dt.day
    df['quarter'] = df['timestamp'].dt.quarter
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df
  
  @staticmethod
  def create_lag_features(
    df: pd.DataFrame,
    sensor_id: str,
    lags: List[int] = None
  ) -> pd.DataFrame:
    """
    Create lag features and rolling statistics for a specific sensor.
    
    Args:
      df: DataFrame with sensor data
      sensor_id: Unique sensor identifier
      lags: List of lag periods to create
      
    Returns:
      DataFrame with lag features and rolling statistics
    """
    if lags is None:
      lags = [1, 2, 3, 6, 12, 24]
    
    df_sensor = df[df['sensor_id'] == sensor_id].copy()
    df_sensor = df_sensor.sort_values('timestamp')
    
    for lag in lags:
      df_sensor[f'temp_lag_{lag}'] = df_sensor['temperature'].shift(lag)
      df_sensor[f'humidity_lag_{lag}'] = df_sensor['humidity'].shift(lag)
    
    df_sensor['temp_ma_6'] = df_sensor['temperature'].rolling(
      window=6, min_periods=1
    ).mean()
    df_sensor['temp_ma_24'] = df_sensor['temperature'].rolling(
      window=24, min_periods=1
    ).mean()
    df_sensor['humidity_ma_6'] = df_sensor['humidity'].rolling(
      window=6, min_periods=1
    ).mean()
    df_sensor['humidity_ma_24'] = df_sensor['humidity'].rolling(
      window=24, min_periods=1
    ).mean()
    
    df_sensor['temp_std_24'] = df_sensor['temperature'].rolling(
      window=24, min_periods=1
    ).std()
    df_sensor['humidity_std_24'] = df_sensor['humidity'].rolling(
      window=24, min_periods=1
    ).std()
    
    return df_sensor


class SensorTemperaturePredictor:
  """Main class for temperature prediction model."""
  
  def __init__(self, model_params: Dict[str, Any] = None):
    """
    Initialize the predictor with model parameters.
    
    Args:
      model_params: Dictionary of RandomForestRegressor parameters
    """
    self.model_params = model_params or {
      'n_estimators': 100,
      'max_depth': 20,
      'min_samples_split': 5,
      'min_samples_leaf': 2,
      'random_state': 42,
      'n_jobs': -1
    }
    
    self.model = RandomForestRegressor(**self.model_params)
    self.scaler = StandardScaler()
    self.feature_engineer = FeatureEngineer()
    self.feature_columns = None
    
  def load_data(self, train_path: str, test_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and prepare training and testing data.
    
    Args:
      train_path: Path to training data CSV
      test_path: Path to testing data CSV
      
    Returns:
      Tuple of (train_df, test_df)
    """
    logger.info("Loading training data...")
    train_df = pd.read_csv(train_path)
    train_df['timestamp'] = pd.to_datetime(train_df['timestamp'])
    
    logger.info("Loading test data...")
    test_df = pd.read_csv(test_path)
    test_df['timestamp'] = pd.to_datetime(test_df['timestamp'])
    
    logger.info(f"Training data: {len(train_df)} records")
    logger.info(f"Test data: {len(test_df)} records")
    
    return train_df, test_df
  
  def prepare_features(
    self,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
  ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply feature engineering to training and test data.
    
    Args:
      train_df: Training DataFrame
      test_df: Testing DataFrame
      
    Returns:
      Tuple of processed (train_df, test_df)
    """
    logger.info("Engineering features...")
    
    train_processed = []
    test_processed = []
    
    for sensor_id in train_df['sensor_id'].unique():
      logger.info(f"Processing sensor {sensor_id[:8]}...")
      
      train_sensor = train_df[train_df['sensor_id'] == sensor_id].copy()
      train_sensor = self.feature_engineer.create_temporal_features(train_sensor)
      train_sensor = self.feature_engineer.create_lag_features(train_sensor, sensor_id)
      train_processed.append(train_sensor)
      
      if sensor_id in test_df['sensor_id'].unique():
        test_sensor = test_df[test_df['sensor_id'] == sensor_id].copy()
        test_sensor = self.feature_engineer.create_temporal_features(test_sensor)
        test_sensor = self.feature_engineer.create_lag_features(test_sensor, sensor_id)
        test_processed.append(test_sensor)
    
    train_df = pd.concat(train_processed, ignore_index=True)
    test_df = pd.concat(test_processed, ignore_index=True)
    
    train_df = train_df.dropna()
    test_df = test_df.dropna()
    
    logger.info(f"Features created - Training: {len(train_df)}, Test: {len(test_df)} records")
    
    return train_df, test_df
  
  def define_features(self) -> List[str]:
    """
    Define feature columns for the model.
    
    Returns:
      List of feature column names
    """
    self.feature_columns = [
      'latitude', 'longitude',
      'hour', 'day_of_week', 'month', 'day_of_month', 'quarter',
      'hour_sin', 'hour_cos', 'month_sin', 'month_cos',
      'humidity',
      'temp_lag_1', 'temp_lag_2', 'temp_lag_3', 
      'temp_lag_6', 'temp_lag_12', 'temp_lag_24',
      'humidity_lag_1', 'humidity_lag_2', 'humidity_lag_3',
      'humidity_lag_6', 'humidity_lag_12', 'humidity_lag_24',
      'temp_ma_6', 'temp_ma_24', 
      'humidity_ma_6', 'humidity_ma_24',
      'temp_std_24', 'humidity_std_24'
    ]
    return self.feature_columns
  
  def train(
    self,
    X_train: pd.DataFrame,
    y_train: pd.Series
  ) -> None:
    """
    Train the Random Forest model.
    
    Args:
      X_train: Training features
      y_train: Training target
    """
    logger.info("Training Random Forest model...")
    
    X_train_scaled = self.scaler.fit_transform(X_train)
    self.model.fit(X_train_scaled, y_train)
    
    logger.info("Model training completed")
  
  def predict(self, X_test: pd.DataFrame) -> np.ndarray:
    """
    Make predictions on test data.
    
    Args:
      X_test: Test features
      
    Returns:
      Array of predictions
    """
    X_test_scaled = self.scaler.transform(X_test)
    return self.model.predict(X_test_scaled)
  
  def evaluate(
    self,
    y_true: pd.Series,
    y_pred: np.ndarray,
    dataset_name: str = "Test"
  ) -> Dict[str, float]:
    """
    Calculate evaluation metrics.
    
    Args:
      y_true: True values
      y_pred: Predicted values
      dataset_name: Name of the dataset for logging
      
    Returns:
      Dictionary of metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    logger.info(f"\n{dataset_name} Set Metrics:")
    logger.info(f"  MAE: {mae:.4f}°C")
    logger.info(f"  RMSE: {rmse:.4f}°C")
    logger.info(f"  R² Score: {r2:.4f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}
  
  def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
    """
    Get feature importance from the trained model.
    
    Args:
      top_n: Number of top features to return
      
    Returns:
      DataFrame with feature importance
    """
    importance_df = pd.DataFrame({
      'feature': self.feature_columns,
      'importance': self.model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    logger.info(f"\nTop {top_n} Most Important Features:")
    for _, row in importance_df.head(top_n).iterrows():
      logger.info(f"  {row['feature']:20s}: {row['importance']:.4f}")
    
    return importance_df.head(top_n)


def main():
  """Main execution function."""
  
  base_path = Path(__file__).parent.parent.parent
  data_path = base_path / 'data'
  analysis_path = base_path / 'src' / 'analysis'
  
  predictor = SensorTemperaturePredictor()
  
  train_df, test_df = predictor.load_data(
    str(data_path / 'sensor_data_train.csv'),
    str(data_path / 'sensor_data_test.csv')
  )
  
  train_df, test_df = predictor.prepare_features(train_df, test_df)
  
  feature_columns = predictor.define_features()
  
  X_train = train_df[feature_columns]
  y_train = train_df['temperature']
  X_test = test_df[feature_columns]
  y_test = test_df['temperature']
  
  predictor.train(X_train, y_train)
  
  y_pred_train = predictor.predict(X_train)
  y_pred_test = predictor.predict(X_test)
  
  train_metrics = predictor.evaluate(y_train, y_pred_train, "Training")
  test_metrics = predictor.evaluate(y_test, y_pred_test, "Test")
  
  feature_importance = predictor.get_feature_importance()
  
  test_df['prediction'] = y_pred_test
  test_df['error'] = np.abs(test_df['temperature'] - test_df['prediction'])
  
  logger.info("\nPer-Sensor Error Analysis:")
  for sensor_id in test_df['sensor_id'].unique():
    sensor_data = test_df[test_df['sensor_id'] == sensor_id]
    mae_sensor = sensor_data['error'].mean()
    logger.info(f"  Sensor {sensor_id[:8]}...: MAE = {mae_sensor:.4f}°C")
  
  results_df = test_df[['sensor_id', 'timestamp', 'latitude', 'longitude',
                        'humidity', 'temperature', 'prediction', 'error']]
  results_df.to_csv(str(analysis_path / 'predictions_results.csv'), index=False)
  
  logger.info("\nModel training and evaluation completed successfully!")
  logger.info(f"Results saved to: {analysis_path / 'predictions_results.csv'}")
  logger.info(f"\nFinal Summary:")
  logger.info(f"  - Average prediction error: {test_metrics['mae']:.3f}°C")
  logger.info(f"  - Model explains {test_metrics['r2']*100:.1f}% of variance")
  logger.info(f"  - Most important features: temperature history and moving averages")


if __name__ == "__main__":
  main()