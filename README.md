# Game UI Asset Pipeline Skill

这个 Skill 用来做一件事：

把提示词、参考图、用户上传的 UI 截图，变成能放进游戏项目里的独立 UI 组件。

它适合做：

- 面板背景图
- 按钮和按钮状态
- 进度条
- HUD 框
- 背包格子
- 地图节点
- 图标
- 九宫格可拉伸 UI
- 一整套同画风 UI 组件包

它不是单独的生图模型。它会让当前平台里已有的识图、生图、抠图、透明背景、图集、游戏引擎接入能力一起工作，然后把结果整理成可用的游戏 UI 资产包。

## 安装方式

### 方式一：安装到 Codex

在 Codex 里复制这段话：

```text
请用 $skill-installer 从 GitHub 安装这个 Skill：

repo: iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill
path: skills/game-ui-asset-pipeline

安装完成后提醒我重启 Codex。
```

重启 Codex 后，就可以在对话里使用：

```text
使用 $game-ui-asset-pipeline ...
```

### 方式二：安装到其他有识图和生图能力的平台

如果你用的不是 Codex，而是其他支持 Agent、Skills、插件、工作流、工具说明或知识库的平台，复制这段话给那个平台里的 AI：

```text
请读取这个 GitHub 仓库：
https://github.com/iwillwill-ALLWILL/codex-game-ui-asset-pipeline-skill

请把 skills/game-ui-asset-pipeline 作为一个可复用的游戏 UI 资产生成 Skill 安装到当前平台。

要求：
1. 保留 SKILL.md 里的触发说明和工作流。
2. 保留 references 里的工具选择、组件命名、风格库规则。
3. 保留 scripts 里的打包、manifest、预览图、风格库入库能力。
4. 如果当前平台不能直接运行 Python 脚本，就把脚本能力改造成当前平台可用的工具节点或工作流。
5. 安装后告诉我应该用什么话术调用它。
```

这个 Skill 要求目标平台至少具备其中一类能力：

| 能力 | 用来做什么 |
|---|---|
| 识图 | 分析参考图里的风格、色卡、组件结构 |
| 生图 | 根据提示词或参考图生成 UI 组件 |
| 图片编辑/抠图 | 把截图里的 UI 扣成透明 PNG |
| 文件读写 | 保存组件、manifest、预览图、风格库 |
| 脚本/工作流 | 批量命名、检查、打包、输出引擎文件 |

如果平台只有聊天能力，没有识图、生图、文件处理能力，这个 Skill 只能当提示词参考，不能完整产出资源。

## 它有哪几种用法

### 1. 根据参考图生成一套 UI 组件

你上传一张参考图，让 AI 按这个画风生成独立 UI 组件。

复制这段：

```text
使用 $game-ui-asset-pipeline，根据我上传的参考图生成一套游戏 UI 组件。

组件包括：
- 主面板背景
- 信息卡片背景
- 普通按钮
- 按下按钮
- 禁用按钮
- 血条底图
- 血条填充
- 金币图标
- 设置图标
- 背包格子

要求：
1. 不要生成完整游戏截图，只生成独立 UI 组件。
2. 不要把文字烘焙进图片，按钮文字后面交给游戏引擎。
3. 所有组件画风、色卡、描边、材质保持一致。
4. 面板和按钮要适合九宫格拉伸。
5. 输出透明 PNG；如果必须用纯色背景，生成后要清理干净边缘颗粒。

完成后给我：
- 所有组件 PNG
- preview.png
- ui-asset-manifest.json
- Godot / Unity / Cocos 可用的导入说明或脚手架
```

### 2. 从用户上传的 UI 截图里直接扣组件

适合你已经有一张好看的 UI 截图，只想把里面的组件拆出来。

复制这段：

```text
使用 $game-ui-asset-pipeline，从我上传的 UI 截图里扣出可复用组件。

目标组件：
- 任务面板
- 顶部进度条
- 角色信息面板
- 技能按钮框
- 地图节点图标
- 右侧菜单按钮

要求：
1. 尽量使用截图里的真实 UI 元素。
2. 去掉不需要的文字，只保留背景框、按钮框、图标和装饰。
3. 每个组件单独输出透明 PNG。
4. 裁切后加透明边距，不要贴边。
5. 检查并清理粉色、绿色、蓝色边缘颗粒。
6. 最后打包成可放进游戏项目的 UI 组件包。
```

