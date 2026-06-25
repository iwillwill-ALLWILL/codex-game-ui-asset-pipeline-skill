# Toolchain Selection

Use this reference to avoid rebuilding existing tools.

## Raw Image Generation

- Built-in `image_gen`: default when the user asks from a prompt/reference and no local project-specific generator is configured.
- ComfyUI: use when a local workflow already exists, when exact reference-image control is needed, or when the user wants repeatable batch generation. Prefer existing workflows using IP-Adapter, ControlNet, LayerDiffuse, or inpainting nodes instead of designing a full new graph.
- AUTOMATIC1111/Forge/InvokeAI: use only if already installed or clearly preferred by the project.
- If a generation backend is blocked or unavailable for a requested UI kit, try another generation backend when available or report the blocker. Do not replace a requested generated kit with screenshot crops, manual placeholder art, or procedural shapes.

## Reference Matching

- IP-Adapter: best for matching style, palette, material language, or visual identity from a reference image.
- ControlNet or equivalent structural control: best for preserving silhouettes, button shape, frame layout, line art, and edge structure.
- Vision inspection: use Codex image viewing to describe the reference before writing prompts.

## Transparency

- Prefer native alpha output when the generation backend supports it.
- Use LayerDiffuse when the local Stable Diffusion/ComfyUI workflow supports transparent generation.
- Use `rembg` or an existing transparent visual asset skill for post-generation background removal.
- Use the packager only for validation. It does not remove backgrounds.

## Concept Screenshot Extraction

Use concept screenshot extraction as a secondary path. It works for visible, well-separated UI pieces, but full UI mockups often do not contain clean source layers. A dark frame may share pixels with a dark tavern wall; a glow may fade into the background; text may cover the border. In these cases, edge errors are a source limitation, not only a bad crop.

Only use this path when the user explicitly asks to extract/cut/salvage the visible screenshot elements. For "generate common UI", "style-library driven UI kit", "常用 UI", or similar requests, screenshots are references for generation and must not become the delivered component source.

Use existing tools in this order:

1. Promptable segmentation such as Segment Anything/SAM 2 for the first object mask.
2. Foreground/background removal such as BiRefNet or `rembg` when the UI object is visually separable from the scene.
3. Trimap alpha matting such as PyMatting for antialiased strokes, bevels, soft shadows, and glows.
4. OpenCV morphology only as postprocessing: close small holes, dilate 1-3 px to preserve strokes, feather the edge, then trim transparent padding.
5. Manual mask correction or regeneration from the style library when the source pixels are occluded or ambiguous.

Do not use the packager as a segmentation tool. It should receive already cleaned PNGs and then validate/copy/preview them.

## Key Color Selection

Do not default blindly to `#ff00ff`. A key color is only safe when it is absent from the UI art, reference palette, glows, shadows, and antialiasing.

Use this order:

1. Native alpha or LayerDiffuse.
2. A key color selected by `scripts/suggest_key_color.py`.
3. A custom key color chosen after visually inspecting the reference.
4. Background removal/matting tools when no flat key is safe.

```bash
python <skill-root>/scripts/suggest_key_color.py --input <reference-image-or-folder>
```

When the script warns that all candidates are close to visible colors, do not force the best candidate. Regenerate with native alpha, choose a custom color far outside the palette, or segment with `rembg`, BiRefNet, PyMatting, or Segment Anything.

## Chroma-Key Edge Cleanup

Use this when generated UI assets have a flat removable background such as `#ff00ff`, but visible pink/green/blue dust remains around the component edge.

- Clean the atlas before grid slicing when the source is an atlas; clean individual PNGs when components were generated separately.
- Reuse the installed `imagegen` script first:

```bash
python <codex-home>/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input <raw-atlas-or-png> \
  --out <clean-alpha.png> \
  --key-color "<selected-key-color>" \
  --soft-matte \
  --transparent-threshold 24 \
  --opaque-threshold 170 \
  --edge-contract 1 \
  --edge-feather 0.25 \
  --despill \
  --force
```

- Use `--auto-key corners` or `--auto-key border` when the background key was sampled from the generated image instead of specified exactly.
- Use `edge-contract 1` for small pink speckles; try `2` only when a visible key-color rim remains and the art can tolerate losing a pixel of edge detail.
- Use `edge-feather 0.25-0.75` after contraction when the edge looks jagged.
- Run the packager after cleanup and treat `possible chroma-key residue` warnings as a QA failure unless that saturated key color is deliberately part of the UI.
- Do not solve key-color dust by only trimming the bounding box. Trimming removes empty canvas but does not remove contaminated edge pixels.
- Do not trust visible-pixel checks alone. Fully transparent pixels can still contain cyan/key-colored RGB; some viewers and game texture filtering can leak that hidden color around the asset edge.

Run the skill cleanup helper after the first matte pass when any cyan/teal/pink/green residue remains, when generated components still show patterned key backgrounds in the corners, or before final packaging of a large component kit:

```bash
python <skill-root>/scripts/clean_alpha_fringe.py \
  --input <folder-or-png> \
  --backup <backup-folder> \
  --report-json <qa-report.json>
```

