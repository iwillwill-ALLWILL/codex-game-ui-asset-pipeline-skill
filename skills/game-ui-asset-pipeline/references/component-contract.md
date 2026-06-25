# Component Contract

This contract keeps generated UI assets reusable across engines.

## Naming

Use PNG filenames that identify component type, name, and state/part:

- `panel_inventory.png`
- `button_play_normal.png`
- `button_play_hover.png`
- `button_play_pressed.png`
- `button_play_disabled.png`
- `progress_health_bg.png`
- `progress_health_fill.png`
- `icon_coin.png`
- `slot_inventory_empty.png`

The packager auto-detects common synonyms, but explicit names reduce correction work.

## Component Types

- `panel`: stretchable background, modal, popup, HUD frame, card, inventory frame.
- `button`: clickable UI image with `normal`, `hover`, `pressed`, and optional `disabled` states.
- `progress_bar`: two-part control with `background`/`track` and `fill`.
- `icon`: non-stretchable image, item icon, HUD icon, badge, currency mark.
- `image`: fallback type when no stronger type is detected.

## Adaptive Progressive Split Levels

When the user says "cut UI components", split from large to small. Output every meaningful level by default, but keep each level in a separate folder.

Default behavior:

1. Analyze the concrete UI first, then build a split ladder that matches the image. Do not force exactly five levels.
2. Produce all useful progressive levels in one pass unless the user narrows the scope.
3. Skip levels that are empty, mechanical, or indistinguishable from a neighboring level.
4. Keep complete objects, useful composites, frame variants, state/part variants, and atomic outputs separate.
5. Make the final atomic level as complete as possible for recomposition.
6. Use the root `overview.png` and each level `overview.png` to help the user compare granularity.

Use semantic folder names:

```text
level_01_<largest-useful-grain>
level_02_<next-useful-grain>
level_03_<next-useful-grain>
...
level_nn_<atomic-or-final-grain>
```

Examples:

| Source object | Good ladder | Notes |
|---|---|---|
| Single icon | `level_01_icon_complete`, `level_02_icon_shape_parts` | Two levels may be enough. |
| Simple button | `level_01_button_complete`, `level_02_button_frame_and_fill`, `level_03_button_atomic` | No fake layout level if there are no internal lines. |
| Complex card | `level_01_card_complete`, `level_02_card_frame_dividers_decor`, `level_03_card_frame_dividers`, `level_04_card_outer_frame`, `level_05_card_atomic_parts` | More levels are justified because each level is useful. |
| Full HUD screenshot | `level_01_major_panels`, `level_02_controls_and_rows`, `level_03_frames_and_tracks`, `level_04_icons_and_atoms` | Four levels may be better than five. |

Card example from large to small:

```text
level_01_card_complete/card_complete.png
level_02_card_frame_dividers_decor/card_outer_inner_decor.png
level_03_card_frame_dividers/card_outer_inner_lines.png
level_04_card_outer_frame/card_outer_frame.png
level_05_card_atomic_parts/outer_frame.png
level_05_card_atomic_parts/inner_lines.png
level_05_card_atomic_parts/decorations.png
level_05_card_atomic_parts/background.png
level_05_card_atomic_parts/icon.png
level_05_card_atomic_parts/portrait.png
```

The first four levels are composite variants of the same card at different granularity. The last level is the fully separated layer set.

For any ambiguous screenshot, provide an extraction ladder before slicing:

```text
Extraction ladder:
- level_01_card_complete: complete card unchanged
- level_02_card_frame_dividers_decor: outer frame + inner dividers + internal decorations
- level_03_card_frame_dividers: outer frame + inner dividers
- level_04_card_outer_frame: outer frame only
- level_05_card_atomic_parts: frame, dividers, decorations, background, icon, portrait as separate PNGs

Produce all listed levels by default. If the image only supports three meaningful levels, output three. If the image supports seven meaningful levels, output seven. If the user asks for only one layer, output only that folder.
```

If the user explicitly asks to "拆彻底", verify that the final atomic folder contains every separable useful part, including frame, divider lines, ornaments, background, icons, portraits, badges, tracks, fills, and glows when present.

## Screenshot Extraction Edge Rules

Concept screenshots are not source-layer files. UI strokes may blend into dark scene backgrounds, text may cover borders, and shadows may merge with scenery. Treat this as an edge ambiguity problem, not only as background cleanup.

Use this order:

1. Prefer a style-library or reference-guided generation workflow for production-ready components.
2. If extracting from a screenshot, make a semantic crop with extra margin before segmentation.
3. Build a foreground mask with existing segmentation/matting tools when possible, then apply morphological close/dilate by 1-3 px to preserve border strokes.
4. Use trimap/alpha matting for semi-transparent glows and antialiasing instead of hard thresholding.
5. After matting, remove scene-background residue, trim only transparent padding, then add 4-12 px transparent padding back.
6. Inspect every asset on dark and light backgrounds. A missing frame pixel is a failure; a visible scene-background sliver is also a failure.
7. If the border cannot be separated because source pixels are genuinely ambiguous or occluded, regenerate that component from the style library instead of over-promising extraction quality.

## Nine-Slice Defaults

The packager suggests conservative margins:

- Panels/buttons: roughly 18-22 percent of the shortest side, clamped to avoid consuming the center.
- Progress bars: horizontal caps based mainly on height; vertical margins stay small.
- Icons/images: no nine-slice unless manually requested.

Override margins in-engine when the generated art has unusually thick corners, shadows, or bevels.

## Resolution and Scaling Contract

Final delivered PNGs should match the intended game usage size closely enough that the engine does not have to hide oversized source detail by brute-force scaling.

