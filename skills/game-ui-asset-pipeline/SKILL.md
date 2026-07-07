---
name: game-ui-asset-pipeline
description: Use when Codex needs game-ready 2D UI assets from prompts, references, screenshots, existing PNGs, or style libraries, including full UI kits, panels, buttons, bars, HUD frames, slots, icons, UI states, simple UI frame animations, nine-slice textures, atlases, engine-ready PNG folders, or persistent style libraries.
---

# Game UI Asset Pipeline

Create game UI asset packs that can be dropped into a project. This skill is a pipeline coordinator: use existing generators and engine tools for the heavy work, then use the bundled packager and style-library helper for clean folders, overview images, target-engine scaffolding, complete common component catalogs, simple UI frame animations, and reusable user-owned project style libraries.

## Supported Modes

- Project style-library driven generation from curated references stored under `assets/style-library`.
- Full common UI kit generation from the bundled, source-grounded component catalog.
- Direct generation from prompt or current reference image.
- Direct extraction from a user-uploaded UI screenshot or atlas into reusable components when the user wants visible elements from that exact image.
- Simple UI frame animations and animated UI component states, such as button pulse, icon glow, reward shine, progress fill sweep, loading spinner, notification ping, panel open/close, or subtle HUD shimmer.
- Packaging existing PNG components into clean level folders with PNGs, `overview.png`, and target-engine scaffolding after detecting or confirming the engine.
- Optional installation into a local Godot/Unity/Cocos project, or generic PNG export for H5/other stacks.

## Workflow

1. Identify the target.
   - Components: `panel`, `button`, `progress_bar`, `icon`, `frame`, `slot`, `hud`.
   - Engine: if a local game project root is available, inspect it before asking. Detect `godot` from `project.godot`, `unity` from `Assets` plus `ProjectSettings` or `Packages/manifest.json`, `cocos` from `project.json` or `assets/settings/package.json`, and `generic` from H5/web markers such as `index.html`, `package.json`, `src`, `public`, or Vite/Next config. Ask the user only when there is no project root, detection finds multiple engine roots, detection fails, or the user wants to override the detected target.
   - Input mode: prompt-only, reference image, existing PNGs, stored style library, direct screenshot extraction, or mixed.
   - Generation scope: full common UI kit, requested component subset, requested material/icon assets, existing PNG packaging, or concept screenshot extraction.
   - Motion scope: static component, state set, or simple UI animation. For animation, ask whether it is a loop or one-shot, desired FPS, frame count, and target engine.
   - Component granularity: build an adaptive split ladder from the actual image. Output every useful level by default, from large reusable groups down to atomic parts. Do not force a fixed five-level scheme; omit mechanical empty levels and name folders by their semantic purpose.

2. If the user asks to store uploaded references for long-term reuse, ingest them into the skill style library.
   - Only store images/text the user explicitly provided and asked to reuse, remember, add to the skill, or "沉淀".
   - Treat the style library as project memory, not a single static prompt. It can contain reference images, text notes, reference prompts, accepted generated outputs, rejected-output lessons, palette data, and manual style rules.
   - When many files are uploaded, curate before ingesting: classify each useful input as `anchor`, `accepted-output`, `support`, `prompt`, `rejected`, or `noise`; keep only the strongest positive references in the style lock and turn noise/rejections into avoid-list lessons.
   - Run `scripts/ingest_style_reference.py ingest` to copy the files, extract a palette, store reference prompts, and create/update a style card.
   - For future style-matched generation, run `scripts/ingest_style_reference.py list` or `show`, then inspect the stored reference images before prompting the image backend.
   - Let the library self-organize over time: update tags, palette roles, prompt bank, avoid-list, component naming habits, accepted generation anchors, and source weights when the user approves or rejects outputs.

3. Reuse the right tool.
   - For raw raster art, use built-in `image_gen`, a local ComfyUI workflow, or the project's configured image backend.
   - For simple UI motion, stay in this skill when the subject is a UI component or UI feedback: button pulse, icon glow, spinner, loading sweep, reward shine, panel open/close, badge pop, hover/pressed transition, or HUD shimmer.
   - For animated characters, combat effects, projectiles, impacts, summons, or long sprite sheets, use `$generate2dsprite`; do not reproduce its frame cleanup logic here.
   - For transparent cutouts, use an existing transparent-asset skill, `rembg`, LayerDiffuse, or the image backend's alpha workflow.
   - For atlas packing, use Free Texture Packer or an engine-native atlas builder when available.
   - For direct editor insertion, use Godot/Unity/Cocos MCP tools when installed; otherwise generate project files and import helpers.

