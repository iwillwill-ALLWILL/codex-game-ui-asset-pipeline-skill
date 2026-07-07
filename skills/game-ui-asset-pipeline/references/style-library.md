# Style Library Workflow

Use this reference when the user asks to upload UI references, store a long-term project style, keep palette/style consistent, cut components from a screenshot, generate new UI components from a stored game style, save reference prompts, or evolve a reusable style library.

## What the Skill Supports Now

- Generate UI component art from prompts or reference images with `image_gen`, ComfyUI, or the project's configured image backend.
- Generate style-locked UI from stored user-provided references so a whole pack shares palette, stroke, material, and corner language.
- Generate simple UI frame animations from stored style references or approved static components so glow, shine, particles, fills, and transition frames match the same palette and material language.
- Extract reusable visible pieces from uploaded UI screenshots or generated atlases, then clean alpha and package them. Treat this as useful for prototypes, salvage, and exact visible elements; do not make it the preferred production route when clean source components can be regenerated.
- Package existing PNGs into level folders containing `png/`, `overview.png`, and target-engine files after detecting or confirming the engine. If the engine is unknown, output a generic PNG pack plus import notes.
- Detect common chroma-key residue such as pink/green/blue edge dust during packaging.
- Store user-provided style references in `assets/style-library/<style>/`, extract a dominant palette, save reference prompts, and create a style card for future prompt construction.

## Consent Boundary

Only persist references when the user explicitly asks to store, remember, reuse long-term, add to the skill, or "沉淀" the uploaded material. Do not silently store arbitrary images from a one-off generation request.

## Curate Large Uploads Before Ingesting

When the user uploads many documents, screenshots, prompts, or reference images, do not blindly add every file as equal evidence. First distill the material into a compact style memory that preserves the most useful signal and discards noise.

Use these roles:

| Role | Meaning | Default style weight | How to use |
|---|---|---:|---|
| `anchor` | highest-confidence visual reference for the target game style | `1.0` | palette, material, linework, corners, icons, and prompt lock |
| `accepted-output` | generated result the user approved | `0.9` | stronger future generation anchor than loose inspiration |
| `support` | useful secondary reference | `0.5` | helps confirm recurring traits but should not overrule anchors |
| `prompt` | text prompt/reference wording | `0.3` | informs phrasing, not visual palette by itself |
| `rejected` | failed output or off-style reference with a known reason | `0.0` | contributes only to avoid-list |
| `noise` | irrelevant, inconsistent, low-quality, or contradictory input | `0.0` | exclude from positive style lock; keep only a short rejection note if useful |

Filtering rules:

1. Rank inputs by user intent, visual consistency, production quality, uniqueness, recency, and whether the user explicitly approved them.
2. Keep only the best visual anchors for the style lock. More files are not automatically better if they contradict the desired palette or material language.
3. Summarize long documents into short style facts: palette roles, materials, UI shapes, icons, forbidden motifs, and component requirements. Do not use whole documents as generation context unless a specific passage matters.
4. Convert repeated visual facts into `style-card.md`; convert successful prompts into `reference-prompts.md`; convert failures into the avoid-list.
5. Do not let rejected/noise files affect palette extraction or positive style prompts.
6. When two references conflict, prefer the explicit user requirement, then approved accepted outputs, then anchor images, then support references, then broad docs.

## Project Style Library Model

Treat each style entry as a living project-level memory. It should become more useful as the user uploads more references and accepts or rejects generated outputs.

Stored material can include:

- `sources/`: user-approved reference images, screenshots, docs, notes, and accepted generated component sheets.
- `palette.json`: extracted palette candidates from all stored images.
- `style-card.md`: compact style contract used for future prompting.
- `reference-prompts.json` and `reference-prompts.md`: user-approved prompts and successful final prompts.
- `motion-notes.md` or style-card notes: optional user-approved UI motion language such as glow softness, sweep shape, pulse strength, sparkle density, frame rate habits, and forbidden off-style effects.
- `index.json`: searchable style list with tags, counts, palette preview, and file paths.

Self-organization rules:

1. Add new user-approved material, do not overwrite old material unless the user asks.
2. Keep stable traits that appear across multiple references: palette roles, line weight, material treatment, corner language, icon silhouette, glow/shadow rules, ornament density, and UI motion language when accepted animated examples exist.
3. Convert accepted outputs into stronger generation anchors when the user says the result is good.
4. Convert rejected outputs into avoid-list notes: what drifted, which colors failed, which shapes were off-style, or which components were unusable.
5. Keep prompt examples separate from visual notes. Prompts explain generation intent; style cards explain visual rules.
6. Preserve a stable style precedence: explicit user requirement > style card > accepted outputs > anchor images > support references > prompt bank > broad docs. Rejected/noise entries are negative evidence only.
7. For every future generation, read the style card, palette, prompt bank, avoid-list, and the most relevant anchor/accepted reference images before prompting the image backend. For UI animation, also read accepted static components and any stored motion notes before choosing glow, shine, sweep, or particle behavior.

## Ingest Uploaded References

Use the ingestion script after the user provides images/text and asks to store them:

```bash
python <skill-root>/scripts/ingest_style_reference.py ingest \
  --style <style-slug> \
  --title "<human title>" \
  --input <uploaded-image-or-folder> \
  --notes "<user notes or visual summary>" \
  --prompt "<reference or successful generation prompt>" \
  --role anchor \
  --weight 1.0 \
  --tag <tag>
```

