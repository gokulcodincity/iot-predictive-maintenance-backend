"""Inference orchestration service for ML predictions."""

import numpy as np

from app.ml.anomaly_detector import AnomalyDetector
from app.ml.failure_predictor import FailurePredictor
from app.ml.model_loader import get_threshold


class InferenceService:
    """Orchestrates LSTM and XGBoost inference for predictions."""

    def __init__(self):
        """Initialize inference service with detector and predictor."""
        self.anomaly_detector = AnomalyDetector()
        self.failure_predictor = FailurePredictor()
        self.threshold_config = get_threshold()

    def predict(
        self,
        sensor_window: np.ndarray,
        engineered_features: list | np.ndarray,
    ) -> dict:
        """Run complete inference pipeline.

        Args:
            sensor_window: NumPy array of shape (30, 5)
                          30 timesteps of 5 sensor features
            engineered_features: List or array of preprocessed features
                                for XGBoost (typically same 5 features or aggregated)

        Returns:
            Dictionary with:
                - anomaly_score: float (0.0-1.0, LSTM reconstruction error)
                - failure_risk: float (0.0-1.0, XGBoost failure probability)
                - confidence: float (0.0-1.0, model confidence in failure prediction)
                - prediction_status: str (NORMAL, WARNING, or CRITICAL)

        Raises:
            ValueError: If input shapes are invalid
        """
        # Step 1: Run anomaly detection
        anomaly_result = self.anomaly_detector.predict(sensor_window)
        anomaly_score = anomaly_result["anomaly_score"]
        is_anomaly = anomaly_result["is_anomaly"]

        # Step 2: Run failure risk prediction
        failure_result = self.failure_predictor.predict(engineered_features)
        failure_risk = failure_result["failure_risk"]
        confidence = failure_result["confidence"]

        # Step 3: Determine prediction status based on rules
        anomaly_threshold = self.threshold_config.get("anomaly_threshold", 0.5)

        if failure_risk >= 0.70:
            # CRITICAL: High failure risk
            prediction_status = "CRITICAL"
        elif failure_risk >= 0.30 or is_anomaly:
            # WARNING: Medium failure risk or anomaly detected
            prediction_status = "WARNING"
        elif failure_risk < 0.30 and anomaly_score < anomaly_threshold:
            # NORMAL: Low risk and no anomaly
            prediction_status = "NORMAL"
        else:
            # Fallback: Conservative classification for edge cases
            prediction_status = "WARNING"

        return {
            "anomaly_score": anomaly_score,
            "failure_risk": failure_risk,
            "confidence": confidence,
            "prediction_status": prediction_status,
        }
