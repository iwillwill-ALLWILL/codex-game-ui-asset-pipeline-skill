#!/usr/bin/env python3
"""Clean chroma-key fringes and hidden RGB from generated transparent PNG UI assets."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageFilter


DEFAULT_KEYS = {
    "#ff00ff": (255, 0, 255),
    "#00ff00": (0, 255, 0),
    "#00ffff": (0, 255, 255),
    "#0000ff": (0, 0, 255),
}


@dataclass
class CleanStats:
    path: str
    flood_removed: int = 0
    edge_removed: int = 0
    transparent_rgb_fixed: int = 0
    remaining_edge_key_pixels: int = 0
    remaining_transparent_nonzero_rgb: int = 0


def parse_hex_color(value: str) -> tuple[int, int, int]:
    text = value.strip().lower()
    if text.startswith("#"):
        text = text[1:]
    if len(text) != 6:
        raise argparse.ArgumentTypeError(f"expected #RRGGBB color, got {value!r}")
    try:
        return tuple(int(text[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid hex color {value!r}") from exc


def channel_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def looks_like_key(rgb: tuple[int, int, int], keys: Iterable[tuple[int, int, int]]) -> bool:
    red, green, blue = rgb
    for key in keys:
        if channel_distance(rgb, key) <= 42:
            return True
        dominant = [idx for idx, value in enumerate(key) if value >= 192]
        suppressed = [idx for idx, value in enumerate(key) if value <= 63]
        if dominant and suppressed:
            values = (red, green, blue)
            if all(values[idx] >= 170 for idx in dominant) and all(values[idx] <= 125 for idx in suppressed):
                return True
    return False


def looks_like_cold_cyan_background(red: int, green: int, blue: int, alpha: int) -> bool:
    if alpha == 0:
        return True
    # Generated image tools often leave dark teal/cyan patterned corner backgrounds,
    # not only bright #00ffff pixels. These should be removable only when connected
    # to the canvas edge, so enclosed blue/green UI fills remain intact.
    if red < 100 and green > 18 and blue > 18 and (max(green, blue) - red) > 10 and abs(green - blue) < 115:
        return True
    if red < 190 and green > 110 and blue > 110 and (green - red) > 14 and (blue - red) > 10 and abs(green - blue) < 125:
        return True
    return False


def edge_mask(alpha: Image.Image, radius: int) -> Image.Image:
    visible = alpha.point(lambda a: 255 if a > 0 else 0, "L")
    transparent = alpha.point(lambda a: 255 if a == 0 else 0, "L")
    near_transparent = transparent.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    return ImageChops.multiply(visible, near_transparent)


def flood_remove_edge_background(
    image: Image.Image,
    keys: list[tuple[int, int, int]],
    cold_cyan: bool,
    min_visible_area: int,
) -> int:
    width, height = image.size
    pixels = image.load()
    queue: deque[tuple[int, int]] = deque()
    seen: set[tuple[int, int]] = set()
    visible_to_remove: list[tuple[int, int]] = []
    has_key_like_visible = False

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    removed = 0
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < width and 0 <= y < height):
            continue
        seen.add((x, y))
        red, green, blue, alpha = pixels[x, y]
        rgb = (red, green, blue)
        removable = alpha == 0 or looks_like_key(rgb, keys)
        if cold_cyan:
            removable = removable or looks_like_cold_cyan_background(red, green, blue, alpha)
        if not removable:
            continue
        if alpha != 0:
            visible_to_remove.append((x, y))
            has_key_like_visible = has_key_like_visible or looks_like_key(rgb, keys)
        for nx, ny in (
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
            (x - 1, y - 1),
            (x + 1, y - 1),
            (x - 1, y + 1),
            (x + 1, y + 1),
        ):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                queue.append((nx, ny))

    if len(visible_to_remove) < min_visible_area and not has_key_like_visible:
        return 0
    for x, y in visible_to_remove:
        red, green, blue, alpha = pixels[x, y]
        if alpha != 0:
            pixels[x, y] = (red, green, blue, 0)
            removed += 1
    return removed


def iterative_edge_cleanup(
    image: Image.Image,
    keys: list[tuple[int, int, int]],
    radius: int,
    passes: int,
    aggressive_cold_cyan: bool,
) -> int:
    removed = 0
    for _ in range(passes):
        mask = edge_mask(image.getchannel("A"), radius).load()
        pixels = image.load()
        step = 0
        for y in range(image.height):
            for x in range(image.width):
                if not mask[x, y]:
                    continue
                red, green, blue, alpha = pixels[x, y]
                if alpha == 0:
                    continue
                rgb = (red, green, blue)
                removable = looks_like_key(rgb, keys)
                if aggressive_cold_cyan:
                    removable = removable or looks_like_cold_cyan_background(red, green, blue, alpha)
                if removable:
                    pixels[x, y] = (red, green, blue, 0)
                    step += 1
        removed += step
        if step == 0:
            break
    return removed


def zero_transparent_rgb(image: Image.Image) -> int:
    pixels = image.load()
    changed = 0
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0 and (red or green or blue):
                pixels[x, y] = (0, 0, 0, 0)
                changed += 1
    return changed


def count_remaining(image: Image.Image, keys: list[tuple[int, int, int]], radius: int) -> tuple[int, int]:
    mask = edge_mask(image.getchannel("A"), radius).load()
    pixels = image.load()
    edge_key = 0
    transparent_nonzero = 0
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                if red or green or blue:
                    transparent_nonzero += 1
            elif mask[x, y] and looks_like_key((red, green, blue), keys):
                edge_key += 1
    return edge_key, transparent_nonzero


def collect_pngs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() == ".png" else []
    return sorted(input_path.rglob("*.png"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="PNG file or folder to clean in place.")
    parser.add_argument("--backup", type=Path, help="Optional folder for original PNG backups.")
    parser.add_argument("--report-json", type=Path, help="Optional path for a JSON cleanup report.")
    parser.add_argument("--key-color", action="append", type=parse_hex_color, help="Removable key color. Repeatable.")
    parser.add_argument("--edge-radius", type=int, default=4, help="Alpha-boundary radius to clean. Defaults to 4.")
    parser.add_argument("--passes", type=int, default=12, help="Max iterative edge cleanup passes. Defaults to 12.")
    parser.add_argument("--min-flood-area", type=int, default=16, help="Minimum edge-connected visible background pixels to remove. Defaults to 16.")
    parser.add_argument("--no-cold-cyan-background", action="store_true", help="Disable dark teal/cyan edge-background cleanup.")
    parser.add_argument(
        "--clean-visible-edge-key",
        action="store_true",
        help="Remove visible key-like pixels exposed directly on the alpha boundary.",
    )
    parser.add_argument(
        "--aggressive-edge-cold-cyan",
        action="store_true",
        help="Also remove cold-cyan pixels exposed on the alpha boundary; implies --clean-visible-edge-key and should be used only after visual QA.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Inspect only; do not write cleaned PNGs.")
    args = parser.parse_args()

    keys = args.key_color or list(DEFAULT_KEYS.values())
    pngs = collect_pngs(args.input)
    if not pngs:
        print(json.dumps({"processed": 0, "changed_files": 0, "files": []}, indent=2))
        return 0

    backup_root = args.backup
    stats: list[CleanStats] = []
    for png in pngs:
        image = Image.open(png).convert("RGBA")
        flood_removed = flood_remove_edge_background(
            image,
            keys,
            cold_cyan=not args.no_cold_cyan_background,
            min_visible_area=args.min_flood_area,
        )
        edge_removed = 0
        if args.clean_visible_edge_key or args.aggressive_edge_cold_cyan:
            edge_removed = iterative_edge_cleanup(
                image,
                keys,
                radius=args.edge_radius,
                passes=args.passes,
                aggressive_cold_cyan=args.aggressive_edge_cold_cyan,
            )
        transparent_fixed = zero_transparent_rgb(image)
        remaining_edge, remaining_transparent = count_remaining(image, keys, radius=args.edge_radius)

        if not args.dry_run and (flood_removed or edge_removed or transparent_fixed):
            if backup_root:
                rel = png.relative_to(args.input) if args.input.is_dir() else Path(png.name)
                backup_path = backup_root / rel
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(png, backup_path)
            image.save(png)

        stats.append(
            CleanStats(
                path=str(png),
                flood_removed=flood_removed,
                edge_removed=edge_removed,
                transparent_rgb_fixed=transparent_fixed,
                remaining_edge_key_pixels=remaining_edge,
                remaining_transparent_nonzero_rgb=remaining_transparent,
            )
        )

    payload = {
        "processed": len(stats),
        "changed_files": sum(
            1 for item in stats if item.flood_removed or item.edge_removed or item.transparent_rgb_fixed
        ),
        "remaining_edge_key_pixels": sum(item.remaining_edge_key_pixels for item in stats),
        "remaining_transparent_nonzero_rgb": sum(item.remaining_transparent_nonzero_rgb for item in stats),
        "files": [item.__dict__ for item in stats],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
