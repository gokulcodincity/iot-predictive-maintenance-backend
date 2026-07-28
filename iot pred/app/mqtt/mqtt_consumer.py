"""MQTT consumer for AWS IoT Core telemetry data with pipeline orchestration."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.db.database import get_database_manager
from app.ml.feature_extractor import FeatureExtractor
from app.ml.inference_service import InferenceService
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.workflow.workflow_orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


class MQTTConsumer:
    """Subscribes to AWS IoT Core MQTT topics and processes telemetry data."""

    # MQTT topic for telemetry
    TELEMETRY_TOPIC = "factory/machine1/telemetry"

    # Required fields in telemetry payload
    REQUIRED_FIELDS = {"machine_id", "timestamp"}

    def __init__(
        self,
        broker_address: str,
        cert_path: str,
        key_path: str,
        ca_path: str,
        on_telemetry_callback: Optional[Callable] = None,
    ):
        """Initialize MQTT consumer with AWS IoT Core credentials.

        Args:
            broker_address: AWS IoT Core endpoint (e.g., "xxxxxx.iot.us-east-1.amazonaws.com")
            cert_path: Path to device certificate
            key_path: Path to private key
            ca_path: Path to CA certificate
            on_telemetry_callback: Callback function to process telemetry data
        """
        self.broker_address = broker_address
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        self.on_telemetry_callback = on_telemetry_callback

        # Initialize MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def connect(self) -> None:
        """Connect to AWS IoT Core broker.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Configure TLS/SSL
            self.client.tls_set(
                ca_certs=self.ca_path,
                certfile=self.cert_path,
                keyfile=self.key_path,
                cert_reqs=mqtt.ssl.CERT_REQUIRED,
                tls_version=mqtt.ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
            self.client.tls_insecure = False

            # Connect to broker
            self.client.connect(self.broker_address, port=8883, keepalive=60)
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to MQTT broker at {self.broker_address}: {str(e)}"
            ) from e

    def start(self) -> None:
        """Start listening for messages (blocking)."""
        self.client.loop_forever()

    def start_async(self) -> None:
        """Start listening for messages (non-blocking)."""
        self.client.loop_start()

    def stop(self) -> None:
        """Stop listening and disconnect from broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties):
        """Handle MQTT connection success.

        Args:
            client: MQTT client instance
            userdata: User data (not used)
            connect_flags: Connection flags
            reason_code: Connection result code
            properties: MQTT properties
        """
        if reason_code == 0:
            # Connection successful
            client.subscribe(self.TELEMETRY_TOPIC)
        else:
            raise ConnectionError(f"Failed to connect, return code {reason_code}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT message with complete pipeline orchestration.

        Args:
            client: MQTT client instance
            userdata: User data (not used)
            msg: MQTT message object
        """
        try:
            # Step 1: Decode JSON payload
            payload = json.loads(msg.payload.decode("utf-8"))

            # Step 2: Validate payload
            self._validate_payload(payload)

            # Step 3-8: Orchestrate pipeline (use event loop if available)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, schedule as task
                    asyncio.create_task(self._orchestrate_pipeline(payload))
                else:
                    # If no loop running, run synchronously
                    loop.run_until_complete(self._orchestrate_pipeline(payload))
            except RuntimeError:
                # No event loop, create new one
                asyncio.run(self._orchestrate_pipeline(payload))

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
        except ValueError as e:
            logger.error(f"Payload validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in message processing: {str(e)}")

    async def _orchestrate_pipeline(self, payload: dict) -> None:
        """Orchestrate complete telemetry processing pipeline.

        Pipeline stages:
        1. Save raw telemetry
        2. Extract features
        3. Run inference
        4. Save predictions
        5. Execute workflow rules
        6. Log success

        Args:
            payload: Validated telemetry payload

        Raises:
            Exception: If any stage fails (logged, pipeline continues)
        """
        try:
            # Get database manager and create session
            db_manager = await get_database_manager()

            async with db_manager.session_context() as db_session:
                # Step 1: Save raw telemetry to database
                logger.info(f"Step 1: Saving telemetry for machine {payload['machine_id']}")
                telemetry_repo = TelemetryRepository(db_session)
                telemetry_record = await telemetry_repo.save_telemetry(payload)
                logger.info(
                    f"Step 1 Complete: Telemetry saved with id {telemetry_record.id}"
                )

                # Step 2: Extract feature vector
                logger.info("Step 2: Extracting feature vector")
                feature_result = FeatureExtractor.extract_features(payload)
                logger.info(
                    f"Step 2 Complete: Feature vector created {feature_result['feature_vector']}"
                )

                # Step 3: Run inference service
                logger.info("Step 3: Running inference service")
                inference_service = InferenceService()
                inference_result = await inference_service.predict(
                    feature_result["feature_vector"],
                    feature_result["feature_vector"],  # engineered_features
                )
                logger.info(
                    f"Step 3 Complete: Prediction status {inference_result['prediction_status']}"
                )

                # Step 4: Save prediction to database
                logger.info("Step 4: Saving prediction")
                prediction_repo = PredictionRepository(db_session)
                prediction_data = {
                    "machine_id": payload["machine_id"],
                    "telemetry_id": telemetry_record.id,
                    "anomaly_score": inference_result["anomaly_score"],
                    "failure_risk": inference_result["failure_risk"],
                    "confidence": inference_result["confidence"],
                    "prediction_status": inference_result["prediction_status"],
                    "model_version": "lstm-xgboost-v1",
                    "inference_time_ms": 0,
                }
                prediction_record = await prediction_repo.create_prediction(
                    prediction_data
                )
                logger.info(
                    f"Step 4 Complete: Prediction saved with id {prediction_record.id}"
                )

                # Step 5: Call workflow orchestrator for rules and alerts
                logger.info("Step 5: Executing workflow orchestrator")
                orchestrator = WorkflowOrchestrator()
                workflow_result = await orchestrator.process_prediction(
                    {
                        "machine_id": payload["machine_id"],
                        "prediction_status": inference_result["prediction_status"],
                        "failure_risk": inference_result["failure_risk"],
                        "anomaly_score": inference_result["anomaly_score"],
                        "confidence": inference_result["confidence"],
                    }
                )
                logger.info(f"Step 5 Complete: Workflow executed, alert severity {workflow_result['alert']['severity']}")

                # Step 6: Log pipeline success
                logger.info(
                    f"Pipeline Complete: Machine {payload['machine_id']} -> "
                    f"Telemetry({telemetry_record.id}) -> "
                    f"Prediction({prediction_record.id}) -> "
                    f"Alert({workflow_result['alert']['severity']})"
                )

        except ValueError as e:
            logger.error(f"Validation error in pipeline: {str(e)}")
        except Exception as e:
            logger.error(
                f"Error in telemetry processing pipeline for machine {payload.get('machine_id')}: {str(e)}"
            )

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        """Handle MQTT disconnection.

        Args:
            client: MQTT client instance
            userdata: User data (not used)
            disconnect_flags: Disconnect flags
            reason_code: Disconnection reason code
            properties: MQTT properties
        """
        if reason_code != 0:
            pass  # Unexpected disconnection

    def _validate_payload(self, payload: dict) -> None:
        """Validate telemetry payload structure and required fields.

        Args:
            payload: Telemetry payload dictionary

        Raises:
            ValueError: If payload is invalid
        """
        # Check required fields
        missing_fields = self.REQUIRED_FIELDS - set(payload.keys())
        if missing_fields:
            raise ValueError(
                f"Payload missing required fields: {', '.join(sorted(missing_fields))}"
            )

        # Validate machine_id
        machine_id = payload.get("machine_id")
        if not isinstance(machine_id, int) or machine_id <= 0:
            raise ValueError(f"machine_id must be a positive integer, got {machine_id}")

        # Validate timestamp
        timestamp = payload.get("timestamp")
        if isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp)
            except ValueError:
                raise ValueError(f"timestamp must be ISO format, got {timestamp}")
        elif not isinstance(timestamp, (int, float)):
            raise ValueError(f"timestamp must be ISO format string or Unix timestamp")

        # Validate optional sensor fields (if present, must be numbers >= 0)
        sensor_fields = {"temperature", "vibration", "current", "speed", "throughput"}
        for field in sensor_fields:
            if field in payload:
                value = payload[field]
                if not isinstance(value, (int, float)):
                    raise ValueError(f"{field} must be a number, got {type(value).__name__}")
                if value < 0:
                    raise ValueError(f"{field} must be >= 0, got {value}")


