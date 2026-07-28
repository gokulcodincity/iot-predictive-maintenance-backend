"""Anomaly detection using LSTM Autoencoder."""

import numpy as np

from app.ml.model_loader import get_lstm_model, get_scaler, get_threshold


class AnomalyDetector:
    """LSTM Autoencoder-based anomaly detector for sensor data."""

    EXPECTED_TIMESTEPS = 30
    EXPECTED_FEATURES = 5

    def __init__(self):
        """Initialize detector by loading models and threshold."""
        self.lstm_model = get_lstm_model()
        self.scaler = get_scaler()
        self.threshold_config = get_threshold()

    def predict(self, sensor_window: np.ndarray) -> dict:
        """Detect anomalies in sensor window using LSTM reconstruction error.

        Args:
            sensor_window: NumPy array of shape (30, 5)
                          30 timesteps, 5 sensor features each
                          Features: [temp, vibration, current, speed, throughput]

        Returns:
            Dictionary with:
                - anomaly_score: float (mean absolute error)
                - is_anomaly: bool (True if score exceeds threshold)

        Raises:
            ValueError: If input shape is not (30, 5)
        """
        # Step 1: Validate input shape
        sensor_data = np.array(sensor_window, dtype=np.float32)
        if sensor_data.shape != (self.EXPECTED_TIMESTEPS, self.EXPECTED_FEATURES):
            raise ValueError(
                f"Invalid input shape: {sensor_data.shape}. "
                f"Expected ({self.EXPECTED_TIMESTEPS}, {self.EXPECTED_FEATURES})"
            )

        # Step 2: Scale input using fitted scaler
        # Scaler trained on (samples, features) → scale each row independently
        scaled_data = self.scaler.transform(sensor_data)
        # scaled_data shape: (30, 5)

        # Step 3: Reshape for LSTM inference
        # LSTM expects (batch_size, timesteps, features)
        lstm_input = scaled_data.reshape(1, self.EXPECTED_TIMESTEPS, self.EXPECTED_FEATURES)
        # lstm_input shape: (1, 30, 5)

        # Step 4: Run reconstruction through LSTM Autoencoder
        reconstructed = self.lstm_model.predict(lstm_input, verbose=0)
        # reconstructed shape: (1, 30, 5)

        # Step 5: Calculate reconstruction error (Mean Absolute Error)
        reconstruction_error = np.mean(np.abs(reconstructed - lstm_input))

        # Step 6: Load threshold and compare
        threshold_value = self.threshold_config.get("anomaly_threshold", 0.5)
        is_anomaly = reconstruction_error > threshold_value
        anomaly_score = float(reconstruction_error)

        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly,
        }
