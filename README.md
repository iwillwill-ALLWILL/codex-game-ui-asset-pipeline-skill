# Game UI Asset Pipeline Skill

这个 Skill 用来把用户自己的参考图、提示词、风格说明、UI 截图，变成可以放进游戏里的 UI 组件包。

它也可以当成一个游戏 UI 素材工具箱来用。不是只有“生成一整套 UI”才需要调用它；抠图、透明背景清理、图片缩小、图集切分、PNG 打包、PNG 转目标引擎起步文件这类小任务，也都可以统一走 `$game-ui-asset-pipeline`。

最推荐的路线是：

```text
用户上传资料
-> AI 提炼成项目风格库
-> AI 按风格库生成全套常用 UI 或指定 UI 组件
-> AI 清理透明背景、整理目录、按目标引擎输出可用文件
-> 用户看 overview.png，把问题截图发回 AI 修
-> 好结果继续沉淀进风格库
```

你不需要先学抠图、图集、九宫格、引擎 UI 节点、Python 脚本。能交给 AI 的就交给 AI。你要做的是：提供资料、说清楚需求、看结果、把截图和问题反馈给 AI。

## 这个 Skill 适合做什么

- 沉淀一个长期复用的项目 UI 风格库
- 按项目风格生成一整套常用游戏 UI
- 按当前需求补指定 UI 组件或素材
- 从一张参考图扩展同风格 UI
- 从 UI 截图或概念图里试拆组件
- 做简单 UI 帧动画，例如按钮呼吸、图标发光、奖励闪烁、进度条扫光、加载转圈、面板弹出
- 清理素材边缘粉色/绿色背景颗粒
- 批量抠图、去底、清理透明 PNG 的脏边和隐藏颜色
- 把过大的 PNG 高质量缩小到游戏里实际会用的尺寸
- 从图集或生成大图里切出单独组件，并检查有没有多切、少切、粘连
- 把已有透明 PNG 按目标引擎整理成可用组件包
- 生成 `overview.png`，方便快速检查整包素材
- 按目标引擎输出起步文件或导入说明，例如 Godot `.tscn`、Unity/Cocos 导入建议、generic PNG 包

它不是单独的生图模型。它会调度当前平台已有的识图、生图、抠图、透明背景、图集整理、文件读写、目标引擎输出能力。平台没有这些能力时，它只能作为提示词和流程参考，不能保证直接产出图片文件。

## 安装

### 安装到 Codex

在 Codex 里复制这段：

```text
请用 $skill-installer 从 GitHub 安装这个 Skill：

repo: iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill
path: skills/game-ui-asset-pipeline

安装完成后提醒我重启 Codex。
```

重启 Codex 后，后续任务这样开头：

```text
使用 $game-ui-asset-pipeline ...
```

### 安装到其他有识图和生图能力的平台

如果你不用 Codex，把这段给那个平台里的 AI：

```text
请读取这个 GitHub 仓库：
https://github.com/iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill

请把 skills/game-ui-asset-pipeline 安装成当前平台可复用的游戏 UI 资产生成 Skill。

要求：
1. 保留 SKILL.md 的触发说明和工作流。
2. 保留 references 里的组件清单、风格库规则、命名规则、工具选择规则。
3. 保留 scripts 里的风格库入库、overview 生成、分层打包、目标引擎输出能力。
4. 如果当前平台不能直接运行 Python 脚本，就把这些能力改造成当前平台可用的工具节点、插件动作或工作流。
5. 安装后告诉我应该怎么用自然语言调用它。
```

目标平台至少要有这些能力：

| 能力 | 用来做什么 |
|---|---|
| 识图 | 看懂参考图、UI 截图、色卡、组件结构 |
| 生图 | 生成按钮、面板、图标、进度条等 UI 资产 |
| 图片编辑/抠图 | 处理透明背景、边缘残留、截图拆分 |
| 文件读写 | 保存风格库、PNG、overview、目标引擎文件 |
| 脚本/工作流 | 批量命名、检查、分类、打包 |
| 图片缩放 | 把大图高质量降采样成游戏实际尺寸，避免强缩后噪点糊在一起 |

## 它也可以当常用小工具用

