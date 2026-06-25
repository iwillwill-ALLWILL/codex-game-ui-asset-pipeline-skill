#!/usr/bin/env python3
"""Resize generated UI PNGs for final in-game use.

The helper avoids the common failure where oversized generated assets are forced
down by an engine or browser and become noisy, muddy, or fringed. Transparent
PNGs are resized in premultiplied-alpha space, then alpha-0 RGB is cleared.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter


def parse_size(value: str) -> tuple[int, int]:
    raw = value.lower().replace("*", "x")
    parts = raw.split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("expected WIDTHxHEIGHT")
    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected integer WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("width and height must be positive")
    return width, height


def collect_pngs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".png":
            raise SystemExit(f"Input file is not a PNG: {input_path}")
        return [input_path]
    if not input_path.is_dir():
        raise SystemExit(f"Input path does not exist: {input_path}")
    return sorted(path for path in input_path.rglob("*.png") if path.is_file())


def compute_target(size: tuple[int, int], args: argparse.Namespace) -> tuple[int, int]:
    width, height = size
    if args.target_size:
        target = args.target_size
    elif args.scale:
        target = (max(1, round(width * args.scale)), max(1, round(height * args.scale)))
    else:
        ratios: list[float] = []
        if args.max_width:
            ratios.append(args.max_width / width)
        if args.max_height:
            ratios.append(args.max_height / height)
        if args.max_side:
            ratios.append(args.max_side / max(width, height))
        if not ratios:
            raise SystemExit("Provide --target-size, --scale, --max-side, --max-width, or --max-height")
        ratio = min(ratios)
        if args.skip_upscale and ratio >= 1:
            target = (width, height)
        else:
            target = (max(1, round(width * ratio)), max(1, round(height * ratio)))

    if args.skip_upscale and (target[0] > width or target[1] > height):
        return width, height
    return target


def resize_multistep(image: Image.Image, target: tuple[int, int]) -> Image.Image:
    resample = Image.Resampling.LANCZOS
    current = image
    target_width, target_height = target
    while current.width > target_width * 2 or current.height > target_height * 2:
        next_width = max(target_width, math.ceil(current.width / 2))
        next_height = max(target_height, math.ceil(current.height / 2))
        current = current.resize((next_width, next_height), resample)
    if current.size != target:
        current = current.resize(target, resample)
    return current


def premultiply(rgba: Image.Image) -> Image.Image:
    red, green, blue, alpha = rgba.split()
    return Image.merge(
        "RGBA",
        (
            ImageChops.multiply(red, alpha),
            ImageChops.multiply(green, alpha),
            ImageChops.multiply(blue, alpha),
            alpha,
        ),
    )


def unpremultiply(premultiplied: Image.Image) -> Image.Image:
    rgba = premultiplied.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                scale = 255.0 / alpha
                pixels[x, y] = (
                    min(255, round(red * scale)),
                    min(255, round(green * scale)),
                    min(255, round(blue * scale)),
                    alpha,
                )
    return rgba


def clear_transparent_rgb(rgba: Image.Image) -> Image.Image:
    image = rgba.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0 and (red or green or blue):
                pixels[x, y] = (0, 0, 0, 0)
    return image


def filter_rgb(image: Image.Image, image_filter: ImageFilter.Filter) -> Image.Image:
    red, green, blue, alpha = image.convert("RGBA").split()
    rgb = Image.merge("RGB", (red, green, blue)).filter(image_filter)
    red, green, blue = rgb.split()
    return Image.merge("RGBA", (red, green, blue, alpha))


def resize_rgba(image: Image.Image, target: tuple[int, int], args: argparse.Namespace) -> Image.Image:
    premul = premultiply(image.convert("RGBA"))
    if args.prefilter > 0:
        premul = filter_rgb(premul, ImageFilter.GaussianBlur(args.prefilter))
    resized = resize_multistep(premul, target)
    result = unpremultiply(resized)
    if not args.no_sharpen and args.unsharp_percent > 0:
        result = filter_rgb(
            result,
            ImageFilter.UnsharpMask(
                radius=args.unsharp_radius,
                percent=args.unsharp_percent,
                threshold=args.unsharp_threshold,
            ),
        )
    return clear_transparent_rgb(result)


def resize_opaque(image: Image.Image, target: tuple[int, int], args: argparse.Namespace) -> Image.Image:
    work = image.convert("RGB")
    if args.prefilter > 0:
        work = work.filter(ImageFilter.GaussianBlur(args.prefilter))
    work = resize_multistep(work, target)
    if not args.no_sharpen and args.unsharp_percent > 0:
        work = work.filter(
            ImageFilter.UnsharpMask(
                radius=args.unsharp_radius,
                percent=args.unsharp_percent,
                threshold=args.unsharp_threshold,
            )
        )
    return work


def output_path_for(path: Path, input_root: Path, args: argparse.Namespace) -> Path:
    if args.in_place:
        return path
    assert args.output is not None
    if input_root.is_file():
        relative = path.name
    else:
        relative = path.relative_to(input_root)
    return args.output / relative


def process_file(path: Path, input_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with Image.open(path) as opened:
        source = opened.copy()
    target = compute_target(source.size, args)
    output = output_path_for(path, input_root, args)
    output.parent.mkdir(parents=True, exist_ok=True)

    if target == source.size:
        if output != path:
            source.save(output)
        return {
            "source": str(path),
            "output": str(output),
            "source_size": list(source.size),
            "target_size": list(target),
            "changed": False,
        }

    if "A" in source.getbands():
        resized = resize_rgba(source, target, args)
    else:
        resized = resize_opaque(source, target, args)
    resized.save(output)
    return {
        "source": str(path),
        "output": str(output),
        "source_size": list(source.size),
        "target_size": list(target),
        "changed": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input PNG or folder of PNGs.")
    parser.add_argument("--output", type=Path, help="Output folder. Required unless --in-place is used.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite input PNGs in place.")
    parser.add_argument("--target-size", type=parse_size, help="Exact output size, e.g. 128x128.")
    parser.add_argument("--scale", type=float, help="Scale factor, e.g. 0.5.")
    parser.add_argument("--max-side", type=int, help="Limit the longest side to this many pixels.")
    parser.add_argument("--max-width", type=int, help="Limit width while preserving aspect ratio.")
    parser.add_argument("--max-height", type=int, help="Limit height while preserving aspect ratio.")
    parser.add_argument("--allow-upscale", dest="skip_upscale", action="store_false", help="Allow upscaling.")
    parser.set_defaults(skip_upscale=True)
    parser.add_argument("--prefilter", type=float, default=0.0, help="Small Gaussian blur before downscale, e.g. 0.12-0.25.")
    parser.add_argument("--no-sharpen", action="store_true", help="Disable mild post-resize unsharp mask.")
    parser.add_argument("--unsharp-radius", type=float, default=0.55)
    parser.add_argument("--unsharp-percent", type=int, default=45)
    parser.add_argument("--unsharp-threshold", type=int, default=4)
    parser.add_argument("--report-json", type=Path, help="Optional JSON report path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.output is None and not args.in_place:
        parser.error("provide --output or --in-place")
    if args.output is not None and args.in_place:
        parser.error("--output and --in-place are mutually exclusive")
    if args.scale is not None and args.scale <= 0:
        parser.error("--scale must be positive")

    input_root = args.input
    files = collect_pngs(input_root)
    results = [process_file(path, input_root, args) for path in files]
    report = {
        "input": str(args.input),
        "output": str(args.output) if args.output else None,
        "count": len(results),
        "changed": sum(1 for item in results if item["changed"]),
        "files": results,
    }
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"count": report["count"], "changed": report["changed"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
