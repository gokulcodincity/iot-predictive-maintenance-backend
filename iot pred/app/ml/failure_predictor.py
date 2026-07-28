"""Failure risk prediction using XGBoost model."""

import numpy as np

from app.ml.model_loader import get_xgboost_model, get_scaler


class FailurePredictor:
    """XGBoost-based failure risk predictor for sensor features."""

    def __init__(self):
        """Initialize predictor by loading XGBoost model and scaler."""
        self.xgboost_model = get_xgboost_model()
        self.scaler = get_scaler()

    def predict(self, features: list | np.ndarray) -> dict:
        """Predict failure risk from sensor features.

        Args:
            features: List or array of sensor features
                     (e.g., [temperature, vibration, current, speed, throughput])
                     Should match the features used during training

        Returns:
            Dictionary with:
                - failure_risk: float (0.0-1.0, probability of failure)
                - confidence: float (0.0-1.0, model confidence in prediction)

        Raises:
            ValueError: If features are invalid or have incorrect shape
        """
        # Step 1: Validate and convert input to numpy array
        feature_array = np.array(features, dtype=np.float32)

        # Check that input is 1D
        if feature_array.ndim != 1:
            raise ValueError(
                f"Invalid feature dimensions: expected 1D array, got shape {feature_array.shape}"
            )

        # Check that feature count matches trained scaler
        expected_features = self.scaler.n_features_in_
        if len(feature_array) != expected_features:
            raise ValueError(
                f"Invalid feature count: expected {expected_features} features, "
                f"got {len(feature_array)}"
            )

        # Reshape for scaler (scaler expects 2D: samples, features)
        features_2d = feature_array.reshape(1, -1)

        # Step 2: Scale features using trained scaler
        scaled_features = self.scaler.transform(features_2d)
        # scaled_features shape: (1, n_features)

        # Step 3: Predict using XGBoost
        # predict_proba returns probability for each class
        # Format: [[prob_no_failure, prob_failure]]
        probabilities = self.xgboost_model.predict_proba(scaled_features)

        # Step 4: Extract failure risk (probability of failure class)
        # Index 1 is the positive class (failure)
        failure_risk = float(probabilities[0, 1])

        # Step 5: Calculate confidence from prediction probabilities
        # Confidence is the maximum probability (how sure the model is)
        confidence = float(np.max(probabilities[0]))

        return {
            "failure_risk": failure_risk,
            "confidence": confidence,
        }
