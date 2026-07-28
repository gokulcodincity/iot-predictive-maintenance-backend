"""Model loader for lazy loading and caching ML models."""

from pathlib import Path

import joblib
import tensorflow as tf


# Module-level variables for lazy loading
_lstm_model = None
_xgboost_model = None
_scaler = None
_threshold = None

# Base directory for models
MODELS_DIR = Path(__file__).parent / "models"


def get_lstm_model():
    """Get LSTM Autoencoder model (lazy loaded).

    Returns:
        Loaded TensorFlow/Keras LSTM Autoencoder model

    Raises:
        FileNotFoundError: If model file not found in models/
        Exception: If model loading fails
    """
    global _lstm_model
    if _lstm_model is None:
        model_path = MODELS_DIR / "best_lstm_autoencoder"
        if not model_path.exists():
            raise FileNotFoundError(
                f"LSTM Autoencoder model not found at {model_path}"
            )
        _lstm_model = tf.keras.models.load_model(model_path)
    return _lstm_model


def get_xgboost_model():
    """Get XGBoost model (lazy loaded).

    Returns:
        Loaded XGBoost model

    Raises:
        FileNotFoundError: If model file not found in models/
        Exception: If model loading fails
    """
    global _xgboost_model
    if _xgboost_model is None:
        model_path = MODELS_DIR / "best_xgboost.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"XGBoost model not found at {model_path}")
        _xgboost_model = joblib.load(model_path)
    return _xgboost_model


def get_scaler():
    """Get feature scaler (lazy loaded).

    Returns:
        Loaded StandardScaler or similar from scikit-learn

    Raises:
        FileNotFoundError: If scaler file not found in models/
        Exception: If scaler loading fails
    """
    global _scaler
    if _scaler is None:
        scaler_path = MODELS_DIR / "standard_scaler.pkl"
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler not found at {scaler_path}")
        _scaler = joblib.load(scaler_path)
    return _scaler


def get_threshold():
    """Get anomaly detection threshold (lazy loaded).

    Returns:
        Dictionary with threshold configuration

    Raises:
        FileNotFoundError: If threshold file not found in models/
        Exception: If threshold loading fails
    """
    global _threshold
    if _threshold is None:
        threshold_path = MODELS_DIR / "anomaly_threshold.pkl"
        if not threshold_path.exists():
            raise FileNotFoundError(f"Threshold config not found at {threshold_path}")
        _threshold = joblib.load(threshold_path)
    return _threshold