4. Generate or extract component art as isolated assets.
   - Prefer one PNG per component or state: `panel_inventory.png`, `button_play_normal.png`, `button_play_hover.png`, `button_play_pressed.png`, `progress_health_bg.png`, `progress_health_fill.png`.
   - For a full UI kit or "常用 UI" request, read `references/ui-component-catalog.md`, choose the `complete` or project-specific checklist, map every item to a known control/game UI archetype, and generate in category batches when needed.
   - Avoid baked UI text unless explicitly requested; labels are usually engine text nodes.
   - Ask for clean orthographic UI art, no mockup screen, no perspective scene, no watermark, no drop shadow that crosses the canvas edge.
   - Prefer native transparent output. If a flat removable background is required, do not default blindly to `#FF00FF`; choose a key color that is absent from the reference/style palette.
   - For panels/buttons, ask for corners and borders that can survive 9-slice scaling.
   - For production UI packs, prefer style-library/reference-guided generation of isolated components over trying to reconstruct components from a full concept screenshot.
   - For direct screenshot extraction, crop/segment the actual UI pieces, remove background residue, strip unwanted text, and add transparent padding after trimming.
   - For uncertain screenshot edges, use conservative masks: crop with margin, expand/close the mask before matting, keep the full visible stroke, then trim only transparent padding. A slightly larger mask is easier to fix than a clipped frame edge.
   - When a frame blends into the background, is hidden by text, or is occluded by scene art, do not pretend the screenshot contains clean reusable source layers. Either mark the extracted asset as approximate, manually refine the mask, or regenerate that component from the stored style library.
   - For style-library generation, reuse palette hex values and visual rules from the selected style card across the whole batch.
   - For final component packs, one PNG means one semantic component. After atlas/sheet slicing and cleanup, run alpha connected-component QA to catch multiple large disconnected subjects, half-neighbor fragments, sticky leftover strips, and edge scraps. Remove fragments only when the remaining component is visually complete; do not ship a PNG containing two partial UI pieces.
   - For generated UI sheets/atlases, inspect the raw sheet layout before slicing. Do not assume a fixed grid when rows have different column counts or cells vary in size. Slice by true separator lines, cell bounds, or foreground component bounds from the original generated sheet. If fixed-grid slicing produced sticky neighbors or half-missing components, discard those derived crops and re-slice from the raw sheet.
   - Do not use "keep only the largest connected component" as a blanket cleanup for panels, frames, buttons, or HUD widgets. A single UI component may contain disconnected rivets, ornaments, frame sides, glow, or internal line art. Use connected-component analysis to find candidates for visual review, then remove only obvious background/separator scraps or regenerate/reslice from the original sheet.
   - For simple UI animations, generate or derive a stable frame sequence from the component art. Keep the canvas size, anchor, padding, and component bounds identical across frames.
   - Prefer subtle UI motion: alpha glow, scale pulse, sparkle sweep, fill movement, highlight shimmer, state transition, or small decorative particles. Avoid changing the component design frame-to-frame.
   - For labels, keep text out of baked frames unless the user explicitly requests text art. Animated buttons should usually animate the blank button, glow layer, fill, icon, or overlay while the engine renders text.
   - For nine-slice panels and buttons, avoid animating the stretchable border if a separate overlay, shine, glow, or fill layer can carry the motion. Static stretchable base plus animated overlay is easier to integrate than many full-panel frames.
   - Name animation frames predictably, such as `button_play_pulse_00.png`, `button_play_pulse_01.png`, or `icon_coin_glow_00.png`. Also export a static fallback PNG and a `preview.gif` or contact sheet.

