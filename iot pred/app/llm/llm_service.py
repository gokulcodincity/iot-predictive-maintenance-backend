"""OpenAI LLM service for generating recommendations."""

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError

from app.core.config import settings


class LLMService:
    """OpenAI-based LLM service for generating maintenance recommendations."""

    def __init__(self):
        """Initialize OpenAI async client with credentials from settings."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in settings")
        if not settings.OPENAI_MODEL:
            raise ValueError("OPENAI_MODEL not configured in settings")

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_recommendation(self, prompt: str) -> dict:
        """Generate maintenance recommendation from prediction prompt using OpenAI.

        Args:
            prompt: Prompt string built by PromptBuilder

        Returns:
            Dictionary with:
                - model: str (model name used)
                - recommendation: str (LLM-generated recommendation)
                - input_tokens: int (tokens consumed by prompt)
                - output_tokens: int (tokens consumed by response)
                - total_tokens: int (total tokens used)

        Raises:
            ValueError: If prompt is empty
            RuntimeError: If OpenAI API call fails
        """
        # Step 1: Validate input
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # Step 2: Call OpenAI Responses API
            response = await self.client.responses.create(
                model=self.model,
                instructions="You are an expert Industrial IoT Predictive Maintenance AI assistant. Analyze the prediction data and provide concise, actionable maintenance recommendations.",
                input=prompt,
                max_output_tokens=2048,
            )

            # Step 3: Extract response and usage information
            recommendation_text = response.output_text

            # Return structured response
            return {
                "model": self.model,
                "recommendation": recommendation_text,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        except APITimeoutError as e:
            raise RuntimeError(
                f"OpenAI API timeout while generating recommendation"
            ) from e

        except APIConnectionError as e:
            raise RuntimeError(
                f"Failed to connect to OpenAI API"
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"OpenAI API error while generating recommendation: {str(e)}"
            ) from e