The helper removes three failure classes:

- edge-connected key/background patches, including dark teal/cyan patterned corners from generated sheets;
- visible key-colored pixels exposed along the alpha boundary after repeated cleanup passes;
- key-colored RGB stored in alpha-0 pixels. Final alpha-0 pixels should not keep `#00ffff`, `#ff00ff`, `#00ff00`, or similar key colors.

After running it, rebuild contact sheets/overviews from the cleaned PNGs and inspect on both light and dark solid backgrounds. If a component intentionally has blue/green interior art, the cleanup should preserve it when it is enclosed by the component frame; only edge-connected background regions should be removed. The default pass is conservative for visible edge art: if a light/dark review still shows a visible cyan edge after the default pass, rerun only the affected files with `--clean-visible-edge-key`; use `--aggressive-edge-cold-cyan` only for confirmed cyan fringe because it can erode legitimate cold-colored edge art.

Escalate to open-source matting/removal tools when the background is not a clean flat key, when the object edge is fuzzy, or when generation produced shadows/reflections on the background:

- `rembg`: fast general background removal for simple cutouts.
- `BiRefNet`: stronger high-quality segmentation for precise foreground masks.
- `PyMatting`: useful when a trimap or explicit alpha matting step is available.
- `backgroundremover`: CLI-oriented batch removal wrapper.
- `RobustVideoMatting`: use for video or frame sequences, not static UI by default.

## High-Quality Downscaling

Use this when a generated UI PNG is much larger than the size used in-game, or when a large component becomes noisy, muddy, or clumped after the engine/editor/browser scales it down.

Preferred order:

1. Generate near the final intended size whenever the backend can do it cleanly.
2. If extra resolution is useful, generate a controlled 2x/3x source, not an arbitrary oversized sheet.
3. Crop or slice to one finished component first, add transparent padding, then resize the component. Do not downscale a whole atlas with large gutters and then cut it.
4. For transparent PNGs, resize with premultiplied alpha and clear RGB in fully transparent pixels after resizing.
5. For reductions larger than about 2x, use multi-step Lanczos resizing. Add a tiny prefilter only when texture noise sparkles or clumps, then use mild unsharp masking to recover UI edge clarity.
6. Inspect the resized result at 100 percent on both dark and light backgrounds before packaging.

Use the bundled helper for final-size exports:

```bash
python <skill-root>/scripts/resize_assets_high_quality.py \
  --input <clean-alpha-png-folder> \
  --output <final-size-png-folder> \
  --max-side 512 \
  --prefilter 0.18
```

For fixed sizes:

```bash
python <skill-root>/scripts/resize_assets_high_quality.py \
  --input icon-coin-source.png \
  --output final-icons \
  --target-size 128x128 \
  --prefilter 0.12
```

Avoid these failure modes:

- one-step runtime shrink from 1024/2048 px source to 32/64 px UI;
- bilinear shrink for painterly UI;
- resizing straight-alpha PNGs without premultiplication, which creates dark or colored rims;
- shrinking text-baked UI labels and then trying to sharpen unreadable text;
- uniformly shrinking a nine-slice panel to solve layout sizing. Keep a clean cap/corner texture and let the engine stretch the center.

## Sprites and Animation

Use `$generate2dsprite` for characters, animated effects, projectiles, impacts, summons, or sprite sheets. After it produces transparent frames/sheets, this skill can package icons, HUD elements, or static UI pieces around them.

## Atlases

- Prefer Free Texture Packer when an atlas is required for Godot, Phaser, Pixi, Cocos2d, or generic JSON.
- Prefer Unity Sprite Atlas or Addressables when the target is Unity.
- Prefer engine-native import settings over custom atlas metadata if the game already has an asset pipeline.
- When splitting generated sheets, fixed grids are only safe when every row and column is truly uniform. If rows have different column counts, gutters vary, or cells are mixed-size, detect real separator lines or foreground component bounds from the raw sheet before alpha cleanup.
- If QA finds sticky neighbors, half-components, or missing frame pieces, return to the raw generated sheet and re-slice. Do not repeatedly clean or largest-component-filter already damaged crops.
- Keep generated sheet contact sheets during QA, but keep them out of the public packaged output so `package_ui_assets.py` does not treat contact previews as a root asset level.

## Local and Remote Skill Sync

When this skill is updated from a real project failure, sync the lesson to both:

- the installed local skill under `$CODEX_HOME/skills/game-ui-asset-pipeline`;
- the source/remote skill repository when present, such as `open-source/codex-game-ui-asset-pipeline-skill/skills/game-ui-asset-pipeline`.

Do not push remote changes unless the user explicitly asks. Validate both copies after editing so future local runs and future installs use the same rules.

## Editor Integration

- Godot: generate `.tscn` starter scenes when no MCP/editor tool is available. Use Godot MCP when installed to create nodes/resources directly.
- Unity: generate import helper scripts when no Unity MCP/editor bridge is available. Use Unity MCP for direct prefab creation when installed.
- Cocos Creator: generate a prefab spec JSON when no Cocos MCP/editor plugin is available. Use Cocos MCP to create nodes and prefabs directly.