Use `--role accepted-output` when the user approves a generated sheet. Use `--role rejected --avoid "<failure reason>"` for failed results. Use `--role noise --avoid "<why excluded>"` only when recording a lesson is useful; otherwise do not ingest noise at all.

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

Hard boundary: when the user asks to generate, make, produce, batch, create "常用 UI", or build a UI kit from a stored style, the stored screenshots are style evidence only. Do not crop them and present the crops as generated components. If image generation is blocked or unavailable, report the generation blocker or switch to another generation backend; never silently fall back to extraction.

1. Run `list` or `show` to locate the style. Read the style card and inspect stored reference images.
2. Build a compact style lock from positive references only:
   - exact palette hex colors from `palette.json`
   - material and linework notes from `style-card.md`
   - useful prompt phrasing from `reference-prompts.md`
   - component shape rules from the reference image
   - explicit negative prompt from the avoid-list plus text, mockup screens, perspective scenes, and off-palette colors
3. If the user asks for a complete/common UI kit, read `ui-component-catalog.md` and choose `standard+` for "常用 UI" or `complete` for "完整/全套/覆盖所有需求". Cover every major catalog family unless the user narrows the scope.
4. Prefer native alpha. If using a flat key background, run `suggest_key_color.py` on the style sources and use the recommended key in both prompt and cleanup.
5. Generate related components in category batches when a single huge atlas would reduce quality. Keep the same style lock, key color, naming scheme, and output categories across every batch.
6. If using a local diffusion workflow, prefer IP-Adapter for style/palette, ControlNet for silhouettes/layout, and LayerDiffuse/native alpha for transparent output.
7. Clean alpha, split components according to the adaptive split ladder, pad edges, then package with category subfolders for full kits.
8. Compare the generated components against the stored palette and style card before reporting done. Regenerate any component that drifts in color temperature, line weight, material, or corner language.
9. If the user accepts the result, offer to ingest the final component sheet or final prompts back into the same style library.

## Style-Locked UI Frame Animation

Use this when the user asks for simple UI motion such as button pulse, icon glow, reward shine, progress sweep, loading spinner, notification ping, badge pop, or panel open/close.

1. Resolve the style source before generating frames:
   - If the user names a style library, run `list` or `show`, read the style card, inspect anchors/accepted outputs, and reuse the palette and material rules.
   - If the user provides a static UI component, treat that component as the visual anchor and match its line weight, bevels, texture, glow color, and ornament density.
   - If both exist, the style library wins for palette/material rules and the static component wins for exact shape, bounds, and anchor.
2. Build the motion prompt from the same style lock used for static UI. Mention exact palette colors, glow/shadow rules, material, edge treatment, and forbidden off-style effects.
3. Keep the base component design stable across frames. Animate overlays, highlights, fills, alpha, scale, sparkle, or glow; do not redraw the button/panel/icon into a different style.
4. Export transparent same-size frames, a static fallback PNG, and `preview.gif` or contact sheet. Frame names must use the component and clip name, such as `button_play_pulse_00.png`.
5. QA the animation against the style source. Regenerate if particles, sweep highlights, glow colors, line weight, or material shading look like another UI kit.
6. If the user approves the animation, offer to store the accepted frames, preview, prompt, and motion notes back into the same style library as `accepted-output`.

## Secondary Mode: Directly Cut Uploaded UI Components

Use this only when the user explicitly wants the UI elements already present in a screenshot/reference image, such as "抠图", "裁出来", "extract", "cut", "salvage", "reuse the exact visible elements", or "从这张图拆". Do not choose this mode for generated UI kits, common UI packs, or style-library driven generation.

1. Inspect the source image and list target components: panels, buttons, progress bars, icons, map nodes, slots, frames, tabs.
2. If the user requested long-term reuse, ingest the source image into a style entry before extraction.
3. Decide the adaptive split ladder before cutting. Output every useful level by default, from the largest meaningful grain down to the most atomic useful layer. Do not force exactly five levels.
4. Crop or segment components from the source. Use existing tools first:
   - flat key/background: use the installed `imagegen` chroma-key cleanup helper
   - complex background: use `rembg`, BiRefNet, Segment Anything, or a local editor workflow if available
   - atlas/grid: remove divider pixels before slicing and add transparent padding after trim
5. For uncertain edges, keep the full visible border stroke first, then remove residue with matting and visual QA. Never solve a missing border by trimming tighter.
6. Remove baked text unless the user asks for literal text art; provide blank frames/buttons for engine text nodes.
7. Package the resulting PNGs with `package_ui_assets.py`, defaulting to level folders with PNG, overview images, and only the detected or requested target-engine files.
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

For UI frame animation, extend the prompt with:

```text
Motion: <loop/one-shot>, <fps>, <frame count>, <pulse/glow/sweep/spinner/etc>.
Style lock for motion: reuse the same palette, material, edge treatment, glow softness, shine shape, and ornament density from <style title or static component>.
Frame rules: same canvas, same anchor, stable base component, animated overlay/fill/glow only, transparent background, static fallback frame.
Negative: new VFX style, off-palette glow, unrelated particles, changing component design, baked text, cropped glow, unstable anchor.
```