- Decide output sizes before packaging: icons commonly need fixed exports such as 32, 64, 128, or 256 px; panels/buttons should use target cap/corner dimensions plus nine-slice for layout stretching.
- Keep source masters separately only while working. Public output should contain final game-ready sizes, not oversized raw generations unless the user asks for masters.
- Use names or folders that make scale obvious when multiple sizes are delivered, such as `icon-coin__64.png`, `icon-coin__128.png`, `panel-inventory__512x256.png`, or `png/icons/128/`.
- Downscale each isolated component after alpha cleanup and before packaging. Do not downscale a whole sheet and then slice, because gutters, neighboring cells, and key-color antialiasing will contaminate the final component.
- For transparent assets, use premultiplied-alpha resizing and zero alpha-0 RGB after resizing to avoid colored rims in thumbnails and texture filtering.
- For nine-slice UI, preserve corner and border detail at the target cap size; use engine stretch regions for larger layout sizes instead of shipping one enormous panel and shrinking it everywhere.
- If a resized asset looks muddy or noisy at 100 percent, regenerate closer to target size or rerun `scripts/resize_assets_high_quality.py` with light prefiltering. Do not solve muddy downscales by sharpening aggressively enough to create halos.

## Output Scope

Default output should be level-based and Godot-first. For small packs, a flat `png/` folder is acceptable. For full/common UI kits, use category subfolders under `png/`.

```text
<pack>/
├── overview.png
├── level_01_complete_ui_kit/
│   ├── overview.png
│   ├── png/
│   │   ├── panels/
│   │   ├── buttons/
│   │   ├── bars/
│   │   ├── cards/
│   │   ├── slots/
│   │   ├── hud/
│   │   ├── icons/
│   │   ├── frames/
│   │   └── images/
│   └── godot/
├── level_02_atomic_parts/
│   ├── overview.png
│   ├── png/
│   └── godot/
```

Do not include JSON, debug folders, raw atlases, or intermediate crops in the public output. Use `--write-manifest` only when debugging the packager itself. Generate Unity, Cocos, generic HTML/H5, or extra diagnostic files only when the user asks for them.

Use `package_ui_assets.py --category-subdirs` when the pack contains many different component types. Keep names descriptive even when category folders exist, such as `button-primary__normal.png`, `bar-health__fill.png`, and `icon-coin.png`.

For generated full kits, a single `level_01_complete` folder is normal when it contains final complete components. More levels are only useful when they represent real granularity differences, for example complete card, frame-only, frame-and-dividers, and atomic parts. Do not create empty or duplicate levels to make the package look larger.

## Single-Component Purity

For final game-ready component packs, every PNG must contain exactly one semantic UI component or one state/part of a component. Do not ship sheet cells that still contain neighboring strips, two half-cropped components, sticky fragments, or multiple unrelated UI pieces.

After alpha cleanup and cropping:

1. Run an alpha connected-component scan on each PNG.
2. Flag assets with more than one significant disconnected subject, edge-touching fragments after padding, long thin leftover strips, or small partial neighbors.
3. Build a candidate contact sheet and inspect it visually before packaging.
4. For flagged assets, keep the main component only when the extra pieces are obvious leftovers and the remaining component is visually complete. Do not use largest-component filtering on frames, panels, buttons, or HUD widgets when it would remove valid disconnected ornaments, sides, inner lines, rivets, or glows.
5. Re-crop to the kept component and add transparent padding before final packaging.

Disconnected pixels are acceptable only when they are clearly part of one component, such as small rivets attached visually to a frame, a controlled glow, or one icon silhouette. They are not acceptable when they look like another button, frame, header strip, side rail, or partial neighbor.

## Generated Sheet Reslicing

When UI components come from generated sheets or atlases, start from the raw generated sheet for final slicing. Do not keep iterating on already damaged crops.

Use this order:

1. Inspect the raw sheet/contact sheet first.
2. Detect real separator lines and per-row/per-column cell bounds when the sheet has visible gutters.
3. If the sheet has uneven rows, variable cell sizes, or mixed layouts, slice by true cell boundaries or foreground component bounds, not by a fixed grid.
4. Remove the key/background color and separator-line antialiasing after each true cell crop.
5. Re-check each final PNG on a contact sheet for two failure classes: extra half-neighbor pieces and missing half-components.

If a generated cell itself contains multiple intentional small assets, split those assets separately only when each split remains complete. If a generated cell is structurally bad, regenerate that category instead of cutting away damage.

## Key-Color Hygiene

Generated UI components should not contain visible chroma-key pixels after alpha cleanup.

- Use selected key colors only as removable backgrounds, not as final UI decoration, unless the user explicitly wants that color.
- Clean with a soft matte and despill before slicing atlases; otherwise key-colored pixels can become baked into the component edge.
- If the packager reports `possible chroma-key residue`, inspect the asset on a dark and light checker background, then rerun chroma cleanup or regenerate with native alpha.
- Treat `#00ffff`/cyan and dark teal generated backgrounds as key-color residue too. Cyan may appear as saturated pixels, pale antialiasing, or dark patterned corner backgrounds.
- Validate hidden RGB, not just visible alpha. Alpha-0 pixels must not retain key-colored RGB because game importers, thumbnails, and texture filtering can reveal it as a colored rim.
- Use `scripts/clean_alpha_fringe.py` after matte cleanup when a batch still has visible cyan/pink/green edge pixels, edge-connected teal background patches, or alpha-0 key RGB.
- Keep enough transparent padding after cleanup so nine-slice corners, button glows, and icon silhouettes are not clipped.
