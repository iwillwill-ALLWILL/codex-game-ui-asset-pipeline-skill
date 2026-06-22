# Style Library Workflow

Use this reference when the user asks to upload UI references, store a long-term style, keep palette/style consistent, cut components from a screenshot, or generate new UI components from a stored game style.

## What the Skill Supports Now

- Generate UI component art from prompts or reference images with `image_gen`, ComfyUI, or the project's configured image backend.
- Extract reusable pieces from uploaded UI screenshots or generated atlases, then clean alpha and package them.
- Package existing PNGs into level folders containing `png/`, `godot/`, and `overview.png` by default. Unity/Cocos outputs are opt-in.
- Detect common chroma-key residue such as pink/green/blue edge dust during packaging.
- Store user-provided style references in `assets/style-library/<style>/`, extract a dominant palette, and create a style card for future prompt construction.

## Consent Boundary

Only persist references when the user explicitly asks to store, remember, reuse long-term, add to the skill, or "沉淀" the uploaded material. Do not silently store arbitrary images from a one-off generation request.

## Ingest Uploaded References

Use the ingestion script after the user provides images/text and asks to store them:

```bash
python <skill-root>/scripts/ingest_style_reference.py ingest \
  --style <style-slug> \
  --title "<human title>" \
  --input <uploaded-image-or-folder> \
  --notes "<user notes or visual summary>" \
  --tag <tag>
```

Then inspect the images and, when useful, edit the generated `style-card.md` manual notes with concise facts:

- palette roles, not just color names
- linework thickness and edge treatment
- material language such as iron, parchment, wood, gem, enamel, glass
- corner and border shape rules
- icon silhouette rules
- glow/shadow rules
- avoid-list for off-style colors, modern UI motifs, text baking, or decoration density

Use `list` and `show` to retrieve stored styles:

```bash
python <skill-root>/scripts/ingest_style_reference.py list
python <skill-root>/scripts/ingest_style_reference.py show --style <style-slug>
```

## Mode A: Directly Cut Uploaded UI Components

Use this when the user wants the UI elements already present in a screenshot/reference image.

1. Inspect the source image and list target components: panels, buttons, progress bars, icons, map nodes, slots, frames, tabs.
2. If the user requested long-term reuse, ingest the source image into a style entry before extraction.
3. Decide the progressive split ladder before cutting. Start with `level_01_complete`; add smaller levels only when the user asks, unless they explicitly request a full deep split.
4. Crop or segment components from the source. Use existing tools first:
   - flat key/background: use the installed `imagegen` chroma-key cleanup helper
   - complex background: use `rembg`, BiRefNet, Segment Anything, or a local editor workflow if available
   - atlas/grid: remove divider pixels before slicing and add transparent padding after trim
5. Remove baked text unless the user asks for literal text art; provide blank frames/buttons for engine text nodes.
6. Package the resulting PNGs with `package_ui_assets.py`, defaulting to level folders with PNG, Godot files, and overview images only.
7. Treat packager warnings, visible residue, and clipped edges as blockers before delivery.

## Mode B: Generate Style-Locked UI From Stored References

Use this when the user wants new components in the same style as materials previously stored in the skill.

1. Run `list` or `show` to locate the style. Read the style card and inspect stored reference images.
2. Build a compact style lock for prompts:
   - exact palette hex colors from `palette.json`
   - material and linework notes from `style-card.md`
   - component shape rules from the reference image
   - explicit negative prompt for text, mockup screens, perspective scenes, and off-palette colors
3. Prefer native alpha. If using a flat key background, run `suggest_key_color.py` on the style sources and use the recommended key in both prompt and cleanup.
4. Generate all related components in one batch/atlas when possible so palette, stroke, lighting, and ornament density match.
5. If using a local diffusion workflow, prefer IP-Adapter for style/palette, ControlNet for silhouettes/layout, and LayerDiffuse/native alpha for transparent output.
6. Clean alpha, split components according to the agreed level ladder, pad edges, then package.
7. Compare the generated components against the stored palette and style card before reporting done. Regenerate any component that drifts in color temperature, line weight, material, or corner language.

## Prompt Pattern

Use this structure for style-locked generation:

```text
Create isolated reusable game UI components, not a full screen mockup.
Style source: <style title>. Match palette exactly: <hex colors>.
Visual rules: <linework/material/corner/icon rules from style-card>.
Components: <component list with states/parts>.
Output: transparent PNG or flat <selected-key-color> removable background, orthographic UI art, no baked text, no watermark.
Negative: modern flat app UI, photorealism, perspective scene, random colors outside palette, fuzzy edges, cropped glow, key-color edge residue.
```
