#!/usr/bin/env python3
"""Package existing PNG game UI assets into clean level folders.

This script does not generate creative art or remove backgrounds. It inspects,
copies, previews, and creates Godot scaffolding for assets produced by image tools.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


STATE_ALIASES = {
    "normal": {"normal", "default", "idle", "up"},
    "hover": {"hover", "over", "highlight", "focused", "focus", "selected"},
    "pressed": {"pressed", "down", "active", "click", "clicked"},
    "disabled": {"disabled", "disable", "locked", "inactive", "gray", "grey"},
}

TYPE_ALIASES = {
    "panel": {"panel", "window", "modal", "popup", "dialog", "card", "frame", "box", "bgpanel"},
    "button": {"button", "btn"},
    "progress_bar": {"progress", "bar", "meter", "gauge", "healthbar", "hpbar", "manabar", "slider"},
    "icon": {"icon", "badge", "coin", "gem", "item", "currency", "hudicon"},
    "slot": {"slot", "cell"},
}

PART_ALIASES = {
    "background": {"bg", "back", "background", "track", "under", "empty", "base"},
    "fill": {"fill", "filled", "value", "foreground", "fg", "front"},
    "frame": {"frame", "border", "rim"},
}

GENERIC_TOKENS = {"ui", "game", "asset", "sprite", "generated", "art", "texture", "png"}
KEY_COLOR_CANDIDATES = {
    "#ff00ff": (255, 0, 255),
    "#00ff00": (0, 255, 0),
    "#0000ff": (0, 0, 255),
}
VISIBLE_ALPHA_THRESHOLD = 16
KEY_RESIDUE_MIN_RATIO = 0.0005
KEY_RESIDUE_MIN_PIXELS = 8
MIN_TRANSPARENT_MARGIN = 2


@dataclass
class DetectedAsset:
    source: Path
    component_type: str
    component_name: str
    category: str
    state: str | None
    part: str | None
    output_name: str
    output_rel: str
    width: int
    height: int
    mode: str
    has_alpha: bool
    alpha_bbox: list[int] | None
    transparent_margin: dict[str, int] | None
    edge_alpha_touch: bool
    chroma_key_residue: list[dict[str, Any]]
    suggested_slice: dict[str, int] | None
    warnings: list[str]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "asset"


def pascal(value: str) -> str:
    words = re.split(r"[^a-zA-Z0-9]+", value)
    name = "".join(w[:1].upper() + w[1:] for w in words if w)
    return name or "GeneratedUi"


def tokenize(stem: str) -> list[str]:
    return [token for token in re.split(r"[^a-zA-Z0-9]+", stem.lower()) if token]


def alias_hit(tokens: list[str], aliases: dict[str, set[str]], default: str | None = None) -> str | None:
    token_set = set(tokens)
    for canonical, choices in aliases.items():
        if token_set & choices:
            return canonical
    return default


def detect_type(tokens: list[str]) -> str:
    detected = alias_hit(tokens, TYPE_ALIASES)
    if detected == "slot":
        return "panel"
    return detected or "image"


def detect_state(tokens: list[str]) -> str | None:
    return alias_hit(tokens, STATE_ALIASES)


def detect_part(component_type: str, tokens: list[str]) -> str | None:
    if component_type != "progress_bar":
        return None
    part = alias_hit(tokens, PART_ALIASES)
    if part:
        return part
    if "progress" in tokens or "bar" in tokens:
        return "fill"
    return None


def component_name(stem: str, tokens: list[str], component_type: str, state: str | None, part: str | None) -> str:
    remove = set(GENERIC_TOKENS)
    for canonical, choices in TYPE_ALIASES.items():
        if canonical == component_type or (canonical == "slot" and component_type == "panel"):
            if canonical == "icon":
                remove |= {"icon", "hudicon"}
            else:
                remove |= choices
    for choices in STATE_ALIASES.values():
        remove |= choices
    for choices in PART_ALIASES.values():
        remove |= choices
    kept = [token for token in tokens if token not in remove]
    if kept:
        return slugify("-".join(kept))
    if component_type == "progress_bar":
        return "progress"
    return slugify(component_type)


def detect_category(component_type: str, name: str, tokens: list[str]) -> str:
    token_set = set(tokens) | set(name.split("-"))
    if component_type == "button":
        return "buttons"
    if component_type == "progress_bar":
        return "bars"
    if component_type == "icon":
        return "icons"
    if "slot" in token_set or "cell" in token_set:
        return "slots"
    if "card" in token_set:
        return "cards"
    if "frame" in token_set or "border" in token_set or "rim" in token_set:
        return "frames"
    if "hud" in token_set:
        return "hud"
    if component_type == "panel":
        return "panels"
    return "images"


def suggest_slice(component_type: str, part: str | None, width: int, height: int) -> dict[str, int] | None:
    if component_type == "icon" or component_type == "image":
        return None
    if component_type == "progress_bar":
        x = max(4, min(32, round(height * 0.5), max(1, width // 3)))
        y = max(2, min(16, round(height * 0.25), max(1, height // 3)))
        return {"left": x, "top": y, "right": x, "bottom": y}
    shortest = max(1, min(width, height))
    margin = max(6, min(64, round(shortest * 0.2), max(1, width // 3), max(1, height // 3)))
    return {"left": margin, "top": margin, "right": margin, "bottom": margin}


def channel_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def looks_like_key_color(rgb: tuple[int, int, int], key: tuple[int, int, int]) -> bool:
    if channel_distance(rgb, key) <= 36:
        return True

    dominant = [idx for idx, value in enumerate(key) if value >= 192]
    suppressed = [idx for idx, value in enumerate(key) if value <= 63]
    if not dominant or not suppressed:
        return False

    return all(rgb[idx] >= 180 for idx in dominant) and all(rgb[idx] <= 110 for idx in suppressed)


def detect_chroma_key_residue(image) -> list[dict[str, Any]]:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    visible = 0
    counts = {key_hex: 0 for key_hex in KEY_COLOR_CANDIDATES}

    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha <= VISIBLE_ALPHA_THRESHOLD:
                continue
            visible += 1
            rgb = (red, green, blue)
            for key_hex, key_rgb in KEY_COLOR_CANDIDATES.items():
                if looks_like_key_color(rgb, key_rgb):
                    counts[key_hex] += 1

    if visible == 0:
        return []

    minimum = max(KEY_RESIDUE_MIN_PIXELS, int(visible * KEY_RESIDUE_MIN_RATIO))
    residue: list[dict[str, Any]] = []
    for key_hex, count in counts.items():
        if count >= minimum:
            residue.append(
                {
                    "key": key_hex,
                    "pixels": count,
                    "visible_pixels": visible,
                    "ratio": round(count / visible, 6),
                }
            )
    return residue


def inspect_png(path: Path, component_type: str, part: str | None) -> dict[str, Any]:
    warnings: list[str] = []
    with Image.open(path) as image:
        width, height = image.size
        mode = image.mode
        has_alpha = "A" in image.getbands()
        alpha_bbox = None
        transparent_margin = None
        edge_alpha_touch = False

        if has_alpha:
            alpha = image.getchannel("A")
            bbox = alpha.getbbox()
            if bbox:
                alpha_bbox = [int(v) for v in bbox]
                transparent_margin = {
                    "left": bbox[0],
                    "top": bbox[1],
                    "right": width - bbox[2],
                    "bottom": height - bbox[3],
                }
                edge_alpha_touch = (
                    bbox[0] == 0 or bbox[1] == 0 or bbox[2] == width or bbox[3] == height
                )
            else:
                warnings.append("alpha channel is fully transparent")
        else:
            warnings.append("image has no alpha channel")

        if width < 16 or height < 16:
            warnings.append("image is very small for game UI")
        if edge_alpha_touch:
            warnings.append("visible pixels touch canvas edge; inspect for clipped art and add transparent padding")
        elif transparent_margin:
            tight_sides = [
                side for side, margin in transparent_margin.items() if margin < MIN_TRANSPARENT_MARGIN
            ]
            if tight_sides:
                warnings.append(
                    "visible pixels are very close to canvas edge "
                    f"({', '.join(tight_sides)}); inspect for clipped art"
                )

        chroma_key_residue = detect_chroma_key_residue(image)
        for residue in chroma_key_residue:
            warnings.append(
                f"possible {residue['key']} chroma-key residue "
                f"({residue['pixels']} visible pixels); clean with soft matte/despill before packaging"
            )

        return {
            "width": width,
            "height": height,
            "mode": mode,
            "has_alpha": has_alpha,
            "alpha_bbox": alpha_bbox,
            "transparent_margin": transparent_margin,
            "edge_alpha_touch": edge_alpha_touch,
            "chroma_key_residue": chroma_key_residue,
            "suggested_slice": suggest_slice(component_type, part, width, height),
            "warnings": warnings,
        }


def detect_asset(path: Path) -> DetectedAsset:
    tokens = tokenize(path.stem)
    component_type = detect_type(tokens)
    state = detect_state(tokens)
    part = detect_part(component_type, tokens)
    name = component_name(path.stem, tokens, component_type, state, part)
    category = detect_category(component_type, name, tokens)

    role = state or part
    if component_type == "button" and role is None:
        role = "normal"
        state = "normal"
    if component_type == "progress_bar" and role is None:
        role = "fill"
        part = "fill"

    prefix = component_type.replace("_", "-")
    output_stem = f"{prefix}-{name}"
    if role:
        output_stem += f"__{slugify(role)}"
    output_name = f"{output_stem}.png"
    output_rel = f"png/{output_name}"

    info = inspect_png(path, component_type, part)
    return DetectedAsset(
        source=path,
        component_type=component_type,
        component_name=name,
        category=category,
        state=state,
        part=part,
        output_name=output_name,
        output_rel=output_rel,
        width=info["width"],
        height=info["height"],
        mode=info["mode"],
        has_alpha=info["has_alpha"],
        alpha_bbox=info["alpha_bbox"],
        transparent_margin=info["transparent_margin"],
        edge_alpha_touch=info["edge_alpha_touch"],
        chroma_key_residue=info["chroma_key_residue"],
        suggested_slice=info["suggested_slice"],
        warnings=info["warnings"],
    )


def unique_output_names(assets: list[DetectedAsset]) -> None:
    seen: dict[str, int] = {}
    for asset in assets:
        count = seen.get(asset.output_name, 0)
        seen[asset.output_name] = count + 1
        if count:
            stem = Path(asset.output_name).stem
            asset.output_name = f"{stem}-{count + 1}.png"
            asset.output_rel = f"png/{asset.output_name}"


def assign_output_paths(assets: list[DetectedAsset], asset_subdir: str, category_subdirs: bool = False) -> None:
    clean_subdir = asset_subdir.strip("/\\")
    for asset in assets:
        if category_subdirs:
            asset.output_rel = rel(f"{clean_subdir}/{asset.category}/{asset.output_name}")
        else:
            asset.output_rel = rel(f"{clean_subdir}/{asset.output_name}")


def rel(path: str) -> str:
    return path.replace("\\", "/")


def asset_record(asset: DetectedAsset) -> dict[str, Any]:
    return {
        "id": Path(asset.output_name).stem,
        "source": str(asset.source),
        "path": asset.output_rel,
        "type": asset.component_type,
        "component": asset.component_name,
        "category": asset.category,
        "state": asset.state,
        "part": asset.part,
        "width": asset.width,
        "height": asset.height,
        "mode": asset.mode,
        "has_alpha": asset.has_alpha,
        "alpha_bbox": asset.alpha_bbox,
        "transparent_margin": asset.transparent_margin,
        "edge_alpha_touch": asset.edge_alpha_touch,
        "chroma_key_residue": asset.chroma_key_residue,
        "suggested_slice": asset.suggested_slice,
        "warnings": asset.warnings,
    }


def build_components(assets: list[DetectedAsset]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[DetectedAsset]] = {}
    for asset in assets:
        grouped.setdefault((asset.component_type, asset.component_name), []).append(asset)

    components: list[dict[str, Any]] = []
    for (component_type, name), items in sorted(grouped.items()):
        first = items[0]
        component: dict[str, Any] = {
            "id": slugify(f"{component_type}-{name}"),
            "name": name,
            "type": component_type,
            "default_size": {"width": first.width, "height": first.height},
            "nine_slice": first.suggested_slice,
        }

        if component_type == "button":
            component["states"] = {item.state or "normal": item.output_rel for item in items}
            component["engine_hint"] = {
                "godot": "TextureButton",
                "unity": "Button + sliced Image",
                "cocos": "Button",
            }
            if "normal" not in component["states"]:
                component.setdefault("warnings", []).append("button has no normal state")
        elif component_type == "progress_bar":
            component["parts"] = {item.part or "fill": item.output_rel for item in items}
            component["engine_hint"] = {
                "godot": "TextureProgressBar",
                "unity": "Slider or Image fill",
                "cocos": "ProgressBar",
            }
            if "background" not in component["parts"]:
                component.setdefault("warnings", []).append("progress bar has no background/track")
            if "fill" not in component["parts"]:
                component.setdefault("warnings", []).append("progress bar has no fill")
        else:
            component["asset"] = first.output_rel
            component["engine_hint"] = {
                "godot": "NinePatchRect" if first.suggested_slice else "TextureRect",
                "unity": "sliced Image" if first.suggested_slice else "Image",
                "cocos": "Sprite",
            }
        components.append(component)

    return components


def copy_assets(assets: list[DetectedAsset], output_dir: Path, asset_subdir: str) -> None:
    for asset in assets:
        dest = output_dir / asset.output_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset.source, dest)


def write_preview(assets: list[DetectedAsset], output_dir: Path, name: str = "overview.png") -> Path | None:
    if not assets:
        return None
    thumb = 160
    label_h = 32
    cols = min(4, max(1, math.ceil(math.sqrt(len(assets)))))
    rows = math.ceil(len(assets) / cols)
    preview = Image.new("RGBA", (cols * thumb, rows * (thumb + label_h)), (32, 34, 38, 255))
    draw = ImageDraw.Draw(preview)
    for idx, asset in enumerate(assets):
        x = (idx % cols) * thumb
        y = (idx // cols) * (thumb + label_h)
        with Image.open(asset.source).convert("RGBA") as image:
            image.thumbnail((thumb - 16, thumb - 16), Image.Resampling.LANCZOS)
            px = x + (thumb - image.width) // 2
            py = y + (thumb - image.height) // 2
            checker = Image.new("RGBA", (thumb, thumb), (45, 48, 54, 255))
            preview.alpha_composite(checker, (x, y))
            preview.alpha_composite(image, (px, py))
        label = Path(asset.output_name).stem.replace("progress-bar", "bar").replace("__", ":")
        if len(label) > 20:
            label = label[:17] + "..."
        draw.text((x + 6, y + thumb + 4), label, fill=(235, 238, 242, 255))
    path = output_dir / name
    preview.save(path)
    return path


def write_manifest(
    pack_name: str,
    assets: list[DetectedAsset],
    components: list[dict[str, Any]],
    output_dir: Path,
    engines: list[str],
    write_file: bool = False,
) -> dict[str, Any]:
    warnings: list[str] = []
    for asset in assets:
        warnings.extend(f"{asset.output_name}: {warning}" for warning in asset.warnings)
    for component in components:
        warnings.extend(f"{component['id']}: {warning}" for warning in component.get("warnings", []))

    manifest = {
        "version": 1,
        "pack_name": pack_name,
        "engines": engines,
        "assets": [asset_record(asset) for asset in assets],
        "components": components,
        "warnings": warnings,
    }
    if write_file:
        (output_dir / "ui-asset-manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return manifest


def godot_res_path(res_prefix: str, rel_path: str) -> str:
    return f"{res_prefix.rstrip('/')}/{rel_path}"


def write_godot_outputs(manifest: dict[str, Any], output_dir: Path, res_prefix: str) -> None:
    godot_dir = output_dir / "godot"
    godot_dir.mkdir(parents=True, exist_ok=True)

    for component in manifest["components"]:
        node_name = pascal(component["id"])
        scene_name = f"{component['id']}.tscn"
        size = component["default_size"]
        slice_cfg = component.get("nine_slice") or {"left": 0, "top": 0, "right": 0, "bottom": 0}

        if component["type"] == "button":
            states = component.get("states", {})
            lines = [f'[gd_scene load_steps={len(states) + 1} format=3]']
            for idx, (state, path) in enumerate(sorted(states.items()), start=1):
                lines.append(f'[ext_resource type="Texture2D" path="{godot_res_path(res_prefix, path)}" id="{idx}_{state}"]')
            lines.append("")
            lines.append(f'[node name="{node_name}" type="TextureButton"]')
            lines.append(f"custom_minimum_size = Vector2({size['width']}, {size['height']})")
            for idx, (state, _path) in enumerate(sorted(states.items()), start=1):
                prop = {
                    "normal": "texture_normal",
                    "hover": "texture_hover",
                    "pressed": "texture_pressed",
                    "disabled": "texture_disabled",
                }.get(state)
                if prop:
                    lines.append(f'{prop} = ExtResource("{idx}_{state}")')
        elif component["type"] == "progress_bar":
            parts = component.get("parts", {})
            lines = [f'[gd_scene load_steps={len(parts) + 1} format=3]']
            for idx, (part, path) in enumerate(sorted(parts.items()), start=1):
                lines.append(f'[ext_resource type="Texture2D" path="{godot_res_path(res_prefix, path)}" id="{idx}_{part}"]')
            lines.append("")
            lines.append(f'[node name="{node_name}" type="TextureProgressBar"]')
            lines.append(f"custom_minimum_size = Vector2({size['width']}, {size['height']})")
            lines.append("max_value = 100.0")
            lines.append("value = 60.0")
            lines.append("nine_patch_stretch = true")
            for idx, (part, _path) in enumerate(sorted(parts.items()), start=1):
                if part == "background":
                    lines.append(f'texture_under = ExtResource("{idx}_{part}")')
                elif part == "fill":
                    lines.append(f'texture_progress = ExtResource("{idx}_{part}")')
            lines.append(f"stretch_margin_left = {slice_cfg['left']}")
            lines.append(f"stretch_margin_top = {slice_cfg['top']}")
            lines.append(f"stretch_margin_right = {slice_cfg['right']}")
            lines.append(f"stretch_margin_bottom = {slice_cfg['bottom']}")
        else:
            asset_path = component.get("asset")
            if not asset_path:
                continue
            node_type = "NinePatchRect" if component.get("nine_slice") else "TextureRect"
            lines = ["[gd_scene load_steps=2 format=3]"]
            lines.append(f'[ext_resource type="Texture2D" path="{godot_res_path(res_prefix, asset_path)}" id="1_tex"]')
            lines.append("")
            lines.append(f'[node name="{node_name}" type="{node_type}"]')
            lines.append(f"custom_minimum_size = Vector2({size['width']}, {size['height']})")
            lines.append('texture = ExtResource("1_tex")')
            if node_type == "NinePatchRect":
                lines.append(f"patch_margin_left = {slice_cfg['left']}")
                lines.append(f"patch_margin_top = {slice_cfg['top']}")
                lines.append(f"patch_margin_right = {slice_cfg['right']}")
                lines.append(f"patch_margin_bottom = {slice_cfg['bottom']}")

        (godot_dir / scene_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def unity_border(asset: dict[str, Any]) -> list[int]:
    slice_cfg = asset.get("suggested_slice") or {"left": 0, "top": 0, "right": 0, "bottom": 0}
    return [slice_cfg["left"], slice_cfg["bottom"], slice_cfg["right"], slice_cfg["top"]]


def write_unity_outputs(manifest: dict[str, Any], output_dir: Path, unity_root: str) -> None:
    unity_dir = output_dir / "unity"
    unity_dir.mkdir(parents=True, exist_ok=True)
    entries = [
        {"path": asset["path"], "border": unity_border(asset), "type": asset["type"]}
        for asset in manifest["assets"]
    ]
    (unity_dir / "unity_sprite_import.json").write_text(
        json.dumps({"pack_name": manifest["pack_name"], "root": unity_root, "entries": entries}, indent=2),
        encoding="utf-8",
    )

    array_lines = []
    for entry in entries:
        left, bottom, right, top = entry["border"]
        array_lines.append(
            f'        new Entry("{entry["path"]}", new Vector4({left}, {bottom}, {right}, {top})),'
        )

    class_name = pascal(f"{manifest['pack_name']}-ui-importer")
    script = f"""#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;

