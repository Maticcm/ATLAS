"""Gemini-backed Brain — stateless single-turn chat."""

from __future__ import annotations

import os

from google import genai
from google.genai import types


class Brain:
    """Wraps the Gemini API. Stateless — caller owns conversation history.

    History is passed in as a plain list of ``{"role": str, "content": str}``
    dicts so that every future provider (GPT, Qwen, local models) can use the
    same canonical format without each managing memory differently.

    Args:
        system_prompt: The system instruction sent to the model on every call.

    Raises:
        RuntimeError: If the ``GEMINI_API_KEY`` environment variable is not set.
    """

    _MODEL = "gemini-2.5-flash"

    def __init__(self, system_prompt: str) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Export it before starting ATLAS."
            )

        self._client = genai.Client(api_key=api_key)
        self._system_prompt = system_prompt

    def chat(self, history: list[dict[str, str]], message: str) -> str:
        """Send a message and return the assistant's reply.

        Args:
            history: Full conversation so far as a list of
                     ``{"role": "user"|"assistant", "content": "..."}`` dicts.
                     The caller is responsible for maintaining and appending to
                     this list — Brain does not mutate it.
            message: The new user message to send.

        Returns:
            The model's plain-text response.
        """
        # Translate provider-agnostic history into Gemini Content objects.
        contents: list[types.Content] = [
            types.Content(
                role="user" if turn["role"] == "user" else "model",
                parts=[types.Part(text=turn["content"])],
            )
            for turn in history
        ]
        # Append the current message.
        contents.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )

        response = self._client.models.generate_content(
            model=self._MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=self._system_prompt,
            ),
        )

        return (response.text or "").strip()
