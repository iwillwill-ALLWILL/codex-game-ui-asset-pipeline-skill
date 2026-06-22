# Game UI Asset Pipeline Skill

把一张参考图、一段提示词，或者一组已经生成好的 PNG，整理成可以直接放进游戏项目里的 UI 组件包。

这个仓库提供一个 Codex Skill：`game-ui-asset-pipeline`。它不自己造图像生成、抠图、图集、编辑器接入这些轮子，而是协调现有工具完成重活，然后用内置脚本做稳定的命名、检查、预览、manifest 和引擎脚手架。

## 你能用它做什么

- 从提示词或参考图生成游戏 UI 组件。
- 从用户上传的 UI 截图里扣出面板、按钮、进度条、图标、slot、HUD 框。
- 把用户主动上传的风格参考图/文字沉淀成长期风格库。
- 按风格库里的色卡、线条、材质、边框规则生成同一画风的新 UI。
- 清理粉色、绿色、蓝色 chroma-key 边缘颗粒。
- 把 PNG 组件打包成 `preview.png`、`ui-asset-manifest.json`、Godot `.tscn`、Unity import helper、Cocos prefab spec。

## 0. 安装

### 方法 A：用 Codex 的 skill-installer

在 Codex 里让 AI 执行：

```text
请用 $skill-installer 从 GitHub 安装：
repo: iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill
path: skills/game-ui-asset-pipeline
```

安装后重启 Codex，让新 skill 生效。

### 方法 B：手动安装

克隆仓库：

```bash
git clone https://github.com/iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill.git
cd codex-game-ui-asset-pipeline-skill
```

Windows：

```powershell
.\install.ps1
```

macOS / Linux：

```bash
chmod +x install.sh
./install.sh
```

如果本机已经有同名 skill，确认要替换后再运行：

```powershell
.\install.ps1 -Force
```

```bash
./install.sh --force
```

## 1. 先跑通最小流程

准备一个文件夹，里面放 3-5 张透明 PNG，例如：

```text
my-ui/
├── panel_inventory.png
├── button_play_normal.png
├── button_play_pressed.png
├── progress_health_bg.png
└── progress_health_fill.png
```

让 Codex 执行：

```text
任务：使用 $game-ui-asset-pipeline 把 my-ui 文件夹打包成游戏 UI 组件包。
输入：my-ui 里面是一组 PNG。
输出：生成 preview.png、ui-asset-manifest.json，并额外输出 Godot、Unity、Cocos 的导入脚手架。
要求：不要修改原始 PNG。先检查 manifest warnings，有问题先修复再告诉我完成。
验收：我能看到 preview.png，manifest 里 warnings 为 0 或者你解释清楚每个 warning。
```

Codex 会调用：

```bash
python <skill-root>/scripts/package_ui_assets.py \
  --input my-ui \
  --output output/my-ui-pack \
  --pack-name my-ui \
  --engines godot,unity,cocos
```

你得到的输出一般长这样：

```text
output/my-ui-pack/
├── assets/ui/
├── cocos/ui_pack_prefab_spec.json
├── godot/*.tscn
├── unity/*Importer.cs
├── preview.png
└── ui-asset-manifest.json
```

## 2. 从参考图生成 UI 组件

上传一张游戏 UI 参考图，然后对 Codex 说：

```text
任务：使用 $game-ui-asset-pipeline，根据这张参考图生成一套可复用的游戏 UI 组件。
组件：主面板、信息卡片、普通按钮、按下按钮、禁用按钮、血条底、血条填充、金币图标、设置图标、背包 slot。
要求：
1. 不要生成整张 UI mockup，要生成独立组件。
2. 不要把中文按钮文字烘焙进图片，文字以后交给游戏引擎。
3. 背景用透明 PNG；如果当前图像工具不支持透明，就用 #ff00ff 纯色背景，之后清理掉。
4. 所有按钮和面板要能做九宫格拉伸。
输出：组件 PNG、preview.png、manifest、Godot/Unity/Cocos 脚手架。
验收：没有粉色边缘颗粒，没有明显裁切，组件风格一致。
```

学生要做的事很少：上传图、说清楚组件列表、看预览图、把不满意的地方截图发回给 AI 修。

## 3. 从用户上传的截图里直接扣组件

如果你想要的 UI 已经在截图里，不一定要重新生成。可以让 Codex 直接扣：

```text
任务：使用 $game-ui-asset-pipeline，从我上传的 UI 截图里扣出可复用组件。
目标组件：
- 左上角任务面板
- 顶部进度条
- 底部角色信息面板
- 技能按钮框
- 地图节点图标
- 右侧菜单按钮
要求：
1. 尽量使用截图里的真实 UI 元素。
2. 去掉组件里的文字，只保留背景框和图标。
3. 裁切后加透明 padding，避免边缘被切掉。
4. 如果有粉色/绿色/蓝色颗粒，先清理再打包。
验收：每个组件都是独立 PNG，manifest warnings 为空。
```

适合用在：你有一张好看的 UI 截图，只想快速拆成游戏里能用的小组件。

## 4. 把用户资料沉淀成风格库

当你希望以后一直复用某个游戏画风时，先让用户明确上传资料，然后沉淀进 skill：