5. Resolve final pixel size before packaging or engine import.
   - Do not rely on the engine, editor, or browser to force huge generated PNGs down to final UI size. Large one-step runtime scaling can turn painterly texture, bevels, antialiasing, and small ornaments into noisy muddy pixels.
   - Prefer generating close to the intended final size, or generate a controlled 2x/3x source and downsample once during the asset pipeline.
   - Crop/trim to the true component bounds first, add transparent padding, then resize. Do not resize a large sheet with empty gutters and then slice it.
   - Prefer mature open-source resize implementations when they are available: OpenCV `INTER_AREA` for decimation, libvips/sharp Lanczos resizing with alpha premultiplication, or ImageMagick filtered resize/unsharp chains. Use the bundled helper as the portable fallback.
   - For transparent PNGs, resize with premultiplied alpha so dark/colored transparent pixels cannot bleed into the edge.
   - For severe reductions, use area/box pre-shrink plus Lanczos final resize, edge-aware flat-area denoise, and mild post-sharpening. Avoid nearest-neighbor, a single bilinear shrink, or blur-only cleanup for UI art.
   - For panels/buttons/frames intended for nine-slice, do not uniformly shrink an already-large complete panel when that destroys corners and border detail. Prefer resizing source art to the target cap size, then use engine nine-slice for larger layout sizes.
   - Keep important final asset sizes as named exports, such as `icon-coin__64.png`, `icon-coin__128.png`, or `panel-inventory__512x256.png`, instead of one oversized source reused everywhere.

```bash
python <skill-root>/scripts/resize_assets_high_quality.py \
  --input <clean-alpha-png-folder> \
  --output <final-size-png-folder> \
  --max-side 512 \
  --denoise auto \
  --sampler area-lanczos \
  --prefilter 0.18
```

6. Choose and clean the alpha/key background deliberately.
   - Run `scripts/suggest_key_color.py` on the reference image or style-library sources when native alpha is unavailable.
   - Use the recommended key color consistently in the generation prompt and cleanup command.
   - If the recommended key is still close to visible colors, switch to native alpha, LayerDiffuse, rembg/BiRefNet, or a custom key color rather than forcing a bad key.
   - Pink/green particles around UI pieces are chroma-key spill, not a normal trim problem. Remove the key color with a soft matte, despill, and a 1px edge contract before splitting atlases into components.
   - Reuse the installed `imagegen` helper when available; do not rewrite chroma-key removal.
   - After chroma-key cleanup, also remove edge-connected teal/cyan background patches and hidden key-color RGB in fully transparent pixels. A PNG can look transparent but still leak cyan through image viewers or game texture filtering if alpha-0 pixels keep key-colored RGB.

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

python <skill-root>/scripts/clean_alpha_fringe.py \
  --input <folder-or-png> \
  --backup <backup-folder> \
  --report-json <qa-report.json>
```

7. Package the PNGs into level folders.

```bash
python <skill-root>/scripts/package_ui_assets.py \
  --input <folder-with-pngs> \
  --output <output-folder> \
  --pack-name <slug> \
  --engines auto \
  --project <game-project-root> \
  --category-subdirs
```

When a local project exists, use `--project <game-project-root>` and leave `--engines auto` so the script detects the engine and installs to the matching project structure. If the user explicitly chose Godot, Unity, Cocos, or generic, pass `--engines godot`, `--engines unity`, `--engines cocos`, or `--engines generic`. If auto-detection reports multiple engines in one repo, stop and ask which project root or engine to use. If the input folder has subfolders, each subfolder is treated as one split level and packaged separately. Default public output contains no JSON; add `--write-manifest` only for debugging.

For a generated common UI kit, `level_01_complete` alone is acceptable when every PNG is already one finished usable component/state/part. Additional levels are for progressive extraction granularity, such as `level_02_parts`, `level_03_atomic`, or screenshot decomposition. Do not create fake levels just to increase folder count.

For animation outputs, organize frame sequences separately from static components:

```text
animations/
  button_play_pulse/
    frames/button_play_pulse_00.png
    frames/button_play_pulse_01.png
    preview.gif
    contact_sheet.png
    engine-import-note.md
