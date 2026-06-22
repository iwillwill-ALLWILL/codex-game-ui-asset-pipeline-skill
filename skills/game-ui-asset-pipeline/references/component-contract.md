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

## Output Scope

Default output should be level-based and Godot-first:

```text
<pack>/
├── overview.png
├── level_01_complete/
│   ├── overview.png
│   ├── png/
│   └── godot/
├── level_02_structured/
│   ├── overview.png
│   ├── png/
│   └── godot/
└── level_03_layout/
    ├── overview.png
    ├── png/
    └── godot/
```

Do not include JSON, debug folders, raw atlases, or intermediate crops in the public output. Use `--write-manifest` only when debugging the packager itself. Generate Unity, Cocos, generic HTML/H5, or extra diagnostic files only when the user asks for them.

## Key-Color Hygiene

Generated UI components should not contain visible chroma-key pixels after alpha cleanup.

- Use selected key colors only as removable backgrounds, not as final UI decoration, unless the user explicitly wants that color.
- Clean with a soft matte and despill before slicing atlases; otherwise key-colored pixels can become baked into the component edge.
- If the packager reports `possible chroma-key residue`, inspect the asset on a dark and light checker background, then rerun chroma cleanup or regenerate with native alpha.
- Keep enough transparent padding after cleanup so nine-slice corners, button glows, and icon silhouettes are not clipped.