```text
任务：使用 $game-ui-asset-pipeline，把我上传的参考图和说明沉淀成一个长期风格库。
风格名：dark-dungeon-ui
资料：我上传的 UI 截图、角色界面截图、按钮参考图、风格说明文档。
要求：
1. 只保存我这次明确要求沉淀的资料。
2. 自动提取色卡。
3. 生成 style-card.md，写清楚线条、材质、边框、图标、发光、避免事项。
4. 不要把这些用户资料提交到公开仓库。
验收：告诉我 style-card.md 和 palette.json 的位置。
```

底层脚本是：

```bash
python <skill-root>/scripts/ingest_style_reference.py ingest \
  --style dark-dungeon-ui \
  --title "Dark Dungeon UI" \
  --input <uploaded-reference-folder> \
  --notes "dark iron frame, warm gold accents, thick ink outline" \
  --tag dark-fantasy
```

它会生成：

```text
assets/style-library/dark-dungeon-ui/
├── sources/
├── palette.json
└── style-card.md
```

注意：`assets/style-library/` 默认被 `.gitignore` 忽略。用户上传的私有参考图默认不进入 GitHub。

## 5. 用风格库生成同画风的新 UI

有了风格库后，下一次可以这样说：

```text
任务：使用 $game-ui-asset-pipeline，根据 style-library 里的 dark-dungeon-ui 画风，生成一套新的战斗 HUD UI。
组件：
- 回合提示面板
- 角色头像框
- 血条底和血条填充
- 4 个技能按钮状态：normal、hover、pressed、disabled
- 6 个地图节点图标：普通、宝箱、事件、精英、Boss、已完成
要求：
1. 先读取 dark-dungeon-ui 的 style-card.md 和 palette.json。
2. 所有组件必须沿用同一色卡、线条粗细、金属材质和边框语言。
3. 生成时不要做完整游戏截图，只做独立组件。
4. 不要烘焙文字。
5. 生成后清理透明边缘并打包。
验收：preview.png 里所有组件看起来像同一个游戏项目出来的。
```

这个流程解决的是：每次生成 UI 都好看，但颜色、线条、材质不稳定的问题。

## 6. 清理粉色边缘颗粒

很多图像工具会用 `#ff00ff` 当临时背景。直接裁切会留下粉色边缘点，这不是普通裁切问题，而是 chroma-key spill。

让 Codex 这样处理：

```text
任务：使用 $game-ui-asset-pipeline 清理这些 UI PNG 的粉色边缘颗粒。
要求：
1. 使用 soft matte、despill、1px edge contract。
2. 如果是 atlas，先清理整张 atlas，再切组件。
3. 清理后重新打包，并确认 manifest 没有 possible #ff00ff chroma-key residue warning。
```

skill 会优先复用已安装的 `imagegen` chroma-key 清理脚本；如果背景不是纯色，再升级到 `rembg`、BiRefNet、PyMatting、Segment Anything 或本地编辑器流程。

## 7. 输出怎么放进游戏

### Godot

看 `godot/*.tscn`。常见映射：

- 面板：`NinePatchRect`
- 按钮：`TextureButton`
- 进度条：`TextureProgressBar`
- 图标：`TextureRect`

### Unity

把输出目录放到：

```text
Assets/GeneratedUI/<pack-name>/
```

然后运行生成的 Unity Editor importer，它会设置 Sprite、透明、mipmap 和边框。

### Cocos Creator

看：

```text
cocos/ui_pack_prefab_spec.json
```

把它当作 prefab/component 合同，交给 Cocos 编辑器脚本或 MCP 工具创建节点。

## 8. 验收标准

每次完成后，看这几件事：

| 检查项 | 通过标准 |
|---|---|
| `preview.png` | 能看出每个组件，边缘没有被裁掉 |
| `ui-asset-manifest.json` | warnings 为空，或每条 warning 都被解释 |
| 透明边缘 | 没有粉色/绿色/蓝色颗粒 |
| 按钮 | 至少有 normal，最好有 hover/pressed/disabled |
| 进度条 | 有 background 和 fill |
| 面板/按钮 | 有合理 nine-slice margins |
| 风格库生成 | 色卡、线条、材质、边框语言一致 |

## 9. 本地开发和测试

安装依赖：

```bash
python -m pip install -r requirements.txt
```

校验 skill：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/game-ui-asset-pipeline
```

检查脚本：

```bash
python -m py_compile skills/game-ui-asset-pipeline/scripts/package_ui_assets.py
python -m py_compile skills/game-ui-asset-pipeline/scripts/ingest_style_reference.py
```

查看命令帮助：

```bash
python skills/game-ui-asset-pipeline/scripts/package_ui_assets.py --help
python skills/game-ui-asset-pipeline/scripts/ingest_style_reference.py --help
```

## 10. 重要边界

- 这个 skill 不是图像生成模型。它会调用 Codex 当前可用的 `image_gen`、ComfyUI、LayerDiffuse、rembg、编辑器 MCP 等工具。
- 公开仓库不包含用户私有参考图。用户上传并沉淀的资料默认只保存在本地 `assets/style-library/`。
- 不建议把完整 UI 截图当成最终组件包。要扣出来或重新生成成独立组件，才能真正放进游戏项目复用。

## License

MIT