不想生成完整 UI 包时，直接把 `$game-ui-asset-pipeline` 当素材处理入口用。这样做的好处是：同一套命名、透明背景、尺寸、overview、目标引擎输出规则都会保持一致，不会每次临时处理出一堆散乱文件。

| 小功能 | 什么时候用 | 你可以怎么说 |
|---|---|---|
| 抠图 / 去底 | 有 PNG/JPG，但背景不是透明 | `使用 $game-ui-asset-pipeline，把这些图片抠成透明 PNG，一张图只保留一个素材。` |
| 清理边缘残留 | 透明图周围有粉色、绿色、青色、暗色脏边 | `使用 $game-ui-asset-pipeline，清理这批透明 PNG 的边缘残留和隐藏背景色。` |
| 高质量缩小 | 大图放进游戏后被强制缩小，出现噪点、糊边、细节粘在一起 | `使用 $game-ui-asset-pipeline，把这些 PNG 高质量缩小到最长边 512，透明边缘不能脏。` |
| 图集切分 | 一张大图里有多个按钮、图标、面板 | `使用 $game-ui-asset-pipeline，从这张图集里切出独立组件，每张 PNG 只能有一个完整组件。` |
| PNG 分类整理 | 已经有一堆 PNG，但命名和目录混乱 | `使用 $game-ui-asset-pipeline，把这个 PNG 文件夹按 panels、buttons、icons、bars 分类整理。` |
| PNG 转目标引擎 UI 包 | 已有透明 PNG，想直接进项目 | `使用 $game-ui-asset-pipeline，把这些 PNG 打包成我项目可用的 UI 组件包。如果我给了项目路径，先自动识别引擎；识别不出再问我。` |
| 动态化 UI 组件 | 想让按钮、图标、奖励、进度条有简单动效 | `使用 $game-ui-asset-pipeline，把这个按钮做成 8 帧循环呼吸发光动画，输出透明 PNG 帧、preview.gif 和目标引擎接入说明。` |
| 生成 overview | 想快速预览一批素材有没有问题 | `使用 $game-ui-asset-pipeline，给这个素材包重新生成 overview.png。` |
| 检查素材质量 | 不确定有没有多切、少切、透明脏边、尺寸过大 | `使用 $game-ui-asset-pipeline，检查这批 UI 素材是否能直接放进游戏。` |

这些小工具任务也应该遵守最终交付规则：

| 规则 | 标准 |
|---|---|
| 一张图一个对象 | 不要有两个半截组件、粘连邻居、残留边条 |
| 透明图真透明 | 可见边缘不能有 key color，alpha 为 0 的像素也不能藏青色/粉色/绿色 RGB |
| 缩放后能用 | 在目标尺寸 100% 查看不糊、不脏、不出彩边 |
| UI 动画稳定 | 每帧同尺寸、同锚点、边缘干净，有 `preview.gif`，循环首尾不跳 |
| 目录干净 | 公共输出只保留最终 PNG、overview 和用户要求的引擎文件 |
| 先识别目标引擎 | 有项目路径时先自动识别；没有项目路径、识别失败或混合工程时再问；不确定时输出 generic PNG 包 |

常用命令背后会优先复用 skill 里的脚本和平台工具：

```bash
# 清理透明边缘和隐藏 key-color RGB
python <skill-root>/scripts/clean_alpha_fringe.py \
  --input <png-or-folder> \
  --backup <backup-folder> \
  --report-json <qa-report.json>

# 高质量缩小透明 PNG，避免大图强缩后变脏变糊
python <skill-root>/scripts/resize_assets_high_quality.py \
  --input <png-or-folder> \
  --output <final-size-folder> \
  --max-side 512 \
  --denoise auto \
  --sampler area-lanczos \
  --prefilter 0.18

# 把 PNG 打包成分类目录、overview 和目标引擎导入文件
python <skill-root>/scripts/package_ui_assets.py \
  --input <folder-with-pngs> \
  --output <output-folder> \
  --pack-name <pack-slug> \
  --engines auto \
  --project <game-project-root> \
  --category-subdirs
```

