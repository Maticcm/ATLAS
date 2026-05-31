"""Chatterbox TTS speech engine — generates and plays audio from text."""

from __future__ import annotations

import logging

import numpy as np
import sounddevice as sd
import torch
from chatterbox.tts import ChatterboxTTS

# Typical speech token rate for Chatterbox is ~86 tokens/second.
# 1000 tokens ≈ 11.6 seconds — too short for longer responses.
# We budget 25 tokens per word plus a 200-token safety margin.
_TOKENS_PER_WORD: int = 25
_TOKEN_MARGIN: int = 200


class SpeechEngine:
    """Loads the Chatterbox model once and speaks text on demand.

    The model is loaded eagerly during ``__init__`` so that startup
    failures surface immediately rather than on the first reply.

    Args:
        logger: Logger instance for status and error messages.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._device = self._detect_device()
        self._logger.info("Loading Chatterbox TTS on %s …", self._device)
        self._model = ChatterboxTTS.from_pretrained(device=self._device)
        self._logger.info("Chatterbox TTS ready.")

    def speak(self, text: str) -> None:
        """Synthesise *text* and play it through the default audio device.

        This call blocks until playback finishes.  The caller is
        responsible for catching exceptions — a failure here should
        never crash the session.

        Generation parameters are chosen for reliability over expressiveness:
        - ``temperature=0.5``  — less randomness → EOS sampled less eagerly
        - ``cfg_weight=0.7``   — stronger text adherence → fewer skipped words
        - ``exaggeration=0.35`` — neutral tone → no pacing artefacts
        - ``repetition_penalty=1.0`` — no penalty; let the codec repeat tokens
          naturally (repeated acoustic tokens ≠ repeated words)

        Args:
            text: Plain text to speak aloud.
        """
        text = text.strip()
        if not text:
            return

        word_count = len(text.split())
        max_new_tokens = word_count * _TOKENS_PER_WORD + _TOKEN_MARGIN
        self._logger.debug(
            "TTS | original=%r | max_new_tokens=%d", text, max_new_tokens
        )

        wav = self._model.generate(
            text,
            temperature=0.5,
            cfg_weight=0.7,
            exaggeration=0.35,
            repetition_penalty=1.0,
        )

        # Chatterbox returns a torch.Tensor (1, samples).
        # sounddevice expects a 1-D or 2-D numpy float32 array.
        audio: np.ndarray = wav.squeeze(0).cpu().numpy()
        duration_s = len(audio) / self._model.sr
        self._logger.debug(
            "TTS | audio duration=%.2fs | sample_rate=%d",
            duration_s,
            self._model.sr,
        )

        sd.play(audio, samplerate=self._model.sr)
        sd.wait()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_device() -> str:
        """Return the best available torch device string."""
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
