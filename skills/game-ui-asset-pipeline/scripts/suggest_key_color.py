#!/usr/bin/env python3
"""Suggest a safe flat background key color for UI asset generation."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install with: python -m pip install Pillow") from exc


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga", ".gif"}
DEFAULT_CANDIDATES = [
    "#ff00ff",
    "#00ff00",
    "#0000ff",
    "#00ffff",
    "#ffff00",
    "#ff0000",
    "#7f00ff",
    "#ff7f00",
]


def parse_hex(value: str) -> tuple[int, int, int]:
    value = value.strip().lower()
    match = re.fullmatch(r"#?([0-9a-f]{6})", value)
    if not match:
        raise argparse.ArgumentTypeError(f"Invalid hex color: {value}")
    raw = match.group(1)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def as_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def discover_inputs(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if not resolved.exists():
            raise SystemExit(f"Input does not exist: {resolved}")
        if resolved.is_dir():
            found.extend(item for item in sorted(resolved.rglob("*")) if item.is_file() and item.suffix.lower() in IMAGE_EXTS)
        elif resolved.is_file() and resolved.suffix.lower() in IMAGE_EXTS:
            found.append(resolved)
    if not found:
        raise SystemExit("No image files found.")
    return found


def sample_pixels(path: Path, max_side: int) -> list[tuple[int, int, int]]:
    with Image.open(path) as image:
        image = image.convert("RGBA")
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        image.thumbnail((max_side, max_side), resample)
        data = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
        return [(red, green, blue) for red, green, blue, alpha in data if alpha > 32]


def distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def percentile(values: list[float], ratio: float) -> float:
    index = min(len(values) - 1, max(0, round((len(values) - 1) * ratio)))
    return values[index]


def rank_candidates(pixels: list[tuple[int, int, int]], candidates: list[tuple[int, int, int]]) -> list[dict[str, Any]]:
    if not pixels:
        raise SystemExit("No visible pixels sampled from inputs.")

    ranked: list[dict[str, Any]] = []
    total = len(pixels)
    for candidate in candidates:
        distances = sorted(distance(pixel, candidate) for pixel in pixels)
        close_36 = sum(1 for value in distances if value <= 36)
        close_64 = sum(1 for value in distances if value <= 64)
        p01 = percentile(distances, 0.01)
        p05 = percentile(distances, 0.05)
        min_distance = distances[0]
        score = p01 + (p05 * 0.35) - (close_36 / total * 600) - (close_64 / total * 250)
        ranked.append(
            {
                "key_color": as_hex(candidate),
                "score": round(score, 3),
                "min_distance": round(min_distance, 3),
                "p01_distance": round(p01, 3),
                "p05_distance": round(p05, 3),
                "close_36_ratio": round(close_36 / total, 6),
                "close_64_ratio": round(close_64 / total, 6),
            }
        )
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path, help="Reference image or folder. Repeatable.")
    parser.add_argument("--candidates", default=",".join(DEFAULT_CANDIDATES), help="Comma-separated hex colors to rank.")
    parser.add_argument("--max-side", type=int, default=220, help="Thumbnail size used for sampling.")
    parser.add_argument("--max-pixels", type=int, default=160000, help="Maximum sampled pixels after downsampling.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidates = [parse_hex(part) for part in args.candidates.split(",") if part.strip()]
    images = discover_inputs(args.input)

    pixels: list[tuple[int, int, int]] = []
    for image in images:
        pixels.extend(sample_pixels(image, args.max_side))
    if len(pixels) > args.max_pixels:
        step = math.ceil(len(pixels) / args.max_pixels)
        pixels = pixels[::step]

    ranked = rank_candidates(pixels, candidates)
    result = {
        "recommended_key_color": ranked[0]["key_color"],
        "sampled_pixels": len(pixels),
        "images": [str(path) for path in images],
        "candidates": ranked,
        "warning": None,
    }
    if ranked[0]["p01_distance"] < 80 or ranked[0]["close_64_ratio"] > 0.001:
        result["warning"] = "Best candidate is still close to visible reference colors; prefer native alpha or a custom key color."

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"recommended_key_color: {result['recommended_key_color']}")
        print(f"sampled_pixels: {result['sampled_pixels']}")
        if result["warning"]:
            print(f"warning: {result['warning']}")
        print("candidates:")
        for item in ranked:
            print(
                f"- {item['key_color']} score={item['score']} "
                f"p01={item['p01_distance']} close64={item['close_64_ratio']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