如果没有本地项目路径，就去掉 `--project`；`--engines auto` 会输出通用 PNG 包。用户明确指定 Godot、Unity、Cocos 或 generic 时，再把 `--engines auto` 改成对应目标。

## 最推荐的三种用法

先记住这个优先级：

| 优先级 | 用法 | 适合什么情况 |
|---|---|---|
| 1 | 项目风格库 -> 全套常用 UI | 正式项目起步，要统一画风和完整组件包 |
| 2 | 项目风格库 -> 指定 UI/素材 | 项目中途缺按钮、图标、面板、道具、HUD |
| 3 | 当前参考图 -> 临时生成 UI | 还没建风格库，但想先按一张图试做 |

从概念图里硬拆组件放在后面。它能做，但不是首推产线。概念图通常不是源文件分层，边框、阴影、文字、背景已经烘焙在一起，边缘不一定能像 PSD/Figma 那样完整分离。

## 1. 沉淀用户自己的项目风格库

项目风格库是这个 Skill 的核心。它保存的是用户主动上传、主动要求沉淀的资料，不会静默保存一次性图片。

风格库会持续保存和整理：

| 内容 | 用途 |
|---|---|
| 核心参考图 | 锁定画风、材质、线条、构图语言 |
| 色卡 | 控制整套 UI 不跑色 |
| 风格卡 | 记录边框、角标、按钮状态、图标、光影规则 |
| 参考提示词 | 保存用户认可的描述方式 |
| 成功生成结果 | 作为后续生成的高权重样板 |
| 失败反馈 | 写进 avoid-list，避免反复跑偏 |
| 标签和索引 | 多个项目风格之间能检索和区分 |

### 第一次创建风格库

准备这些资料，能给多少给多少：

| 资料 | 怎么给 AI |
|---|---|
| 参考图 | 上传截图、概念图、UI 图、资产图 |
| 风格说明 | 直接用自然语言描述 |
| 参考提示词 | 贴之前用过的 prompt |
| 不想要的方向 | 说清楚哪些颜色、质感、形状不要 |
| 目标组件 | 说清楚最终要按钮、面板、卡牌、HUD 还是全套 |

复制这段给 AI：

```text
使用 $game-ui-asset-pipeline，把我上传的资料沉淀成一个长期可复用的项目 UI 风格库。

风格名：<填写风格名>

任务：
1. 先看我上传的所有参考图、提示词和说明。
2. 不要把资料全部等权重使用，先筛掉噪音。
3. 提炼最稳定的色卡、线条、材质、边框、角标、按钮状态、图标规则。
4. 把最契合目标画风的参考图标成 anchor。
5. 把有帮助但不是核心的参考标成 support。
6. 把参考提示词和成功提示词保存进 prompt bank。
7. 把跑偏方向写进 avoid-list。
8. 生成风格卡、色卡和风格库索引。

输出：
1. 告诉我这个风格库的名称。
2. 用短表格总结色卡、材质、线条、边框、图标规则。
3. 告诉我哪些资料被当成核心参考，哪些被当成辅助参考，哪些被排除。
4. 后续生成 UI 时默认读取这个风格库。
```

### 一次上传很多资料时怎么处理

资料越多，不代表越好。AI 要做的是提炼精华，不是把所有图和文档都塞进 prompt。

| 角色 | 什么时候用 | 对后续生成的影响 |
|---|---|---|
| `anchor` | 最像目标项目的核心参考 | 最高，决定主色、线条、材质、边框 |
| `accepted-output` | 用户已经确认效果好的生成结果 | 很高，作为成功样板 |
| `support` | 有帮助但不是核心的辅助参考 | 中等，用来确认共性 |
| `prompt` | 参考提示词、成功提示词、风格说明 | 影响描述方式 |
| `rejected` | 失败结果或跑偏样例 | 不正向学习，只写进 avoid-list |
| `noise` | 不相关、低质量、风格冲突资料 | 丢弃或只记录为什么不要 |

复制这段给 AI：

