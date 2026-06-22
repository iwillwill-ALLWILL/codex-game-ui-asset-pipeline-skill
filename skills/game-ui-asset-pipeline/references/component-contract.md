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

## Nine-Slice Defaults

The packager suggests conservative margins:

- Panels/buttons: roughly 18-22 percent of the shortest side, clamped to avoid consuming the center.
- Progress bars: horizontal caps based mainly on height; vertical margins stay small.
- Icons/images: no nine-slice unless manually requested.

Override margins in-engine when the generated art has unusually thick corners, shadows, or bevels.

## Manifest Expectations

`ui-asset-manifest.json` contains:

- `assets`: copied PNGs with dimensions, alpha/bounds inspection, and suggested slice margins.
- `components`: grouped panel/button/progress/icon definitions.
- `warnings`: packaging issues Codex should inspect before declaring success.

Generated files should be treated as scaffolding. If a local project already has a UI theme, atlas, prefab, or import convention, map this manifest into that convention instead of forcing a new structure.

## Key-Color Hygiene

Generated UI components should not contain visible chroma-key pixels after alpha cleanup.

- Use bright key colors such as `#ff00ff` only as removable backgrounds, not as final UI decoration, unless the user explicitly wants that color.
- Clean with a soft matte and despill before slicing atlases; otherwise key-colored pixels can become baked into the component edge.
- If the manifest reports `possible chroma-key residue`, inspect the asset on a dark and light checker background, then rerun chroma cleanup or regenerate with native alpha.
- Keep enough transparent padding after cleanup so nine-slice corners, button glows, and icon silhouettes are not clipped.
