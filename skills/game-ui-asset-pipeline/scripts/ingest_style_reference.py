#!/usr/bin/env python3
"""Store user-provided UI style references inside this skill.

The script copies explicitly supplied reference images/text into
assets/style-library/<style>/, extracts simple dominant color palettes from
images, and writes a small index plus a style card that later generations can
reuse for palette/style consistency.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:  # pragma: no cover - handled at runtime
    Image = None  # type: ignore[assignment]


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tga", ".gif"}
TEXT_EXTS = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".csv", ".toml", ".ini"}
DOC_EXTS = {".pdf", ".docx", ".pptx", ".xlsx"}
KEY_COLORS = {
    (255, 0, 255),
    (0, 255, 0),
    (0, 0, 255),
}
CURATION_ROLES = ("anchor", "support", "prompt", "accepted-output", "rejected", "noise")
DEFAULT_ROLE_WEIGHTS = {
    "anchor": 1.0,
    "accepted-output": 0.9,
    "support": 0.5,
    "prompt": 0.3,
    "rejected": 0.0,
    "noise": 0.0,
}
POSITIVE_STYLE_ROLES = {"anchor", "accepted-output", "support"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "style"


def skill_root(default: Path | None = None) -> Path:
    return (default or Path(__file__).resolve().parents[1]).resolve()


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def index_path(root: Path) -> Path:
    return root / "assets" / "style-library" / "index.json"


def load_index(root: Path) -> dict[str, Any]:
    path = index_path(root)
    if not path.exists():
        return {"version": 1, "styles": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_inputs(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if not resolved.exists():
            raise SystemExit(f"Input does not exist: {resolved}")
        if resolved.is_dir():
            for item in sorted(resolved.rglob("*")):
                if item.is_file():
                    found.append(item)
        elif resolved.is_file():
            found.append(resolved)
    return found


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTS:
        return "image"
    if suffix in TEXT_EXTS:
        return "text"
    if suffix in DOC_EXTS:
        return "document"
    return "other"


def safe_dest_name(path: Path, digest: str) -> str:
    stem = slugify(path.stem)[:64]
    suffix = path.suffix.lower()
    return f"{digest[:12]}-{stem}{suffix}"


def close_to_key(rgb: tuple[int, int, int]) -> bool:
    for key in KEY_COLORS:
        if max(abs(rgb[0] - key[0]), abs(rgb[1] - key[1]), abs(rgb[2] - key[2])) <= 36:
            return True
    return False


def sample_visible_pixels(path: Path, max_side: int = 220, max_pixels: int = 90000) -> tuple[list[tuple[int, int, int]], tuple[int, int]]:
    if Image is None:
        return [], (0, 0)

    with Image.open(path) as image:
        original_size = image.size
        image = image.convert("RGBA")
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        image.thumbnail((max_side, max_side), resample)
        pixels: list[tuple[int, int, int]] = []
        pixel_data = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
        for red, green, blue, alpha in pixel_data:
            if alpha <= 32:
                continue
            rgb = (red, green, blue)
            if close_to_key(rgb):
                continue
            pixels.append(rgb)

    if len(pixels) > max_pixels:
        step = math.ceil(len(pixels) / max_pixels)
        pixels = pixels[::step]
    return pixels, original_size


def quantize_palette(pixels: list[tuple[int, int, int]], limit: int = 12) -> list[dict[str, Any]]:
    if not pixels:
        return []

    if Image is None:
        bucketed = Counter((r // 16 * 16, g // 16 * 16, b // 16 * 16) for r, g, b in pixels)
        total = sum(bucketed.values())
        return [
            {"hex": f"#{r:02x}{g:02x}{b:02x}", "count": count, "ratio": round(count / total, 6)}
            for (r, g, b), count in bucketed.most_common(limit)
        ]

    swatch = Image.new("RGB", (len(pixels), 1))
    swatch.putdata(pixels)
    colors = max(1, min(limit, len(set(pixels))))
    method = getattr(getattr(Image, "Quantize", Image), "MEDIANCUT", 0)
    quantized = swatch.quantize(colors=colors, method=method)
    palette = quantized.getpalette() or []
    counts = quantized.getcolors(maxcolors=len(pixels)) or []
    total = sum(count for count, _index in counts) or 1

    result: list[dict[str, Any]] = []
    for count, index in sorted(counts, reverse=True):
        offset = index * 3
        if offset + 2 >= len(palette):
            continue
        red, green, blue = palette[offset], palette[offset + 1], palette[offset + 2]
        result.append(
            {
                "hex": f"#{red:02x}{green:02x}{blue:02x}",
                "count": int(count),
                "ratio": round(count / total, 6),
            }
        )
    return result[:limit]


def read_notes(args: argparse.Namespace) -> str:
    chunks: list[str] = []
    if args.notes:
        chunks.append(args.notes.strip())
    if args.notes_file:
        chunks.append(args.notes_file.read_text(encoding="utf-8", errors="replace").strip())
    return "\n\n".join(chunk for chunk in chunks if chunk)


def read_prompts(args: argparse.Namespace) -> list[str]:
    prompts: list[str] = []
    for prompt in args.prompt or []:
        prompt = prompt.strip()
        if prompt:
            prompts.append(prompt)
    for prompt_file in args.prompt_file or []:
        text = prompt_file.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            prompts.append(text)
    return prompts


def read_avoid_items(args: argparse.Namespace, notes: str) -> list[str]:
    items = [(item or "").strip() for item in args.avoid or []]
    if args.role in {"rejected", "noise"} and notes.strip():
        items.append(notes.strip())
    return [item for item in items if item]


def resolved_role_weight(role: str, explicit_weight: float | None) -> float:
    if explicit_weight is None:
        return DEFAULT_ROLE_WEIGHTS.get(role, 0.5)
    return max(0.0, min(1.0, explicit_weight))


def positive_style_record(record: dict[str, Any]) -> bool:
    role = record.get("role", "support")
    try:
        weight = float(record.get("style_weight", DEFAULT_ROLE_WEIGHTS.get(role, 0.5)))
    except (TypeError, ValueError):
        weight = 0.0
    return role in POSITIVE_STYLE_ROLES and weight > 0


def text_excerpt(path: Path, max_chars: int = 2400) -> str:
    if file_kind(path) != "text":
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n..."
    return text


def write_style_card(
    root: Path,
    style_dir: Path,
    entry: dict[str, Any],
    palette: dict[str, Any],
    notes: str,
    prompts: list[dict[str, Any]],
    text_notes: list[dict[str, str]],
    avoid_list: list[str],
) -> None:
    path = style_dir / "style-card.md"
    manual_notes = ""
    marker = "\n## Manual Style Notes\n"
    if path.exists():
        old = path.read_text(encoding="utf-8", errors="replace")
        if marker in old:
            manual_notes = old.split(marker, 1)[1].strip()

    colors = palette.get("aggregate", {}).get("colors", [])
    palette_lines = [
        f"- `{color['hex']}` ratio `{color['ratio']}`"
        for color in colors[:12]
    ] or ["- No image palette extracted."]
    grouped_files: dict[str, list[str]] = {role: [] for role in CURATION_ROLES}
    for item in entry.get("files", []):
        role = item.get("role", "support")
        if role not in grouped_files:
            grouped_files[role] = []
        weight = item.get("style_weight", DEFAULT_ROLE_WEIGHTS.get(role, 0.5))
        grouped_files[role].append(
            f"- `{item['path']}` ({item['kind']}, role `{role}`, weight `{weight}`, sha256 `{item['sha256'][:12]}`)"
        )
    file_sections: list[str] = []
    for role in CURATION_ROLES:
        lines = grouped_files.get(role, [])
        if not lines:
            continue
        file_sections.append(f"### {role}\n\n" + "\n".join(lines))
    file_lines = "\n\n".join(file_sections) if file_sections else "No stored files."
    avoid_lines = [f"- {item}" for item in avoid_list] or ["- No avoid-list items recorded."]
    text_lines: list[str] = []
    for item in text_notes:
        text_lines.append(f"### {item['name']}\n\n```text\n{item['excerpt']}\n```")
    prompt_lines: list[str] = []
    for idx, prompt in enumerate(prompts[-12:], start=max(1, len(prompts) - 11)):
        title = prompt.get("title") or f"Prompt {idx}"
        body = prompt.get("text", "")
        prompt_lines.append(f"### {title}\n\n```text\n{body}\n```")

    content = f"""# {entry['title']}

