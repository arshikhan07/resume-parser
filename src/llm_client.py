# app/llm_client.py
import os
from typing import Any, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)

# This is a generic LLM/Embeddings client wrapper.
# Supports:
# - embeddings (for matching)
# - a "refine_parsed_resume" call that sends structured data to an LLM for cleanup
# Implementation uses OpenAI packages if OPENAI_API_KEY is provided; otherwise provides simple fallbacks.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # change as needed
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")


class LLMClient:
    def __init__(self):
        self.key = OPENAI_API_KEY

        # lazy import to avoid hard dependency at import time
        self._client = None
        if self.key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.key)
            except Exception as e:
                logger.warning("OpenAI import failed: %s", e)

    def is_available(self) -> bool:
        return self._client is not None

    def refine_parsed_resume(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a system+user prompt to an LLM to clean/normalize parsed resume fields.
        Returns refined parsed dict. If LLM not configured, return input unchanged.
        """
        if not self.is_available():
            return parsed

        prompt = f"""You are a resume parsing assistant. Given this JSON parsed resume, normalize fields (emails, phones, skill lists, company names) and return a JSON object with same keys: {parsed}"""
        try:
            resp = self._client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You normalize parsed resume JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            content = resp.choices[0].message.content
            import json
            # LLM might return JSON; attempt to parse
            parsed_out = json.loads(content)
            return parsed_out
        except Exception as e:
            logger.exception("LLM refine failed: %s", e)
            return parsed

    def get_embedding(self, text: str):
        if not self.is_available():
            # fallback: simple hash into vector space (not production)
            return [float(hash(text) % 1000) / 1000.0]
        try:
            resp = self._client.embeddings.create(model=OPENAI_EMBED_MODEL, input=text)
            return resp.data[0].embedding
        except Exception as e:
            logger.exception("Embedding failed: %s", e)
            return [float(hash(text) % 1000) / 1000.0]

    def semantic_score(self, text_a: str, text_b: str) -> float:
        # naive cosine similarity on embeddings
        import math
        a = self.get_embedding(text_a)
        b = self.get_embedding(text_b)
        # handle different sizes
        min_len = min(len(a), len(b))
        if min_len == 0:
            return 0.0
        dot = sum(a[i] * b[i] for i in range(min_len))
        na = math.sqrt(sum(a[i] * a[i] for i in range(min_len)))
        nb = math.sqrt(sum(b[i] * b[i] for i in range(min_len)))
        if na == 0 or nb == 0:
            return 0.0
        return float(dot / (na * nb))