```text
使用 $game-ui-asset-pipeline，整理我上传的大量资料，更新 <风格名> 项目风格库。

要求：
1. 先做资料筛选，不要全部等权重入库。
2. 只保留最能代表目标画风的资料作为 anchor。
3. 我确认过好看的生成结果标成 accepted-output。
4. 普通辅助资料标成 support。
5. 文档只提炼会影响 UI 风格和组件生成的精华，不要整篇塞进提示词。
6. 跑偏、过亮、过现代、边缘脏、色卡冲突的内容写进 rejected/avoid-list。
7. 后续生成时，以风格卡、色卡、anchor、accepted-output 为主，rejected/noise 只作为避坑。

完成后告诉我：
1. 保留下来的核心风格是什么。
2. 被排除的噪音是什么，为什么排除。
3. 后续生成 UI 时应该遵守哪些风格规则。
```

### 用户确认效果好后继续沉淀

每次生成后，如果你觉得效果好，不要只说“不错”。让 AI 把结果写回风格库，后面会越来越稳。

```text
使用 $game-ui-asset-pipeline，把这次我确认效果好的 UI 组件沉淀进 <风格名> 风格库。

要求：
1. 把最终图片或最终提示词标成 accepted-output。
2. 总结这次成功的色卡、材质、边框、图标和按钮状态经验。
3. 更新风格卡和 prompt bank。
4. 后续生成同项目 UI 时优先参考这次成功结果。
```

如果效果不好，直接把问题发回 AI：

```text
使用 $game-ui-asset-pipeline，把这次失败原因写进 <风格名> 风格库的 avoid-list。

失败点：
- <比如：颜色太亮>
- <比如：边框太现代>
- <比如：按钮状态不明显>
- <比如：图标不像同一个游戏>

要求：
1. 不要把这批失败图当成正向参考。
2. 只记录失败原因和下次避免规则。
3. 重新生成时必须避开这些问题。
```

## 2. 生成全套常用游戏 UI

这是正式项目最推荐的产线：先有风格库，再生成完整 UI 组件包。

复制这段给 AI：

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 项目风格库，生成一套完整常用游戏 UI 组件包。

任务：
1. 不要生成完整游戏截图，只生成独立可复用 UI 组件。
2. 按内置完整 UI 组件清单生成，覆盖常见游戏 UI 需求。
3. 每个组件都要对应成熟 UI/control 原型，比如按钮、进度条、滑条、面板、列表、标签页、卡牌、背包格子、HUD、地图节点、图标。
4. 所有组件沿用风格库的色卡、线条、边框、材质、图标规则。
5. 不要把文字烘焙进图片，文字交给游戏引擎。
6. 按类别分批生成，质量优先，不要强行塞进一张大图。
7. 面板、按钮、卡框要适合九宫格拉伸。
8. 如果我提供项目路径，先自动识别目标引擎；没有项目路径或识别不出时再问我。

