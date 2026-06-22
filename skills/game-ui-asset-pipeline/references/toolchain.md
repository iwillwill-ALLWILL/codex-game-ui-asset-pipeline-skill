# Toolchain Selection

Use this reference to avoid rebuilding existing tools.

## Raw Image Generation

- Built-in `image_gen`: default when the user asks from a prompt/reference and no local project-specific generator is configured.
- ComfyUI: use when a local workflow already exists, when exact reference-image control is needed, or when the user wants repeatable batch generation. Prefer existing workflows using IP-Adapter, ControlNet, LayerDiffuse, or inpainting nodes instead of designing a full new graph.
- AUTOMATIC1111/Forge/InvokeAI: use only if already installed or clearly preferred by the project.

## Reference Matching

- IP-Adapter: best for matching style, palette, material language, or visual identity from a reference image.
- ControlNet or equivalent structural control: best for preserving silhouettes, button shape, frame layout, line art, and edge structure.
- Vision inspection: use Codex image viewing to describe the reference before writing prompts.

## Transparency

- Prefer native alpha output when the generation backend supports it.
- Use LayerDiffuse when the local Stable Diffusion/ComfyUI workflow supports transparent generation.
- Use `rembg` or an existing transparent visual asset skill for post-generation background removal.
- Use the packager only for validation. It does not remove backgrounds.

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

Escalate to open-source matting/removal tools when the background is not a clean flat key, when the object edge is fuzzy, or when generation produced shadows/reflections on the background:

- `rembg`: fast general background removal for simple cutouts.
- `BiRefNet`: stronger high-quality segmentation for precise foreground masks.
- `PyMatting`: useful when a trimap or explicit alpha matting step is available.
- `backgroundremover`: CLI-oriented batch removal wrapper.
- `RobustVideoMatting`: use for video or frame sequences, not static UI by default.

## Sprites and Animation

Use `$generate2dsprite` for characters, animated effects, projectiles, impacts, summons, or sprite sheets. After it produces transparent frames/sheets, this skill can package icons, HUD elements, or static UI pieces around them.

## Atlases

- Prefer Free Texture Packer when an atlas is required for Godot, Phaser, Pixi, Cocos2d, or generic JSON.
- Prefer Unity Sprite Atlas or Addressables when the target is Unity.
- Prefer engine-native import settings over custom atlas metadata if the game already has an asset pipeline.

## Editor Integration

- Godot: generate `.tscn` starter scenes when no MCP/editor tool is available. Use Godot MCP when installed to create nodes/resources directly.
- Unity: generate import helper scripts when no Unity MCP/editor bridge is available. Use Unity MCP for direct prefab creation when installed.
- Cocos Creator: generate a prefab spec JSON when no Cocos MCP/editor plugin is available. Use Cocos MCP to create nodes and prefabs directly.