public static class {class_name}
{{
    private struct Entry
    {{
        public string Path;
        public Vector4 Border;
        public Entry(string path, Vector4 border) {{ Path = path; Border = border; }}
    }}

    private const string Root = "{unity_root}";
    private static readonly Entry[] Entries = new Entry[]
    {{
{chr(10).join(array_lines)}
    }};

    [MenuItem("Tools/Generated UI/Apply Sprite Import Settings/{manifest['pack_name']}")]
    public static void Apply()
    {{
        foreach (var entry in Entries)
        {{
            var assetPath = (Root + "/" + entry.Path).Replace("\\\\", "/");
            if (!File.Exists(assetPath))
            {{
                Debug.LogWarning("Missing UI asset: " + assetPath);
                continue;
            }}
            var importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null) continue;
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.spriteBorder = entry.Border;
            importer.SaveAndReimport();
        }}
        Debug.Log("Applied generated UI sprite settings for {manifest['pack_name']}.");
    }}
}}
#endif
"""
    (unity_dir / f"{class_name}.cs").write_text(script, encoding="utf-8")


def write_cocos_outputs(manifest: dict[str, Any], output_dir: Path) -> None:
    cocos_dir = output_dir / "cocos"
    cocos_dir.mkdir(parents=True, exist_ok=True)
    prefab_spec = {
        "pack_name": manifest["pack_name"],
        "asset_root": f"assets/generated-ui/{manifest['pack_name']}",
        "components": manifest["components"],
    }
    (cocos_dir / "ui_pack_prefab_spec.json").write_text(
        json.dumps(prefab_spec, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def copy_tree_contents(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for item in source.rglob("*"):
        rel_item = item.relative_to(source)
        dest = target / rel_item
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)


def install_to_project(output_dir: Path, project: Path, pack_name: str, engines: list[str]) -> list[str]:
    installed: list[str] = []
    if "godot" in engines and (project / "project.godot").exists():
        target = project / "assets" / "generated_ui" / pack_name
        copy_tree_contents(output_dir, target)
        installed.append(str(target))
    if "unity" in engines and (project / "Assets").exists():
        target = project / "Assets" / "GeneratedUI" / pack_name
        copy_tree_contents(output_dir, target)
        installed.append(str(target))
    if "cocos" in engines and ((project / "assets").exists() or (project / "project.json").exists()):
        target = project / "assets" / "generated-ui" / pack_name
        copy_tree_contents(output_dir, target)
        installed.append(str(target))
    return installed


def parse_engines(value: str) -> list[str]:
    if value.lower() == "all":
        return ["godot", "unity", "cocos", "generic"]
    allowed = {"godot", "unity", "cocos", "generic"}
    engines = [slugify(part) for part in value.split(",") if part.strip()]
    bad = [engine for engine in engines if engine not in allowed]
    if bad:
        raise SystemExit(f"Unsupported engine(s): {', '.join(bad)}")
    return engines or ["generic"]


def discover_levels(input_dir: Path) -> list[tuple[str, Path, list[Path]]]:
    direct_pngs = sorted(input_dir.glob("*.png"))
    child_levels: list[tuple[str, Path, list[Path]]] = []
    for child in sorted(input_dir.iterdir()):
        if not child.is_dir():
            continue
        pngs = sorted(child.glob("*.png"))
        if not pngs:
            continue
        slug = slugify(child.name)
        if not slug.startswith("level-"):
            slug = f"level-{len(child_levels) + 1:02d}-{slug}"
        child_levels.append((slug.replace("-", "_"), child, pngs))

    if child_levels:
        levels: list[tuple[str, Path, list[Path]]] = []
        if direct_pngs:
            levels.append(("level_00_root", input_dir, direct_pngs))
        levels.extend(child_levels)
        return levels
    if direct_pngs:
        return [("level_01_complete", input_dir, direct_pngs)]
    raise SystemExit(f"No PNG files found in {input_dir}")


def package_level(
    level_name: str,
    pngs: list[Path],
    output_dir: Path,
    pack_name: str,
    engines: list[str],
    asset_subdir: str,
    category_subdirs: bool,
    write_manifest_file: bool,
    godot_res_prefix: str | None,
    unity_root: str | None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets = [detect_asset(path) for path in pngs]
    unique_output_names(assets)
    assign_output_paths(assets, asset_subdir, category_subdirs=category_subdirs)
    copy_assets(assets, output_dir, asset_subdir)
    overview = write_preview(assets, output_dir)
    components = build_components(assets)
    manifest = write_manifest(pack_name, assets, components, output_dir, engines, write_file=write_manifest_file)

    if "godot" in engines:
        res_prefix = godot_res_prefix or f"res://assets/generated_ui/{pack_name}/{level_name}"
        write_godot_outputs(manifest, output_dir, res_prefix)
    if "unity" in engines:
        root = unity_root or f"Assets/GeneratedUI/{pack_name}/{level_name}"
        write_unity_outputs(manifest, output_dir, root)
    if "cocos" in engines:
        write_cocos_outputs(manifest, output_dir)

    return {
        "level": level_name,
        "output": str(output_dir),
        "assets": len(assets),
        "components": len(components),
        "warnings": len(manifest["warnings"]),
        "overview": str(overview) if overview else None,
    }


def write_root_overview(levels: list[dict[str, Any]], output_dir: Path) -> None:
    overview_paths = [(level["level"], Path(level["overview"])) for level in levels if level.get("overview")]
    overview_paths = [(name, path) for name, path in overview_paths if path.exists()]
    if not overview_paths:
        return

    thumb_w = 280
    thumb_h = 220
    label_h = 28
    cols = min(2, len(overview_paths))
    rows = math.ceil(len(overview_paths) / cols)
    canvas = Image.new("RGBA", (cols * thumb_w, rows * (thumb_h + label_h)), (28, 30, 34, 255))
    draw = ImageDraw.Draw(canvas)
    for idx, (level_name, path) in enumerate(overview_paths):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        with Image.open(path).convert("RGBA") as image:
            image.thumbnail((thumb_w - 16, thumb_h - 16), Image.Resampling.LANCZOS)
            canvas.alpha_composite(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        draw.text((x + 8, y + thumb_h + 4), level_name, fill=(238, 240, 244, 255))
    canvas.save(output_dir / "overview.png")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Folder containing generated PNG UI assets.")
    parser.add_argument("--output", required=True, type=Path, help="Output folder for packaged assets.")
    parser.add_argument("--pack-name", default="generated-ui", help="Slug used for output and engine folders.")
    parser.add_argument("--engines", default="godot", help="Comma list: godot,unity,cocos,generic or all. Defaults to godot.")
    parser.add_argument("--asset-subdir", default="png", help="PNG folder name inside each level. Defaults to png.")
    parser.add_argument("--category-subdirs", action="store_true", help="Organize PNGs under category folders such as png/buttons and png/icons.")
    parser.add_argument("--write-manifest", action="store_true", help="Write ui-asset-manifest.json for debugging. Off by default.")
    parser.add_argument("--project", type=Path, help="Optional game project root to receive generated files.")
    parser.add_argument(
        "--godot-res-prefix",
        help="Godot res:// prefix. Defaults to res://assets/generated_ui/<pack-name>.",
    )
    parser.add_argument(
        "--unity-root",
        help="Unity asset root. Defaults to Assets/GeneratedUI/<pack-name>.",
    )
    args = parser.parse_args(argv)

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    pack_name = slugify(args.pack_name)
    engines = parse_engines(args.engines)

    if not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    levels = discover_levels(input_dir)
    level_summaries: list[dict[str, Any]] = []
    for level_name, _level_dir, pngs in levels:
        level_output = output_dir / level_name
        level_summaries.append(
            package_level(
                level_name=level_name,
                pngs=pngs,
                output_dir=level_output,
                pack_name=pack_name,
                engines=engines,
                asset_subdir=args.asset_subdir,
                category_subdirs=args.category_subdirs,
                write_manifest_file=args.write_manifest,
                godot_res_prefix=args.godot_res_prefix,
                unity_root=args.unity_root,
            )
        )
    write_root_overview(level_summaries, output_dir)

    installed = []
    if args.project:
        installed = install_to_project(output_dir, args.project.resolve(), pack_name, engines)

    summary = {
        "pack_name": pack_name,
        "output": str(output_dir),
        "levels": level_summaries,
        "assets": sum(level["assets"] for level in level_summaries),
        "components": sum(level["components"] for level in level_summaries),
        "warnings": sum(level["warnings"] for level in level_summaries),
        "installed": installed,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