### 3. 把用户上传的资料沉淀成长期风格库

适合团队或课程反复做同一个游戏项目风格。

你上传参考图、截图、风格说明，然后复制这段：

```text
使用 $game-ui-asset-pipeline，把我上传的资料沉淀成一个长期可复用的 UI 风格库。

风格名：<填写风格名>

要求：
1. 只保存我这次明确要求沉淀的资料。
2. 从参考图里提取色卡。
3. 总结这个风格的线条、材质、边框、角标、发光、图标规则。
4. 生成 style-card.md 和 palette.json。
5. 后续生成新 UI 时，必须优先读取这个风格库。
```

生成完风格库后，你以后可以这样用：

```text
使用 $game-ui-asset-pipeline，读取 <风格名> 这个风格库，生成一套新的战斗 HUD UI。

组件包括：
- 回合提示面板
- 角色头像框
- 血条底图和填充
- 4 个技能按钮状态
- 6 个地图节点图标

要求所有组件沿用风格库里的色卡、描边、材质、边框语言。
```

### 4. 清理 UI 素材边缘的粉色颗粒

很多生图流程会用粉色背景做临时透明底。直接裁切会留下粉色小点。

复制这段：

```text
使用 $game-ui-asset-pipeline，清理这些 UI 素材周围的粉色边缘颗粒。

要求：
1. 这不是普通裁切问题，要按 chroma-key spill 处理。
2. 如果是整张 atlas，先清理 atlas，再切组件。
3. 使用 soft matte、despill、边缘收缩和轻微羽化。
4. 清理后重新打包。
5. 检查 manifest，不要再出现 possible #ff00ff chroma-key residue warning。
```

### 5. 把已有 PNG 打包成游戏 UI 组件包

适合你已经有一组透明 PNG，只需要整理成游戏项目能用的结构。

复制这段：

```text
使用 $game-ui-asset-pipeline，把我提供的 PNG 文件夹打包成游戏 UI 组件包。

要求：
1. 自动识别 panel、button、progress_bar、icon、slot。
2. 自动识别按钮状态 normal、hover、pressed、disabled。
3. 自动识别进度条 background 和 fill。
4. 生成 preview.png 和 ui-asset-manifest.json。
5. 给出 Godot、Unity、Cocos 的导入结果或使用说明。
6. 如果 manifest 有 warnings，先解释并修复能修复的问题。
```

## 产出物是什么

一次完整任务通常会得到这些东西：

| 产出 | 作用 |
|---|---|
| 组件 PNG | 游戏里真正使用的 UI 图片 |
| `preview.png` | 快速检查所有组件是否正常 |
| `ui-asset-manifest.json` | 记录组件类型、尺寸、状态、九宫格建议、警告 |
| Godot `.tscn` | Godot 起步场景 |
| Unity import helper | 设置 Sprite、透明、边框 |
| Cocos prefab spec | 给 Cocos 创建 prefab 的结构说明 |
| `style-card.md` | 长期风格库说明 |
| `palette.json` | 从参考图提取的色卡 |

## 这个 Skill 主要解决什么问题

| 问题 | 解决方式 |
|---|---|
| 每次生图都像不同游戏 | 用风格库锁定色卡、材质、线条和边框规则 |
| 截图好看但不能直接进游戏 | 把截图拆成独立透明组件 |
| UI 图片有粉色边缘颗粒 | 用 chroma-key 清理流程处理边缘污染 |
| 按钮、进度条、面板命名混乱 | 自动整理成组件 manifest |
| 素材给到引擎还要重新配置 | 输出 Godot、Unity、Cocos 的起步导入结构 |
| 课程或团队想复用同一画风 | 把用户主动上传的资料沉淀进本地风格库 |

## 使用时要告诉 AI 的关键信息

你不需要讲技术细节，只要把这几件事说清楚：

```text
我要做什么游戏画风？
我上传的图是参考风格，还是要直接扣组件？
我要哪些组件？
要不要按钮状态？
要不要进度条 background / fill？
目标引擎是 Godot、Unity、Cocos，还是先通用？
是否要把这次资料沉淀成长期风格库？
```

## License

MIT
