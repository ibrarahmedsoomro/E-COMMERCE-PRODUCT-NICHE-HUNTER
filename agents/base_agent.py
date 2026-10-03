"""Base Agent class supporting both Gemini Live/Flash API and deterministic Mock LLM."""

import os
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """Base orchestrator for multi-agent reasoning."""

    def __init__(self, model_name: str = "gemini-2.5-flash", use_mock: bool = False):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Automatically use Mock LLM if API key is not supplied or mock is forced
        self.use_mock = use_mock or (not bool(self.api_key))
        self.client = None

        if not self.use_mock and self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.use_mock = True

    def generate_structured_output(
        self,
        system_instruction: str,
        prompt: str,
        response_schema: Type[T],
        mock_fallback: T
    ) -> T:
        """Calls Gemini API with structured JSON output or returns mock fallback."""
        if self.use_mock or self.client is None:
            return mock_fallback

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                    "temperature": 0.2
                }
            )
            data = json.loads(response.text)
            return response_schema(**data)
        except Exception:
            # Fallback to safe deterministic output if network/rate-limit occurs
            return mock_fallback