输出目录：
1. 根目录有 overview.png。
2. 每个层级有自己的 overview.png。
3. PNG 按 panels、buttons、bars、cards、slots、hud、icons、frames、images 分类。
4. 引擎文件放到对应引擎文件夹；如果目标引擎不确定，先输出 generic PNG 包。
```

常用 UI 组件清单覆盖这些大类：

| 类别 | 应该包含什么 |
|---|---|
| panels / frames | 窗口、大中小面板、弹窗、tooltip、顶部栏、侧栏、分割线、角标、底纹 |
| buttons | primary、secondary、danger、confirm、cancel、back、close、tab、toggle、checkbox、radio，全状态 |
| bars / sliders | health、mana、stamina、xp、loading、cooldown、capacity、slider，背景和填充分开 |
| cards / slots | 角色卡、物品卡、技能卡、任务卡、奖励卡、背包格、装备格、稀有度框 |
| HUD | 血量资源区、货币区、任务追踪、通知、迷你地图、计时器、波次、分数 |
| menus | 主菜单、暂停、设置、背包、装备、技能、商店、制作、任务、结算 |
| map / progression | 地图节点、路径、当前/完成/锁定/商店/boss/事件状态 |
| battle / status | 技能按钮、回合顺序、目标标记、buff、debuff、伤害/治疗标签 |
| icons | 导航、资源、属性、状态、稀有度、职业、地图、操作图标 |
| decoration atoms | 铆钉、边角、徽章、横幅、丝带、发光、划痕、材质贴片 |

这个清单不是凭空想出来的。它综合了成熟 UI/control 体系和游戏资产分类：Godot 控件、Unity UI Toolkit、Cocos Creator UI 组件、Dear ImGui 常见控件、Material Design 组件分类、Kenney UI Pack、Game-icons.net、OpenGameArt GUI 资源分类。

参考来源：

| 来源 | 主要借鉴什么 |
|---|---|
| [Godot Control / UI 节点](https://docs.godotengine.org/en/stable/classes/class_control.html) | Godot 控件基类和 UI 组织方式 |
| [Unity UI Toolkit](https://docs.unity3d.com/Manual/UIElements.html) | 通用控件族、列表、树、选择器、按钮等 |
| [Cocos Creator UI 组件](https://docs.cocos.com/creator/manual/en/ui-system/components/editor/button.html) | 游戏引擎中的按钮、滑条、进度条、滚动视图等控件 |
| [Dear ImGui](https://github.com/ocornut/imgui) | 游戏工具 UI 的按钮、滑条、树、表、菜单、弹窗等控件形态 |
| [Material Design Components](https://m3.material.io/components) | 通用 UI 组件分类和交互状态 |
| [Kenney UI Pack](https://kenney.nl/assets/ui-pack) | 游戏 UI 资产包常见分类 |
| [Game-icons.net](https://game-icons.net/) | 游戏图标分类和常用符号覆盖面 |
| [OpenGameArt GUI](https://opengameart.org/art-search-advanced?keys=gui) | 开源游戏 GUI 资产分类参考 |

## 3. 按当前需求生成指定 UI 组件或素材

如果你不需要全套，只缺几个组件，就让 AI 只做这次需要的东西。

复制这段：

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 项目风格库，只生成我这次需要的 UI 组件和素材。

目标：
- <例如：4 个技能按钮，normal/hover/pressed/disabled>
- <例如：1 个 boss 血条底图和填充图>
- <例如：8 个状态图标>
- <例如：1 个奖励弹窗面板>
- <例如：3 个稀有度物品框>

要求：
1. 只生成这些目标，不要生成全套。
2. 沿用风格库里的色卡、线条、材质、边框、按钮状态、图标规则。
3. 每个组件都要是独立透明 PNG。
4. 需要状态的组件要输出完整状态。
5. 进度条、滑条要把 background/track/fill/handle 分开。
6. 如果我提供项目路径，先自动识别目标引擎；没有项目路径或识别不出时再问我，然后输出 overview.png 和对应导入说明。
7. 输出目录按类别整理，不要塞成一堆散图。

验收：
1. 打开 overview.png 能看清所有组件。
2. 组件之间画风一致。
3. 边缘没有背景残留。
4. 没有不该烘焙进去的文字。
```

如果你要的不是 UI 控件，而是 UI 里会用到的素材，也可以这样说：

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 项目风格库，生成一批 UI 里要用的素材。

素材清单：
- <例如：金币、钥匙、药水、火把、绳索、食物图标>
- <例如：职业徽章、状态图标、地图节点图标>
- <例如：按钮角标、铆钉、横幅、封蜡、发光边框>

要求：
1. 这些素材要和 UI 组件同画风。
2. 透明 PNG。
3. 不要生成完整界面截图。
4. 按 icons、badges、decorations、materials 分类输出。
5. 生成 overview.png 方便检查。
```

## 4. 临时根据一张参考图生成同风格 UI

如果还没建立风格库，但你有一张参考图，可以先临时试做。

```text
使用 $game-ui-asset-pipeline，根据我上传的参考图，生成同风格的独立游戏 UI 组件。

目标组件：
- <写清楚要什么>

要求：
1. 先分析参考图的色卡、描边、材质、边框、按钮状态、图标风格。
2. 不要直接生成完整界面，只生成独立组件。
3. 组件透明背景。
4. 面板和按钮要适合九宫格拉伸。
5. 输出 overview.png 和目标引擎导入说明。

