from google import genai
from google.genai import types
import json
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key and len(self.api_key) > 10:
            logger.info(f"AI: Configuring Gemini with key: {self.api_key[:5]}...{self.api_key[-5:]}")
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-3-flash-preview'
            self.enabled = True
        else:
            self.enabled = False
            logger.warning(f"Gemini API Key invalid or missing: {self.api_key}")

    def process_messy_rows(self, rows_text: str, report_date: str, master_list: List[str] = None) -> List[Dict[str, Any]]:
        """
        Sends raw text extracted from a PDF table to Gemini to structure and normalize it.
        """
        if not self.enabled:
            return []

        master_info = ""
        if master_list:
            master_info = f"MASTER LIST OF ALLOWED COMMODITIES:\n" + "\n".join([f"- {name}" for name in sorted(master_list)])

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
           - Entry: {{"commodity": string, "category": string, "unit": string, "price_low": number, "price_high": number, "price_prevailing": number}}
        
        4. **CLEANING**:
           - "Beef Brisket, Local" -> "Beef Brisket" (if that matches master list).
           - Remove dangling commas or trailing abbreviations like "(Imp.)" if they are already integrated into the master name.
        
        5. Return ONLY a valid JSON array.

        ### TEXT TO PROCESS:
        {rows_text}
        """

        try:
            # Set safety settings to allow all content (for agricultural data)
            config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
                    types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
                    types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
                    types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE'),
                ]
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            if not response or not response.text:
                logger.error(f"AI returned empty response. Response: {response}")
                return []

            logger.info(f"AI Raw Response: {response.text[:200]}...")
            clean_json = response.text.strip().replace('```json', '').replace('```', '')
            parsed = json.loads(clean_json)
            logger.info(f"AI Successfully parsed {len(parsed)} entries.")
            return parsed
        except Exception as e:
            logger.error(f"AI Processing failed: {e}")
            return []

    def normalize_commodity_name(self, name: str) -> str:
        """
        Uses AI to normalize a commodity name to a standard form.
        """
        if not self.enabled:
            return name

        prompt = f"""
        Normalize the following agricultural commodity name to a standard, professional English name used in the Philippines.
        Original: "{name}"
        Standardized Name:
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Normalization failed: {e}")
            return name
