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

## Progressive Split Levels

When the user says "cut UI components", split from large to small. Do not start by extracting every tiny layer.

Default behavior:

1. Produce the largest useful layer first.
2. Show the level overview to the user.
3. If the user asks for smaller granularity, produce the next level.
4. Continue downward until the object is decomposed as thoroughly as the user needs.

Use this level naming:

| Folder | Meaning | Typical contents |
|---|---|---|
| `level_01_complete` | Full reusable object, unchanged except cleanup/padding. | complete card, full panel, full toolbar |
| `level_02_structured` | Main frame plus internal divisions and visible decorations, content removed if possible. | card frame + separators + ornaments |
| `level_03_layout` | Frame plus internal guide/divider lines, decorations removed. | outer frame + inner split lines |
| `level_04_outer_frame` | Outer silhouette/frame only. | card outline, panel border, button frame |
| `level_05_atomic` | Separate atoms for maximum recomposition. | outer frame, inner lines, corners, bolts, background, icon, portrait |

Card example from large to small:

```text
level_01_complete/card_complete.png
level_02_structured/card_outer_inner_decor.png
level_03_layout/card_outer_inner_lines.png
level_04_outer_frame/card_outer_frame.png
level_05_atomic/outer_frame.png
level_05_atomic/inner_lines.png
level_05_atomic/decorations.png
level_05_atomic/background.png
level_05_atomic/icon.png
level_05_atomic/portrait.png
```

The first four levels are composite variants of the same card at different granularity. The last level is the fully separated layer set.

For any ambiguous screenshot, provide an extraction ladder before slicing:

```text
Extraction ladder:
- level_01_complete: complete card unchanged
- level_02_structured: outer frame + inner dividers + internal decorations
- level_03_layout: outer frame + inner dividers
- level_04_outer_frame: outer frame only
- level_05_atomic: frame, dividers, decorations, background, icon, portrait as separate PNGs

Start with level_01_complete. Wait for user feedback before producing smaller levels.
```

If the user explicitly asks to "拆彻底", produce every level down to `level_05_atomic`.

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
