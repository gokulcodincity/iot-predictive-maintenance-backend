"""Feature extraction from telemetry data."""

from datetime import datetime
from typing import Optional

import numpy as np


class FeatureExtractor:
    """Extracts and prepares feature vectors from telemetry data."""

    # Sensor fields in EXACT training order
    SENSOR_FIELDS = ["temperature", "vibration", "current", "speed", "throughput"]

    # All required fields for feature extraction
    REQUIRED_FIELDS = {"machine_id", "timestamp"} | set(SENSOR_FIELDS)

    @staticmethod
    def extract_features(payload: dict) -> dict:
        """Extract and prepare feature vector from telemetry payload.

        Args:
            payload: Telemetry payload containing:
                - machine_id: int
                - timestamp: str or float (ISO format or Unix timestamp)
                - temperature: float
                - vibration: float
                - current: float
                - speed: float
                - throughput: float

        Returns:
            Dictionary with:
                - machine_id: int
                - timestamp: str (ISO format)
                - feature_vector: list of floats in training order
                  [temperature, vibration, current, speed, throughput]

        Raises:
            ValueError: If payload is invalid or missing required fields
        """
        # Step 1: Validate payload has all required fields
        missing_fields = FeatureExtractor.REQUIRED_FIELDS - set(payload.keys())
        if missing_fields:
            raise ValueError(
                f"Payload missing required fields: {', '.join(sorted(missing_fields))}"
            )

        # Step 2: Extract and validate machine_id
        machine_id = payload.get("machine_id")
        if not isinstance(machine_id, int) or machine_id <= 0:
            raise ValueError(f"machine_id must be positive integer, got {machine_id}")

        # Step 3: Extract and normalize timestamp
        timestamp = payload.get("timestamp")
        timestamp_str = FeatureExtractor._normalize_timestamp(timestamp)

        # Step 4: Extract sensor values and build feature vector
        feature_vector = []
        for field in FeatureExtractor.SENSOR_FIELDS:
            value = payload.get(field)

            # Validate sensor value
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"{field} must be numeric, got {type(value).__name__}"
                )

            if value < 0:
                raise ValueError(f"{field} must be >= 0, got {value}")

            # Convert to float and add to vector
            feature_vector.append(float(value))

        # Step 5: Return structured result
        return {
            "machine_id": machine_id,
            "timestamp": timestamp_str,
            "feature_vector": feature_vector,
        }

    @staticmethod
    def _normalize_timestamp(timestamp) -> str:
        """Normalize timestamp to ISO format string.

        Args:
            timestamp: ISO format string or Unix timestamp (int/float)

        Returns:
            Timestamp in ISO format string

        Raises:
            ValueError: If timestamp format is invalid
        """
        if isinstance(timestamp, str):
            # Validate ISO format by parsing
            try:
                datetime.fromisoformat(timestamp)
                return timestamp
            except ValueError:
                raise ValueError(f"timestamp not in ISO format: {timestamp}")

        elif isinstance(timestamp, (int, float)):
            # Convert Unix timestamp to ISO format
            try:
                dt = datetime.utcfromtimestamp(timestamp)
                return dt.isoformat()
            except (ValueError, OSError):
                raise ValueError(f"timestamp not valid Unix timestamp: {timestamp}")

        else:
            raise ValueError(
                f"timestamp must be ISO string or Unix timestamp, got {type(timestamp).__name__}"
            )

    @staticmethod
    def extract_features_batch(payloads: list) -> list:
        """Extract features from multiple telemetry payloads.

        Args:
            payloads: List of telemetry payload dictionaries

        Returns:
            List of feature extraction results

        Raises:
            ValueError: If any payload is invalid
        """
        results = []
        for payload in payloads:
            result = FeatureExtractor.extract_features(payload)
            results.append(result)
        return results


class ExtractedFeatures:
    """Structured container for extracted features."""

    def __init__(self, machine_id: int, timestamp: str, feature_vector: list):
        """Initialize extracted features.

        Args:
            machine_id: Machine identifier
            timestamp: ISO format timestamp
            feature_vector: Feature vector as list of floats
        """
        self.machine_id = machine_id
        self.timestamp = timestamp
        self.feature_vector = feature_vector

    def to_numpy(self) -> np.ndarray:
        """Convert feature vector to numpy array.

        Returns:
            NumPy array of feature vector
        """
        return np.array(self.feature_vector, dtype=np.float32)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary with machine_id, timestamp, and feature_vector
        """
        return {
            "machine_id": self.machine_id,
            "timestamp": self.timestamp,
            "feature_vector": self.feature_vector,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ExtractedFeatures("
            f"machine_id={self.machine_id}, "
            f"timestamp={self.timestamp}, "
            f"features={len(self.feature_vector)})"
        )