```

If the current packager does not understand animation folders, package static PNGs normally and create the animation folder by convention. Do not flatten animation frames into an unrelated icon/button category without a clear clip name.

8. Integrate.
   - If a project root is available, inspect it and use the detected engine before creating engine-specific files. If no project root is available or detection is ambiguous, ask for the target engine. Do not create Godot scaffolding when the user asked for Unity, Cocos, or generic PNG assets.
   - Godot: use generated `.tscn` starter scenes when requested; Godot UI stretch assets should become `NinePatchRect`, `TextureButton`, or `TextureProgressBar`.
   - Godot UI frame animations should use the project's preferred approach: `AnimationPlayer` swapping a `TextureRect.texture`, animated overlay nodes, tweens/shaders for simple glow or scale, or generated frame sequences when baked art is necessary.
   - Unity/Cocos/generic: generate only when requested or when the detected project root clearly matches that engine.
   - For any engine, prefer engine-native tweens/shaders for purely mechanical scale, alpha, or rotation changes. Use baked frame PNGs when the art itself changes, such as sparkles, hand-painted glows, liquid fill, or reward shine.

9. QA before reporting done.
   - Open the root `overview.png` and each level's `overview.png`.
   - Keep the public output focused: `level_xxx/png`, `level_xxx/godot`, and overview images.
   - Treat `possible chroma-key residue` warnings as blockers for final delivery unless the color is intentional UI art.
   - Verify each button has at least a normal state, each progress bar has background/fill when possible, and stretchable components have reasonable slice margins.
   - Inspect cutout edges on dark and light backgrounds. If a frame loses visible pixels, add margin and rebuild the mask; if it includes scene-background pixels, use a tighter segmentation/matting pass.
   - Scan both visible edge pixels and alpha-0 RGB. Final transparent PNGs should have no visible key/cyan edge pixels and no hidden key-colored RGB in fully transparent pixels; clean with `scripts/clean_alpha_fringe.py` before rebuilding overviews.
   - Inspect single-component purity. A packager warning count of zero is not enough: scan alpha connected components and review a candidate contact sheet for assets with multiple significant components, sticky edge fragments, or half-cropped neighbors. Each delivered PNG should contain one usable component with transparent padding.
   - Inspect for over-cutting. If panels, frames, buttons, or HUD elements are missing sides, ornaments, fills, or frame pieces, do not "fix" by keeping the largest blob. Re-slice from the raw generated sheet using real cell boundaries, or regenerate that category.
   - Inspect scaled assets at 100 percent on the target background. If a large source was reduced and looks muddy, sparkly, or clumped, rebuild final-size PNGs with `scripts/resize_assets_high_quality.py` or regenerate closer to target size before packaging.
   - For UI animation, verify the `preview.gif` and contact sheet: every frame has the same size, stable anchor, clean alpha, consistent component design, readable loop/one-shot timing, and no accidental text or neighbor fragments.
   - For loops, check the first/last frame seam. For one-shot clips, check that the first frame can sit idle or has a matching static fallback.
   - If assets are blank, cropped, noisy, text-baked by accident, inconsistent across states, or only approximate because the concept screenshot is ambiguous, regenerate or clean them before integration.

## Resource Navigation

- Read `references/toolchain.md` when choosing between built-in image generation, ComfyUI, chroma-key cleanup, background removal, atlas packers, or MCP/editor integration.
- Read `references/component-contract.md` when naming assets, designing split levels, adjusting nine-slice margins, or mapping PNGs to a specific engine.
- Read `references/style-library.md` when the user asks to upload references, store style materials, keep palette/style consistent across components, extract UI from a screenshot, or generate from a stored game style.
- Read `references/ui-component-catalog.md` when the user asks for a full UI kit, common UI components, a complete component set, or organized output categories.
- Run `scripts/package_ui_assets.py --help` for deterministic packaging options.
- Run `scripts/ingest_style_reference.py --help` for persistent style-library commands.
- Run `scripts/suggest_key_color.py --help` before chroma-key generation when the background key color is not obvious.
- Run `scripts/resize_assets_high_quality.py --help` when generated PNGs are larger than the intended game size, when icons/panels look noisy after forced scaling, or when transparent edges darken after resize.

## Guardrails

- Do not generate creative UI art with Python, SVG, Canvas, CSS, or procedural placeholders. Scripts may only inspect, copy, preview, and package already-created raster assets.
- Do not hand-roll a diffusion backend, background remover, atlas packer, or engine editor bridge when a usable project tool exists.
- Do not treat a full UI mockup screenshot as a finished component pack. Extract or regenerate components separately so buttons, panels, and bars remain reusable.
- Do not use this skill for character, enemy, combat VFX, projectile, impact, or complex sprite-sheet animation; delegate those to `$generate2dsprite`.
- Do not bake every UI feedback effect into frames. If a tween, shader, or engine state change is cleaner, deliver static states plus a short integration note instead of unnecessary frame sequences.
- Do output every meaningful split level by default, from complete object down to atomic layers, but keep each level in its own folder so the result stays usable.
- Do not silently persist user images/text. Store them in the style library only when the user explicitly asks for long-term reuse or skill memory.
- Keep unrelated game implementation changes out of scope unless the user explicitly asks to wire the new UI into gameplay.
