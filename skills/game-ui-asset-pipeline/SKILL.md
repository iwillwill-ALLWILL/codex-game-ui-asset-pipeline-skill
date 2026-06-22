---
name: game-ui-asset-pipeline
description: Generate, extract, style-match, and package game-ready 2D UI component assets from prompts, uploaded reference images, stored user style references, or existing PNGs. Use when Codex needs to create or integrate panels, buttons, progress bars, HUD frames, inventory slots, icons, UI states, nine-slice textures, atlases, Godot scenes, Unity/Cocos outputs on request, clean level-based PNG folders, or a persistent style library from user-provided images/text. This skill should compose existing image generation, background removal, sprite, atlas, and editor/MCP tools instead of reimplementing them.
---

# Game UI Asset Pipeline

Create game UI asset packs that can be dropped into a project. This skill is a pipeline coordinator: use existing generators and engine tools for the heavy work, then use the bundled packager and style-library helper for clean level folders, overview images, Godot scaffolding, and reusable user-owned style references.

## Supported Modes

- Style-locked generation from references stored under `assets/style-library`.
- Direct generation from prompt or current reference image.
- Direct extraction from a user-uploaded UI screenshot or atlas into reusable components when the user wants visible elements from that exact image.
- Packaging existing PNG components into clean level folders with PNGs, `overview.png`, and Godot scaffolding by default. Generate JSON/Unity/Cocos outputs only when requested.
- Optional installation into a local Godot/Unity/Cocos project.

## Workflow

1. Identify the target.
   - Components: `panel`, `button`, `progress_bar`, `icon`, `frame`, `slot`, `hud`.
   - Engine: default to `godot` unless the user names `unity`, `cocos`, or `generic`.
   - Input mode: prompt-only, reference image, existing PNGs, stored style library, direct screenshot extraction, or mixed.
   - Component granularity: build an adaptive split ladder from the actual image. Output every useful level by default, from large reusable groups down to atomic parts. Do not force a fixed five-level scheme; omit mechanical empty levels and name folders by their semantic purpose.

2. If the user asks to store uploaded references for long-term reuse, ingest them into the skill style library.
   - Only store images/text the user explicitly provided and asked to reuse, remember, add to the skill, or "沉淀".
   - Run `scripts/ingest_style_reference.py ingest` to copy the files, extract a palette, and create a style card.
   - For future style-matched generation, run `scripts/ingest_style_reference.py list` or `show`, then inspect the stored reference images before prompting the image backend.

3. Reuse the right tool.
   - For raw raster art, use built-in `image_gen`, a local ComfyUI workflow, or the project's configured image backend.
   - For animated characters, effects, projectiles, or sprite sheets, use `$generate2dsprite`; do not reproduce its frame cleanup logic here.
   - For transparent cutouts, use an existing transparent-asset skill, `rembg`, LayerDiffuse, or the image backend's alpha workflow.
   - For atlas packing, use Free Texture Packer or an engine-native atlas builder when available.
   - For direct editor insertion, use Godot/Unity/Cocos MCP tools when installed; otherwise generate project files and import helpers.

4. Generate or extract component art as isolated assets.
   - Prefer one PNG per component or state: `panel_inventory.png`, `button_play_normal.png`, `button_play_hover.png`, `button_play_pressed.png`, `progress_health_bg.png`, `progress_health_fill.png`.
   - Avoid baked UI text unless explicitly requested; labels are usually engine text nodes.
   - Ask for clean orthographic UI art, no mockup screen, no perspective scene, no watermark, no drop shadow that crosses the canvas edge.
   - Prefer native transparent output. If a flat removable background is required, do not default blindly to `#FF00FF`; choose a key color that is absent from the reference/style palette.
   - For panels/buttons, ask for corners and borders that can survive 9-slice scaling.
   - For production UI packs, prefer style-library/reference-guided generation of isolated components over trying to reconstruct components from a full concept screenshot.
   - For direct screenshot extraction, crop/segment the actual UI pieces, remove background residue, strip unwanted text, and add transparent padding after trimming.
   - For uncertain screenshot edges, use conservative masks: crop with margin, expand/close the mask before matting, keep the full visible stroke, then trim only transparent padding. A slightly larger mask is easier to fix than a clipped frame edge.
   - When a frame blends into the background, is hidden by text, or is occluded by scene art, do not pretend the screenshot contains clean reusable source layers. Either mark the extracted asset as approximate, manually refine the mask, or regenerate that component from the stored style library.
   - For style-library generation, reuse palette hex values and visual rules from the selected style card across the whole batch.