Style slug: `{entry['slug']}`
Updated: `{entry['updated_at']}`
Tags: `{', '.join(entry.get('tags', [])) or 'none'}`

## User Notes

{notes or 'No explicit user notes recorded.'}

## Stored References

{file_lines}

## Style Lock Precedence

Positive style evidence order: explicit user requirement > this style card > accepted outputs > anchor references > support references > prompt bank > broad docs. Rejected and noise entries are negative evidence only and must not affect palette extraction or positive style prompts.

## Extracted Palette

{chr(10).join(palette_lines)}

## Avoid List

{chr(10).join(avoid_lines)}

## Text Reference Excerpts

{chr(10).join(text_lines) if text_lines else 'No text excerpts recorded.'}

## Reference Prompt Bank

{chr(10).join(prompt_lines) if prompt_lines else 'No reference prompts recorded.'}

## Generation Anchor

When this style is selected, inspect the stored reference images before generation, reuse the extracted palette as hard color guidance, and keep line weight, material treatment, corner language, icon silhouette language, and ornament density consistent across every UI component in the same batch.

## Self-Organization Rules

- Treat new user-approved images, notes, and prompts as additive evidence for this project style.
- Prefer recurring traits across multiple references over one-off details from a single image.
- Keep a stable style lock: palette roles, line weight, material language, corner shapes, icon rules, button states, and avoid-list.
- When a generated result is accepted by the user, store its prompt or final component sheet as a stronger reference for future batches.
- When a generated result is rejected, add the failure reason to the avoid-list instead of deleting useful references.
- Do not let rejected/noise entries influence palette or positive prompt construction.