完成后问我是否要把这张参考图和本次结果沉淀成项目风格库。
```

## 5. 从 UI 截图或概念图里拆组件

这个功能适合快速试拆、复用截图里已经清晰可见的元素，或分析一个 UI 的层级结构。

它不是最稳的正式产线。截图里的边框、阴影、文字、背景常常已经粘在一起，AI 只能根据可见像素判断边界。背景残留可以清理，但边框少一块、多一块，有时是源图本身不可分。

复制这段：

```text
使用 $game-ui-asset-pipeline，从我上传的 UI 截图里拆出可复用组件。

要求：
1. 先分析图里有哪些 UI 组件：面板、按钮、进度条、图标、卡牌、背包格子、HUD、地图节点等。
2. 根据这张图设计从大到小的拆分层级，不要机械套固定五层。
3. 默认输出所有有用层级。
4. 每个层级单独一个文件夹。
5. 每个组件单独输出透明 PNG。
6. 边框宁可多留一点，也不要切掉描边。
7. 如果某个组件和背景不可分，要明确标注为近似结果，并建议用风格库重新生成。
8. 输出 overview.png 和目标引擎导入说明。
```

拆分层级要按具体图自适应。比如复杂卡牌可以是：

| 层级 | 内容 |
|---|---|
| `level_01_card_complete` | 完整卡牌 |
| `level_02_card_frame_dividers_decor` | 外框 + 内部分割线 + 内部装饰 |
| `level_03_card_frame_dividers` | 外框 + 内部分割线 |
| `level_04_card_outer_frame` | 只有外轮廓 |
| `level_05_card_atomic_parts` | 外框、分割线、装饰、背景、icon、人物立绘全部拆开 |

简单按钮可能只有三层，复杂 HUD 可能有七层。原则是：只要这个粒度对复用有价值，就输出；没有价值的空层不要输出。

## 6. 清理粉色/绿色背景残留

很多生图流程会用粉色或绿色做临时透明底。直接裁切会留下边缘颗粒，这叫 chroma-key spill，不是普通裁剪问题。

复制这段：

```text
使用 $game-ui-asset-pipeline，清理这批 UI 素材周围的粉色/绿色边缘颗粒。

要求：
1. 先判断 key color 是否和 UI 色卡撞色。
2. 如果撞色，换安全背景色或重新生成透明 PNG。
3. 如果是整张 atlas，先清理 atlas，再切组件。
4. 用 soft matte、despill、边缘轻微收缩和羽化处理。
5. 清理后重新生成 overview.png。
6. 在深色和浅色背景上检查边缘。
7. 发现残留就返工，不要直接交付。
```

如果问题不是粉色颗粒，而是边框和背景粘在一起，用这段：

```text
使用 $game-ui-asset-pipeline，重新处理这批从概念图里拆出的 UI 组件边缘。

要求：
1. 先判断问题是背景残留，还是 UI 边框和背景不可分。
2. 每个组件先保守扩大裁切范围，不要切掉边框。
3. 优先使用现有开源分割、抠图、alpha matting 工具，不要只靠颜色阈值。
4. mask 后处理可以 close/dilate 1-3px 保住描边，再轻微 feather。
5. 深色和浅色背景都要检查。
6. 如果源图边缘被文字、阴影、场景背景遮挡，就停止硬拆，改成按风格库重新生成。
```

可用开源方向：

| 工具 | 适合做什么 |
|---|---|
| [SAM 2](https://github.com/facebookresearch/sam2) | 点选/框选式分割 UI 大块区域 |
| [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) | 高质量前景分割 |
| [rembg](https://github.com/danielgatis/rembg) | 简单独立素材的批量背景移除 |
| [PyMatting](https://github.com/pymatting/pymatting) | 有 trimap 时处理抗锯齿、发光、软边 |

## 7. 把已有 PNG 打包成目标引擎 UI 组件包

如果你已经有透明 PNG，只想整理成游戏项目能用的结构：

```text
使用 $game-ui-asset-pipeline，把我提供的 PNG 文件夹打包成游戏 UI 组件包。

目标引擎：<自动识别项目 / Godot / Unity / Cocos / generic>

