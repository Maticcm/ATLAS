"""Gemini-backed Brain — stateless single-turn chat."""

from __future__ import annotations

import os

from google import genai
from google.genai import types

from atlas.tools.registry import ToolDefinition
from atlas.tools.tool_call import ToolCall, ToolResult


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
            message: The new user message to send.

        Returns:
            The model's plain-text response.
        """
        contents = self._build_contents(history, message)

        response = self._client.models.generate_content(
            model=self._MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=self._system_prompt,
            ),
        )

        return (response.text or "").strip()

    def chat_with_tools(
        self,
        history: list[dict[str, str]],
        message: str,
        tools: list[ToolDefinition],
        tool_results: list[ToolResult] | None = None,
    ) -> str | ToolCall:
        """Send a message (and optional tool results) and return a reply or tool call.

        Args:
            history: Full conversation so far (see ``chat``).
            message: The original user message.
            tools:   Definitions of tools available to the model.
            tool_results: If the model previously returned a ToolCall, this
                          contains the outcome of executing it.

        Returns:
            Either a plain text string (the final answer) OR a ToolCall
            requesting the application to execute a tool.
        """
        contents = self._build_contents(history, message)

        if tool_results:
            # Reconstruct the function call and response so the model
            # understands what it did and what happened.
            for res in tool_results:
                contents.append(
                    types.Content(
                        role="model",
                        parts=[
                            types.Part.from_function_call(
                                name=res.tool_name,
                                args={},  # Minimal args, we just need the history
                            )
                        ],
                    )
                )
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=res.tool_name,
                                response={"output": res.output, "success": res.success},
                            )
                        ],
                    )
                )

        gemini_tools = [
            types.FunctionDeclaration(
                name=t.name,
                description=t.description,
                parameters=t.parameters,
            )
            for t in tools
        ]

        response = self._client.models.generate_content(
            model=self._MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=self._system_prompt,
                tools=[types.Tool(function_declarations=gemini_tools)],
                # Disable automatic execution so we can handle it manually.
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

        if not response.candidates:
            return ""

        # Check if the model decided to call a tool
        for part in response.candidates[0].content.parts:
            if part.function_call:
                args = {}
                if part.function_call.args:
                    args = dict(part.function_call.args)
                return ToolCall(name=part.function_call.name, arguments=args)

        # Otherwise, just return the text
        return (response.text or "").strip()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_contents(
        self, history: list[dict[str, str]], message: str
    ) -> list[types.Content]:
        """Translate provider-agnostic history into Gemini Content objects."""
        contents: list[types.Content] = [
            types.Content(
                role="user" if turn["role"] == "user" else "model",
                parts=[types.Part(text=turn["content"])],
            )
            for turn in history
        ]
        contents.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )
        return contents