## Manual Style Notes

{manual_notes or 'Add concise visual traits after inspecting the references: palette role, linework, shapes, materials, UI corner treatment, icon rules, and avoid-list.'}
"""
    path.write_text(content, encoding="utf-8")


def append_prompt_bank(style_dir: Path, entry: dict[str, Any], new_prompts: list[str]) -> list[dict[str, Any]]:
    path = style_dir / "reference-prompts.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "style": entry["slug"], "prompts": []}
    prompts = data.setdefault("prompts", [])
    existing = {item.get("sha256") for item in prompts}
    now = now_iso()
    for prompt in new_prompts:
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if digest in existing:
            continue
        prompts.append(
            {
                "title": f"Reference Prompt {len(prompts) + 1}",
                "text": prompt,
                "sha256": digest,
                "added_at": now,
            }
        )
        existing.add(digest)
    save_json(path, data)
    md_lines = [f"# {entry['title']} Reference Prompts", ""]
    for item in prompts:
        md_lines.append(f"## {item.get('title', 'Prompt')}")
        md_lines.append("")
        md_lines.append("```text")
        md_lines.append(item.get("text", ""))
        md_lines.append("```")
        md_lines.append("")
    (style_dir / "reference-prompts.md").write_text("\n".join(md_lines), encoding="utf-8")
    return prompts


def ingest(args: argparse.Namespace) -> int:
    root = skill_root(args.skill_root)
    library_dir = root / "assets" / "style-library"
    style_slug = slugify(args.style)
    style_dir = library_dir / style_slug
    role = args.role
    style_weight = resolved_role_weight(role, args.weight)
    sources_dir = style_dir / ("rejections" if role in {"rejected", "noise"} else "sources")
    sources_dir.mkdir(parents=True, exist_ok=True)

    now = now_iso()
    inputs = discover_inputs(args.input)
    idx = load_index(root)
    styles = idx.setdefault("styles", {})
    entry = styles.get(style_slug, {})
    existing_hashes = {item.get("sha256") for item in entry.get("files", [])}
    files = list(entry.get("files", []))
    copied = 0
    text_notes: list[dict[str, str]] = []

    for source in inputs:
        digest = sha256_file(source)
        if digest in existing_hashes:
            continue
        kind = file_kind(source)
        dest = sources_dir / safe_dest_name(source, digest)
        shutil.copy2(source, dest)
        copied += 1
        record = {
            "path": rel(dest, root),
            "original_path": str(source),
            "name": source.name,
            "kind": kind,
            "sha256": digest,
            "bytes": source.stat().st_size,
            "added_at": now,
            "role": role,
            "style_weight": style_weight,
        }
        files.append(record)
        existing_hashes.add(digest)
        excerpt = text_excerpt(source)
        if excerpt:
            text_notes.append({"name": source.name, "excerpt": excerpt})

    image_records: list[dict[str, Any]] = []
    aggregate_pixels: list[tuple[int, int, int]] = []
    for record in files:
        if record.get("kind") != "image":
            continue
        if not positive_style_record(record):
            continue
        image_path = root / record["path"]
        pixels, size = sample_visible_pixels(image_path)
        aggregate_pixels.extend(pixels)
        image_records.append(
            {
                "path": record["path"],
                "width": size[0],
                "height": size[1],
                "sampled_pixels": len(pixels),
                "colors": quantize_palette(pixels, limit=10),
            }
        )
    if len(aggregate_pixels) > 160000:
        step = math.ceil(len(aggregate_pixels) / 160000)
        aggregate_pixels = aggregate_pixels[::step]

    palette = {
        "version": 1,
        "style": style_slug,
        "updated_at": now,
        "aggregate": {
            "sampled_pixels": len(aggregate_pixels),
            "colors": quantize_palette(aggregate_pixels, limit=16),
        },
        "images": image_records,
    }
    save_json(style_dir / "palette.json", palette)

    notes = read_notes(args)
    new_prompts = read_prompts(args)
    new_avoid_items = read_avoid_items(args, notes)
    previous_notes = entry.get("notes", "")
    merged_notes = notes or previous_notes
    avoid_list = list(entry.get("avoid_list", []))
    existing_avoid = set(avoid_list)
    for item in new_avoid_items:
        if item not in existing_avoid:
            avoid_list.append(item)
            existing_avoid.add(item)
    tags = sorted(set(entry.get("tags", [])) | {slugify(tag) for tag in args.tag})
    role_counts: dict[str, int] = {}
    for item in files:
        item_role = item.get("role", "support")
        role_counts[item_role] = role_counts.get(item_role, 0) + 1
    entry = {
        "slug": style_slug,
        "title": args.title or entry.get("title") or args.style,
        "created_at": entry.get("created_at") or now,
        "updated_at": now,
        "tags": tags,
        "notes": merged_notes,
        "avoid_list": avoid_list,
        "path": rel(style_dir, root),
        "style_card": rel(style_dir / "style-card.md", root),
        "palette_file": rel(style_dir / "palette.json", root),
        "files": files,
        "role_counts": role_counts,
        "image_count": sum(1 for item in files if item.get("kind") == "image"),
        "text_count": sum(1 for item in files if item.get("kind") == "text"),
        "document_count": sum(1 for item in files if item.get("kind") == "document"),
        "palette": palette["aggregate"]["colors"][:12],
    }
    prompts = append_prompt_bank(style_dir, entry, new_prompts)
    entry["prompt_count"] = len(prompts)
    entry["prompt_bank"] = rel(style_dir / "reference-prompts.md", root)
    styles[style_slug] = entry
    save_json(index_path(root), idx)
    write_style_card(root, style_dir, entry, palette, merged_notes, prompts, text_notes, avoid_list)

    print(
        json.dumps(
            {
                "style": style_slug,
                "role": role,
                "style_weight": style_weight,
                "copied": copied,
                "files": len(files),
                "image_count": entry["image_count"],
                "prompt_count": entry["prompt_count"],
                "avoid_count": len(avoid_list),
                "palette_colors": len(entry["palette"]),
                "style_card": str(style_dir / "style-card.md"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def list_styles(args: argparse.Namespace) -> int:
    root = skill_root(args.skill_root)
    idx = load_index(root)
    for slug, entry in sorted(idx.get("styles", {}).items()):
        tags = ", ".join(entry.get("tags", []))
        role_counts = ", ".join(f"{role}:{count}" for role, count in sorted(entry.get("role_counts", {}).items()))
        print(f"{slug}\t{entry.get('title', slug)}\timages={entry.get('image_count', 0)}\troles={role_counts or 'none'}\ttags={tags}")
    return 0


def show_style(args: argparse.Namespace) -> int:
    root = skill_root(args.skill_root)
    idx = load_index(root)
    slug = slugify(args.style)
    entry = idx.get("styles", {}).get(slug)
    if not entry:
        raise SystemExit(f"Style not found: {slug}")
    if args.format == "json":
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0

    colors = ", ".join(color["hex"] for color in entry.get("palette", [])[:10]) or "none"
    print(f"# {entry.get('title', slug)}")
    print(f"slug: {slug}")
    print(f"style_card: {root / entry['style_card']}")
    print(f"palette: {colors}")
    print("references:")
    for item in entry.get("files", []):
        role = item.get("role", "support")
        weight = item.get("style_weight", DEFAULT_ROLE_WEIGHTS.get(role, 0.5))
        print(f"- {root / item['path']} role={role} weight={weight}")
    avoid_list = entry.get("avoid_list", [])
    if avoid_list:
        print("avoid_list:")
        for item in avoid_list:
            print(f"- {item}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, help="Override skill root. Defaults to this script's parent skill.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Copy user references into the style library.")
    ingest_parser.add_argument("--style", required=True, help="Style slug or human name.")
    ingest_parser.add_argument("--title", help="Human title for the style.")
    ingest_parser.add_argument("--input", action="append", required=True, type=Path, help="File or folder to ingest. Repeatable.")
    ingest_parser.add_argument("--notes", help="User-provided notes to store with this style.")
    ingest_parser.add_argument("--notes-file", type=Path, help="Text/Markdown notes file to store with this style.")
    ingest_parser.add_argument("--prompt", action="append", help="User-provided reference prompt to store with this style. Repeatable.")
    ingest_parser.add_argument("--prompt-file", action="append", type=Path, help="Text/Markdown prompt file to store with this style. Repeatable.")
    ingest_parser.add_argument("--role", choices=CURATION_ROLES, default="support", help="Curated role for these inputs. Rejected/noise items do not affect palette extraction.")
    ingest_parser.add_argument("--weight", type=float, help="Optional style influence weight from 0.0 to 1.0. Defaults depend on --role.")
    ingest_parser.add_argument("--avoid", action="append", help="Avoid-list lesson to store with this style. Repeatable.")
    ingest_parser.add_argument("--tag", action="append", default=[], help="Search tag. Repeatable.")
    ingest_parser.set_defaults(func=ingest)

    list_parser = subparsers.add_parser("list", help="List stored style entries.")
    list_parser.set_defaults(func=list_styles)

    show_parser = subparsers.add_parser("show", help="Show one style entry for prompt construction.")
    show_parser.add_argument("--style", required=True)
    show_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    show_parser.set_defaults(func=show_style)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
