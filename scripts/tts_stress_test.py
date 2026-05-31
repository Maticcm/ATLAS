"""
Stress-test script for Chatterbox TTS word-skipping regression.

Synthesises the same sentence N times and saves each run to a WAV file
so you can compare them in an audio editor (e.g. Audacity) or diff durations
to spot truncation.

Usage:
    python scripts/tts_stress_test.py
    python scripts/tts_stress_test.py --runs 10 --text "Your custom sentence."
    python scripts/tts_stress_test.py --out-dir out/tts

Output:
    run_001.wav, run_002.wav, … in --out-dir (default: tts_stress_test_output/)
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import torch
import torchaudio


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chatterbox TTS stress-test")
    parser.add_argument(
        "--text",
        default=(
            "Sir, I do not have access to your personal statistics. "
            "Please specify the type of stats you require."
        ),
        help="Sentence to synthesise repeatedly.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of synthesis passes (default: 5).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("tts_stress_test_output"),
        help="Directory to write WAV files (default: tts_stress_test_output/).",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Torch device (cuda/cpu/mps). Auto-detected if omitted.",
    )
    return parser.parse_args()


def _detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("tts_stress_test")

    args = _parse_args()
    device = args.device or _detect_device()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    log.info("Loading Chatterbox TTS on %s …", device)
    from chatterbox.tts import ChatterboxTTS
    model = ChatterboxTTS.from_pretrained(device=device)
    log.info("Model ready. Sample rate: %d Hz", model.sr)

    word_count = len(args.text.split())
    max_new_tokens = word_count * 25 + 200

    log.info("Text   : %r", args.text)
    log.info("Words  : %d", word_count)
    log.info("Runs   : %d", args.runs)
    log.info("MaxTok : %d", max_new_tokens)
    log.info("OutDir : %s", args.out_dir.resolve())
    print()

    durations: list[float] = []

    for i in range(1, args.runs + 1):
        log.info("=== Run %d / %d ===", i, args.runs)
        t0 = time.perf_counter()

        wav = model.generate(
            args.text,
            temperature=0.5,
            cfg_weight=0.7,
            exaggeration=0.35,
            repetition_penalty=1.0,
            max_new_tokens=max_new_tokens,
        )

        elapsed = time.perf_counter() - t0
        audio = wav.squeeze(0).cpu()
        duration_s = audio.shape[0] / model.sr
        durations.append(duration_s)

        out_path = args.out_dir / f"run_{i:03d}.wav"
        torchaudio.save(str(out_path), audio.unsqueeze(0), model.sr)

        log.info(
            "  Generated in %.2fs | Audio duration %.2fs | Saved → %s",
            elapsed,
            duration_s,
            out_path,
        )

    print()
    log.info("=== Summary ===")
    log.info("  Durations: %s", [f"{d:.2f}s" for d in durations])
    log.info("  Min: %.2fs  Max: %.2fs  Range: %.2fs",
             min(durations), max(durations), max(durations) - min(durations))

    # A large range (>0.5s) suggests inconsistent truncation.
    threshold = 0.5
    if max(durations) - min(durations) > threshold:
        log.warning(
            "Duration range %.2fs exceeds %.2fs — possible truncation variance.",
            max(durations) - min(durations),
            threshold,
        )
        sys.exit(1)
    else:
        log.info("✅ Duration variance within acceptable range.")


if __name__ == "__main__":
    main()
