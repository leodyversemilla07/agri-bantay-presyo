import json
import logging
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import (
    AIConfigurationError,
    AIProcessingError,
    AIRateLimitError,
)

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    AI-powered processor for extracting structured data from PDF text.
    Uses Google Gemini with retry logic and error handling.
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key and len(self.api_key) > 10:
            logger.info(f"AI: Configuring Gemini with key: {self.api_key[:5]}...{self.api_key[-5:]}")
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = "gemini-3-flash-preview"
                self.enabled = True
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.enabled = False
                self.client = None
        else:
            self.enabled = False
            self.client = None
            logger.warning("Gemini API Key invalid or missing")

    def _call_with_retry(self, prompt: str, config: Any = None) -> Optional[str]:
        """
        Call the AI API with retry logic for transient failures.

        Args:
            prompt: The prompt to send to the AI
            config: Optional configuration for the API call

        Returns:
            The response text or None if all retries failed

        Raises:
            AIRateLimitError: If rate limited after all retries
            AIProcessingError: If processing fails after all retries
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                if config:
                    response = self.client.models.generate_content(
                        model=self.model_name, contents=prompt, config=config
                    )
                else:
                    response = self.client.models.generate_content(model=self.model_name, contents=prompt)

                if response and response.text:
                    return response.text
                else:
                    logger.warning(f"Empty response on attempt {attempt + 1}")

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check for rate limiting
                if "rate" in error_str or "quota" in error_str or "429" in error_str:
                    wait_time = self.RETRY_DELAY * (2**attempt)  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                # Check for authentication errors (don't retry)
                if "auth" in error_str or "key" in error_str or "401" in error_str:
                    raise AIConfigurationError(reason=str(e))

                # Other errors - retry with backoff
                logger.warning(f"AI call failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        # All retries exhausted
        if last_error:
            if "rate" in str(last_error).lower():
                raise AIRateLimitError()
            raise AIProcessingError(service="Gemini", reason=str(last_error))

        return None

    def process_messy_rows(
        self, rows_text: str, report_date: str, master_list: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Sends raw text extracted from a PDF table to Gemini to structure and normalize it.

        Args:
            rows_text: Raw text extracted from PDF
            report_date: The date of the report
            master_list: Optional list of valid commodity names

        Returns:
            List of structured price entries
        """
        if not self.enabled:
            logger.warning("AI processor not enabled, returning empty list")
            return []

        if not rows_text or len(rows_text.strip()) < 50:
            logger.warning("Input text too short for AI processing")
            return []

        master_info = ""
        if master_list:
            master_info = "MASTER LIST OF ALLOWED COMMODITIES:\n" + "\n".join(
                [f"- {name}" for name in sorted(master_list)]
            )

        prompt = f"""
        You are an expert at extracting agricultural price data from messy PDF text.
        Given the following text extracted from a Department of Agriculture price monitoring report for the date {report_date},
        convert it into a structured JSON array of price entries.

        ### MASTER LIST REFERENCE
        {master_info}

        ### EXTRACTION RULES:
        1. **MANDATORY FIELD NORMALIZATION**:
           - Match every extracted item to the most likely candidate in the MASTER LIST.
           - If it is clearly a variant (e.g. "Imported", "Local"), ensure it matches the specific name in the master list.
           - DO NOT create duplicate entries for the same item. If an item appears multiple times in the text (e.g. in a summary and a detail table), extract it ONLY ONCE using the most complete data.

        2. **CATEGORY ACCURACY**:
           - Be extremely careful with Categories. Do not put Beef under Fish.
           - "Rice" category includes all rice variants. "Meat" includes Pork/Beef. "Fish" includes Bangus/Tilapia.

        3. **FIELDS**:
        - Entry: {{"commodity": string, "category": string, "unit": string, "price_low": number, "price_high": number, "price_prevailing": number, "price_average": number}}

        4. **CLEANING & UNITS**:
           - "Beef Brisket, Local" -> "Beef Brisket" (if that matches master list).
           - The unit is often not in a column but in the category header like "RICE (per kg)". Ensure the "unit" field is populated (e.g., "kg", "piece", "bottle").
           - Remove dangling commas or trailing abbreviations like "(Imp.)" if they are already integrated into the master name.

        5. Return ONLY a valid JSON array.

        ### TEXT TO PROCESS:
        {rows_text}
        """

        try:
            # Set safety settings to allow all content (for agricultural data)
            config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE",
                    ),
                ]
            )

            response_text = self._call_with_retry(prompt, config)

            if not response_text:
                logger.error("AI returned empty response after retries")
                return []

            logger.info(f"AI Raw Response: {response_text[:200]}...")

            # Clean and parse JSON response
            clean_json = response_text.strip()
            clean_json = clean_json.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(clean_json)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse AI response as JSON: {je}")
                logger.debug(f"Raw response: {clean_json[:500]}")
                return []

            if not isinstance(parsed, list):
                logger.error(f"AI response is not a list: {type(parsed)}")
                return []

            logger.info(f"AI Successfully parsed {len(parsed)} entries.")
            return parsed

        except (AIRateLimitError, AIConfigurationError):
            raise  # Re-raise for caller to handle
        except AIProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AI processing: {e}")
            raise AIProcessingError(service="Gemini", reason=str(e))

    def normalize_commodity_name(self, name: str) -> str:
        """
        Uses AI to normalize a commodity name to a standard form.

        Args:
            name: The commodity name to normalize

        Returns:
            Normalized commodity name
        """
        if not self.enabled:
            return name

        if not name or len(name.strip()) < 2:
            return name

        prompt = f"""
        Normalize the following agricultural commodity name to a standard, professional English name used in the Philippines.
        Original: "{name}"
        Standardized Name:
        """

        try:
            response_text = self._call_with_retry(prompt)
            if response_text:
                return response_text.strip()
            return name
        except Exception as e:
            logger.error(f"AI Normalization failed: {e}")
            return name