def create_mqtt_consumer(
    on_telemetry_callback: Optional[Callable] = None,
) -> MQTTConsumer:
    """Factory function to create MQTT consumer with AWS IoT Core settings.

    Args:
        on_telemetry_callback: Optional callback function to process telemetry data

    Returns:
        Configured MQTTConsumer instance

    Raises:
        ValueError: If AWS IoT settings are not configured
    """
    # Get AWS IoT settings (assume they're in settings)
    broker_address = getattr(settings, "AWS_IOT_ENDPOINT", None)
    cert_path = getattr(settings, "AWS_IOT_CERT_PATH", None)
    key_path = getattr(settings, "AWS_IOT_KEY_PATH", None)
    ca_path = getattr(settings, "AWS_IOT_CA_PATH", None)

    # Validate settings
    if not all([broker_address, cert_path, key_path, ca_path]):
        raise ValueError(
            "AWS IoT settings not configured (AWS_IOT_ENDPOINT, AWS_IOT_CERT_PATH, "
            "AWS_IOT_KEY_PATH, AWS_IOT_CA_PATH)"
        )

    return MQTTConsumer(
        broker_address=broker_address,
        cert_path=cert_path,
        key_path=key_path,
        ca_path=ca_path,
        on_telemetry_callback=on_telemetry_callback,
    )