5. Choose and clean the alpha/key background deliberately.
   - Run `scripts/suggest_key_color.py` on the reference image or style-library sources when native alpha is unavailable.
   - Use the recommended key color consistently in the generation prompt and cleanup command.
   - If the recommended key is still close to visible colors, switch to native alpha, LayerDiffuse, rembg/BiRefNet, or a custom key color rather than forcing a bad key.
   - Pink/green particles around UI pieces are chroma-key spill, not a normal trim problem. Remove the key color with a soft matte, despill, and a 1px edge contract before splitting atlases into components.
   - Reuse the installed `imagegen` helper when available; do not rewrite chroma-key removal.

```bash
python <skill-root>/scripts/suggest_key_color.py --input <reference-image-or-folder>

python <codex-home>/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input <raw-atlas-or-png> \
  --out <clean-alpha.png> \
  --key-color "<recommended-key-color>" \
  --soft-matte \
  --transparent-threshold 24 \
  --opaque-threshold 170 \
  --edge-contract 1 \
  --edge-feather 0.25 \
  --despill \
  --force
```

6. Package the PNGs into level folders.

```bash
python <skill-root>/scripts/package_ui_assets.py \
  --input <folder-with-pngs> \
  --output <output-folder> \
  --pack-name <slug> \
  --engines godot
```

If the input folder has subfolders, each subfolder is treated as one split level and packaged separately. Default public output contains no JSON; add `--write-manifest` only for debugging.

Add `--project <game-project-root>` when the game project is local and should receive generated files.

7. Integrate.
   - Godot default: use generated `.tscn` starter scenes; Godot UI stretch assets should become `NinePatchRect`, `TextureButton`, or `TextureProgressBar`.
   - Unity/Cocos/generic: generate only when explicitly requested to keep output focused.

8. QA before reporting done.
   - Open the root `overview.png` and each level's `overview.png`.
   - Keep the public output focused: `level_xxx/png`, `level_xxx/godot`, and overview images.
   - Treat `possible chroma-key residue` warnings as blockers for final delivery unless the color is intentional UI art.
   - Verify each button has at least a normal state, each progress bar has background/fill when possible, and stretchable components have reasonable slice margins.
   - Inspect cutout edges on dark and light backgrounds. If a frame loses visible pixels, add margin and rebuild the mask; if it includes scene-background pixels, use a tighter segmentation/matting pass.
   - If assets are blank, cropped, noisy, text-baked by accident, inconsistent across states, or only approximate because the concept screenshot is ambiguous, regenerate or clean them before integration.

## Resource Navigation

- Read `references/toolchain.md` when choosing between built-in image generation, ComfyUI, chroma-key cleanup, background removal, atlas packers, or MCP/editor integration.
- Read `references/component-contract.md` when naming assets, designing split levels, adjusting nine-slice margins, or mapping PNGs to a specific engine.
- Read `references/style-library.md` when the user asks to upload references, store style materials, keep palette/style consistent across components, extract UI from a screenshot, or generate from a stored game style.
- Run `scripts/package_ui_assets.py --help` for deterministic packaging options.
- Run `scripts/ingest_style_reference.py --help` for persistent style-library commands.
- Run `scripts/suggest_key_color.py --help` before chroma-key generation when the background key color is not obvious.

## Guardrails

- Do not generate creative UI art with Python, SVG, Canvas, CSS, or procedural placeholders. Scripts may only inspect, copy, preview, and package already-created raster assets.
- Do not hand-roll a diffusion backend, background remover, atlas packer, or engine editor bridge when a usable project tool exists.
- Do not treat a full UI mockup screenshot as a finished component pack. Extract or regenerate components separately so buttons, panels, and bars remain reusable.
- Do output every meaningful split level by default, from complete object down to atomic layers, but keep each level in its own folder so the result stays usable.
- Do not silently persist user images/text. Store them in the style library only when the user explicitly asks for long-term reuse or skill memory.
- Keep unrelated game implementation changes out of scope unless the user explicitly asks to wire the new UI into gameplay.
