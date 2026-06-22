# Style Library Workflow

Use this reference when the user asks to upload UI references, store a long-term project style, keep palette/style consistent, cut components from a screenshot, generate new UI components from a stored game style, save reference prompts, or evolve a reusable style library.

## What the Skill Supports Now

- Generate UI component art from prompts or reference images with `image_gen`, ComfyUI, or the project's configured image backend.
- Generate style-locked UI from stored user-provided references so a whole pack shares palette, stroke, material, and corner language.
- Extract reusable visible pieces from uploaded UI screenshots or generated atlases, then clean alpha and package them. Treat this as useful for prototypes, salvage, and exact visible elements; do not make it the preferred production route when clean source components can be regenerated.
- Package existing PNGs into level folders containing `png/`, `godot/`, and `overview.png` by default. Unity/Cocos outputs are opt-in.
- Detect common chroma-key residue such as pink/green/blue edge dust during packaging.
- Store user-provided style references in `assets/style-library/<style>/`, extract a dominant palette, save reference prompts, and create a style card for future prompt construction.

## Consent Boundary

Only persist references when the user explicitly asks to store, remember, reuse long-term, add to the skill, or "沉淀" the uploaded material. Do not silently store arbitrary images from a one-off generation request.

## Project Style Library Model

Treat each style entry as a living project-level memory. It should become more useful as the user uploads more references and accepts or rejects generated outputs.

Stored material can include:

- `sources/`: user-approved reference images, screenshots, docs, notes, and accepted generated component sheets.
- `palette.json`: extracted palette candidates from all stored images.
- `style-card.md`: compact style contract used for future prompting.
- `reference-prompts.json` and `reference-prompts.md`: user-approved prompts and successful final prompts.
- `index.json`: searchable style list with tags, counts, palette preview, and file paths.

Self-organization rules:

1. Add new user-approved material, do not overwrite old material unless the user asks.
2. Keep stable traits that appear across multiple references: palette roles, line weight, material treatment, corner language, icon silhouette, glow/shadow rules, and ornament density.
3. Convert accepted outputs into stronger generation anchors when the user says the result is good.
4. Convert rejected outputs into avoid-list notes: what drifted, which colors failed, which shapes were off-style, or which components were unusable.
5. Keep prompt examples separate from visual notes. Prompts explain generation intent; style cards explain visual rules.
6. For every future generation, read the style card, palette, prompt bank, and at least the most relevant reference images before prompting the image backend.

## Ingest Uploaded References

Use the ingestion script after the user provides images/text and asks to store them:

```bash
python <skill-root>/scripts/ingest_style_reference.py ingest \
  --style <style-slug> \
  --title "<human title>" \
  --input <uploaded-image-or-folder> \
  --notes "<user notes or visual summary>" \
  --prompt "<reference or successful generation prompt>" \
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
- accepted prompt patterns and rejected-output lessons

Use `list` and `show` to retrieve stored styles:

```bash
python <skill-root>/scripts/ingest_style_reference.py list
python <skill-root>/scripts/ingest_style_reference.py show --style <style-slug>
```

## Preferred Mode: Generate Style-Locked UI From Stored References

Use this when the user wants production-ready components in the same style as materials previously stored in the skill. Prefer this over concept screenshot extraction for buttons, panels, bars, cards, slots, and repeatable HUD parts.

1. Run `list` or `show` to locate the style. Read the style card and inspect stored reference images.
2. Build a compact style lock for prompts:
   - exact palette hex colors from `palette.json`
   - material and linework notes from `style-card.md`
   - useful prompt phrasing from `reference-prompts.md`
   - component shape rules from the reference image
   - explicit negative prompt for text, mockup screens, perspective scenes, and off-palette colors
3. If the user asks for a complete/common UI kit, read `ui-component-catalog.md` and choose the complete or project-specific checklist.
4. Prefer native alpha. If using a flat key background, run `suggest_key_color.py` on the style sources and use the recommended key in both prompt and cleanup.
5. Generate related components in category batches when a single huge atlas would reduce quality. Keep the same style lock, key color, naming scheme, and output categories across every batch.
6. If using a local diffusion workflow, prefer IP-Adapter for style/palette, ControlNet for silhouettes/layout, and LayerDiffuse/native alpha for transparent output.
7. Clean alpha, split components according to the adaptive split ladder, pad edges, then package with category subfolders for full kits.
8. Compare the generated components against the stored palette and style card before reporting done. Regenerate any component that drifts in color temperature, line weight, material, or corner language.
9. If the user accepts the result, offer to ingest the final component sheet or final prompts back into the same style library.

## Secondary Mode: Directly Cut Uploaded UI Components

Use this when the user wants the UI elements already present in a screenshot/reference image.

1. Inspect the source image and list target components: panels, buttons, progress bars, icons, map nodes, slots, frames, tabs.
2. If the user requested long-term reuse, ingest the source image into a style entry before extraction.
3. Decide the adaptive split ladder before cutting. Output every useful level by default, from the largest meaningful grain down to the most atomic useful layer. Do not force exactly five levels.
4. Crop or segment components from the source. Use existing tools first:
   - flat key/background: use the installed `imagegen` chroma-key cleanup helper
   - complex background: use `rembg`, BiRefNet, Segment Anything, or a local editor workflow if available
   - atlas/grid: remove divider pixels before slicing and add transparent padding after trim
5. For uncertain edges, keep the full visible border stroke first, then remove residue with matting and visual QA. Never solve a missing border by trimming tighter.
6. Remove baked text unless the user asks for literal text art; provide blank frames/buttons for engine text nodes.
7. Package the resulting PNGs with `package_ui_assets.py`, defaulting to level folders with PNG, Godot files, and overview images only.
8. Treat packager warnings, visible residue, clipped edges, and accidental scene-background slivers as blockers before delivery. If the screenshot cannot provide a clean edge, regenerate the component from the style library.

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
