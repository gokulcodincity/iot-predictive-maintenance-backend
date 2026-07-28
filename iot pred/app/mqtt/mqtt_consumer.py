"""MQTT consumer for AWS IoT Core telemetry data."""

import json
from datetime import datetime
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings


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
        """Handle incoming MQTT message.

        Args:
            client: MQTT client instance
            userdata: User data (not used)
            msg: MQTT message object
        """
        try:
            # Decode JSON payload
            payload = json.loads(msg.payload.decode("utf-8"))

            # Validate payload
            self._validate_payload(payload)

            # Call callback if provided
            if self.on_telemetry_callback:
                self.on_telemetry_callback(payload)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {str(e)}") from e
        except ValueError as e:
            raise ValueError(f"Payload validation failed: {str(e)}") from e

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