要求：
1. 自动识别 panel、button、progress_bar、icon、slot。
2. 自动识别按钮状态 normal、hover、pressed、disabled、selected。
3. 自动识别进度条 background、track、fill、handle。
4. 大包按 panels、buttons、bars、cards、slots、hud、icons、frames、images 分类。
5. 根目录保留 overview.png。
6. 每个层级保留自己的 overview.png。
7. 如果提供了游戏项目路径，先根据项目代码自动识别目标引擎；识别失败或混合工程时再询问；不确定引擎时输出 generic PNG 包。
```

## 产出目录长什么样

一次完整 UI 包通常长这样：

```text
<pack>/
├── overview.png
└── level_01_complete_ui_kit/
    ├── overview.png
    ├── png/
    │   ├── panels/
    │   ├── buttons/
    │   ├── bars/
    │   ├── cards/
    │   ├── slots/
    │   ├── hud/
    │   ├── icons/
    │   ├── frames/
    │   └── images/
    └── <engine>/
```

默认不要把风格库、debug、JSON、中间裁剪图混进组件交付目录。风格库是长期记忆，组件包是这次要放进游戏里的结果。

## 怎么验收结果

生成完成后，你主要看这些：

| 看什么 | 通过标准 |
|---|---|
| `overview.png` | 能一眼看到所有组件，分类清楚 |
| 画风 | 色卡、线条、材质、边框、图标像同一个游戏 |
| 透明背景 | 没有粉色、绿色、场景背景残留 |
| 按钮状态 | normal、hover、pressed、disabled 区分明显 |
| 进度条 | background/track/fill 分开，能在引擎里组合 |
| 面板/按钮 | 边角没有被切掉，适合九宫格拉伸 |
| 文字 | 默认不烘焙文字，后续交给引擎文本节点 |
| 目标引擎 | 有对应导入说明、起步文件或可导入结构 |

发现问题时，不要自己猜怎么修。把 `overview.png` 或问题截图发给 AI：

```text
使用 $game-ui-asset-pipeline，修正这批 UI 组件。

问题：
- <贴截图或描述：哪个组件哪里不对>

要求：
1. 保持原来的风格库和目录结构。
2. 只重做有问题的组件。
3. 修完重新生成 overview.png。
4. 如果问题来自源图不可分，告诉我应该改为重新生成哪个组件。
```

## 常见任务怎么说

### 做一个新项目的完整 UI 包

```text
使用 $game-ui-asset-pipeline，先把我上传的参考图和说明沉淀成 <风格名> 风格库，再用这个风格库生成完整常用游戏 UI 组件包。

目标引擎：<自动识别项目 / Godot / Unity / Cocos / generic>

要求：
1. 先提炼风格，不要直接生图。
2. 组件按完整清单覆盖常见游戏 UI。
3. 有项目路径时先自动识别目标引擎，再输出对应导入说明或起步文件。
4. 输出后给我 overview.png，方便我反馈修改。
```

### 只补一个界面要用的素材

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 风格库，为我的 <界面名> 补齐这批 UI 组件：

- <组件 1>
- <组件 2>
- <组件 3>

要求：
1. 只做这些，不要生成全套。
2. 保持同画风。
3. 有项目路径时先自动识别目标引擎；没有项目路径、识别失败或混合工程时再问，然后输出透明 PNG、overview.png 和对应导入说明。
```

### 让 AI 自己判断该生成哪些 UI

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 风格库，根据我这个游戏需求，判断需要哪些常用 UI 组件并生成。

游戏类型：<比如：肉鸽地牢 / 模拟经营 / 卡牌战斗 / 生存探索>
主要界面：<写几个界面>
目标引擎：<自动识别项目 / Godot / Unity / Cocos / generic>

要求：
1. 先列出建议生成的组件清单。
2. 清单要基于成熟 UI/control 原型，不要凭空想。
3. 我确认后再生成。
4. 按目标引擎输出；不确定时先输出 generic PNG 包。
```

## 功能边界

- 正式生产首推“风格库生成独立组件”，不是“从概念图硬拆”。
- 截图拆分能复用可见像素，但不能恢复不存在的源图层。
- 复杂边缘可以用分割、抠图、alpha matting 改善，但源图遮挡或粘连时仍要重新生成。
- 文字默认不要烘焙进图片，除非你明确要文字美术字。
- 生成引擎文件前先识别或确认目标引擎。用户不确定时，先交付 generic PNG 包、overview 和导入说明。

## License

MIT
