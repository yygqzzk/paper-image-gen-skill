---
name: paper-image-gen
description: 为学术论文生成配图 - 支持对话模式和自动迭代模式。支持实验绘图（Python代码路径）和论文架构图（API路径）两种类型。兼容 Claude Code 和 Codex。触发词：/paper-image-gen、画图、生成配图、论文图、架构图、流程图、实验图、可视化。
---

# Paper Image Gen Skill

为学术论文生成高质量配图，支持实验数据可视化和架构示意图两种场景。

> **平台兼容**：支持 Claude Code 和 Codex。图片生成后：Claude Code 用 Read 工具内联展示；Codex 输出文件绝对路径，告知用户自行查看。其余操作（脚本执行、文件读写）两平台相同。

## 参数解析

从用户输入中解析以下参数：
- `--ralph`：启用 Ralph 自动模式（默认为对话模式）
- `--max-rounds N`：最大迭代轮数（默认 8，配置文件 `default_max_rounds` 可覆盖）
- `--output PATH`：指定输出路径
- `--path [a|b]`：强制指定生成路径（a=Python代码, b=API生成）；显式指定时跳过路径推荐，不发出警告
- 其余文本为用户的图片描述（原始需求）

## 配置读取

**首次运行 Path B（API 生成）时**，检查配置文件 `~/.claude/image-gen.json` 是否存在：

1. 如果不存在，依次询问用户：`api_url`（Gemini Image API 完整 URL）和 `api_key`
2. 将配置写入 `~/.claude/image-gen.json`，执行 `chmod 600 ~/.claude/image-gen.json`
3. 提醒用户：此文件包含 API Key，请勿提交到版本控制

也支持环境变量 `IMAGE_GEN_URL` 和 `IMAGE_GEN_API_KEY`（优先级高于配置文件）。

**两条路径均读取的配置字段**（无论是否使用 API）：
- `default_max_rounds`：作为 `--max-rounds` 的默认值（用户显式传入时以用户值为准）
- `paper_domain`：论文领域默认值（CV / NLP / 图学习 / 其他），可在需求澄清时覆盖
- `target_venue`：目标会议/期刊默认值，可在需求澄清时覆盖

**API 凭证校验**（`api_url`、`api_key`）仅在 Path B 执行。

## 需求澄清（仅对话模式）

### 规则

- 每轮只问一个问题，优先使用选择题（A/B/C 格式）
- 不限轮数，可追问/深入
- **4 个核心维度**全部明确后，Claude 自主判断是否充分进入下一步：
  1. **图片类型**：实验绘图 / 论文架构图
  2. **论文领域**：CV / NLP / 图学习 / 其他（配置文件中有默认值时可跳过）
  3. **目标会议/期刊**：NeurIPS / CVPR / ICML / Nature / 学位论文 / 其他（可选，无则"通用学术标准"；配置文件中有默认值时可跳过）
  4. **核心内容**：具体图表元素、实验数据、模型结构等

### 跳过规则

- 用户描述已包含某维度信息 → 跳过该问题
- 实验绘图时用户已提供数据（表格/CSV/JSON）→ 跳过"数据说明"追问
- 配置文件中 `paper_domain` / `target_venue` 有值 → 可跳过对应问题（但用户仍可覆盖）
- 信息矛盾时优先追问澄清，不假设

### 结束判断

- 4 个维度均明确（会议/期刊维度允许"无"）→ 自动进入「路径推荐」
- Claude 判断追加问题对质量无显著提升 → 提前结束

### Ralph 模式

跳过此阶段，直接分析用户原始描述，进入路径推荐。

## 路径推荐

根据图片类型推荐生成路径，说明理由，用户可接受或通过 `--path` 覆盖：

| 图片类型 | 默认推荐 | 推荐理由 |
|---------|---------|---------|
| 实验绘图（有数据） | Path A（Python 代码） | 数据驱动，精确可控，支持迭代修改 |
| 论文架构图 | Path B（API 生成） | 需要创意视觉表达，文本生图更适合 |
| 实验绘图（无数据，仅示意） | Path B（API 生成） | 无数据时示意图更合适 |

`--path a/b` 显式指定时，跳过推荐直接执行，不发出警告，不做类型校验。

## Path A：Python 代码生成（实验绘图）

### 数据输入方式

- 用户直接在对话中粘贴数据（表格、JSON、CSV 内容）→ Claude 将数据硬编码到生成的代码中
- 用户提供文件路径 → Claude 在代码中使用 `pd.read_csv(path)` 或 `np.loadtxt(path)` 读取
- 用户无数据时 → 建议切换到 Path B 生成示意图

### 执行流程

1. Claude 根据需求 + `academic-chart` 模板生成 Python 代码
2. 展示代码给用户，说明推荐图表类型及理由
3. **Claude 直接执行**（默认）：将代码写入唯一临时文件后执行
   - 临时文件名含时间戳：`/tmp/paper_img_$(date +%s).py`
   - 代码中必须使用 `plt.savefig(output_path, dpi=300, bbox_inches='tight', format='png')`，不使用 `plt.show()`
   - 输出路径遵循「图片保存」章节约定
   - 执行成功后，读取生成的图片展示给用户（详见顶部平台兼容说明）
4. 用户反馈 → **基于上轮代码 + 反馈修改**（保留已确认的改进），重新执行（迭代）

### 依赖管理

- 默认仅使用 `matplotlib` + `numpy`（无需 pip install）
- 需要 `seaborn` / `pandas` 时，先执行 `python3 -c "import seaborn"` 检查可用性
- 不可用时：降级到 matplotlib 实现，或提示用户 `pip install seaborn` 后重试
- 不使用 `plotly`（需要 GUI 环境，不适合 Claude 直接执行）

### 代码输出规范

- 图片格式：PNG，`dpi=300`（印刷标准）
- 图幅尺寸默认双栏 `figsize=(6.75, 4.0)`，代码注释中提供单栏 `figsize=(3.25, 2.5)` 供用户切换
- 字体大小：坐标轴标签 10-12pt，标题 12-14pt，图例 9-10pt

### Path A 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| `ModuleNotFoundError` | 检查是否可降级到 matplotlib；若需 seaborn/pandas，提示 `pip install` 后重试 |
| 语法错误 / NameError | 自动修复代码后重试（最多 2 次）；仍失败则展示代码让用户自行运行 |
| 执行超时（>60s） | 显示超时信息，建议用户自行运行代码 |
| 文件路径错误 | 提示用户确认数据文件路径或手动创建 `figures/` 目录 |
| 图片为空 / 渲染异常 | 读取图片文件评估，修改代码后重试 |

### Path A Ralph 模式

1. Claude 自动选择图表类型，生成代码并执行
2. 读取输出图片进行 5 维度评估：
   - **匹配度**：图片内容与用户描述是否一致
   - **布局清晰度**：结构清晰、元素排列合理
   - **标签可读性**：坐标轴/图例/标注清楚
   - **学术适用性**：配色专业，符合目标会议/期刊标准
   - **数据准确性**：数据点/趋势/比例正确呈现
3. 不满意 → 自动修改代码重新执行
4. 满意或连续 2 轮无提升 → 交付用户确认

## Path B：API 图片生成（论文架构图）

### 执行流程

1. Claude 基于需求 + `arch-diagram` 模板生成英文 prompt
2. **对话模式**：展示 prompt 给用户确认（可直接确认或修改）
3. 调用脚本生成图片：`python3 ~/.claude/scripts/image-gen.py --prompt "完整prompt" --output "输出路径"`
4. 检查脚本输出：`OK:` 成功，`ERROR:` 失败
5. 成功时：读取生成的图片展示给用户
6. 用户反馈 → 基于**原始描述 + 本轮反馈**重新生成 prompt（不在上轮 prompt 上累积）→ 确认后重新生成（迭代）

### Path B 错误处理

| 脚本输出 | 处理方式 |
|----------|----------|
| `ERROR:NETWORK:...` | 提示检查网络或 API URL，不计入迭代次数 |
| `ERROR:API:429...` | 等待 10 秒后重试一次 |
| `ERROR:API:...` | 显示错误信息给用户 |
| `ERROR:CONFIG:...` | 引导用户重新配置（删除旧配置文件，重新走首次运行流程） |
| `ERROR:DECODE:...` / `ERROR:IO:...` | 显示错误信息，建议检查输出路径 |

### Path B Ralph 模式

1. 自动生成 prompt（含增强模板），自动调用脚本
2. 成功时读取图片，进行 5 维度评估：
   - **匹配度**：图片内容与用户描述是否一致
   - **布局清晰度**：结构清晰、元素排列合理
   - **标签可读性**：文字标注清楚、无乱码
   - **学术适用性**：适合论文印刷、配色专业
   - **伪影检查**：无明显生成伪影或变形
3. 不满意 → 基于原始描述 + 评估结果自动优化 prompt，继续迭代
4. 满意或连续 2 轮评估无提升 → 交付用户确认

## 内置模板：academic-chart（实验绘图）

**角色**：就职于顶级科学期刊（Nature, Science）或顶级 AI 会议（CVPR, NeurIPS）的资深数据可视化专家。

### 推荐图表类型库（从中选 1-2 种，说明理由）

| 类别 | 图表类型 | 适用场景 |
|------|---------|---------|
| 数值对比 | 纵向/横向柱状图 | SOTA 对比（方法名短用纵向，名长用横向） |
| 数值对比 | 雷达图 | 多维度综合能力评估（≥4 维度） |
| 数值对比 | 帕累托前沿图 | 两指标权衡（精度 vs 速度） |
| 数值对比 | 堆叠柱状图 | 时间/资源细分构成 |
| 趋势收敛 | 带置信阴影折线图 | 训练 Loss/Accuracy（含标准差） |
| 趋势收敛 | 局部放大折线图 | 多模型后期收敛差异微小时 |
| 模型评估 | ROC 曲线 | 均衡数据集二分类，配 AUC 标注 |
| 模型评估 | PR 曲线 | 不平衡数据集（正样本极少） |
| 矩阵可视化 | 热力图 | 混淆矩阵、多任务性能矩阵 |
| 矩阵可视化 | 散点图+对角线 | 预测值 vs 真实值相关性 |
| 矩阵可视化 | 气泡图 | 散点+第三维（参数量/FLOPs） |
| 统计分布 | 小提琴图 | 数据概率密度分布（优于箱线图） |
| 统计分布 | 箱线图 | 多组数据分布范围+离群点 |
| 复合布局 | 双 Y 轴图 | 两个量纲不同变量同图 |
| 复合布局 | 分面网格图 | 对比变量过多时矩阵拆分 |

### 配色策略（按目标会议/期刊）

根据 `target_venue` 选择：
- NeurIPS/ICML：colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
- CVPR/ICCV：colors = ['#2196F3', '#FF9800', '#4CAF50', '#F44336']
- Nature/Science/学位论文/其他/默认：colors = ['#0072B2', '#E69F00', '#009E73', '#D55E00']（色盲友好）

### 图幅规范

默认双栏，代码中写入注释供用户切换：
- 双栏（默认）：figsize=(6.75, 4.0)
- 单栏：figsize=(3.25, 2.5)

### 尺度处理（数据差异悬殊时必须处理）

- 组间差异 >5×：提供断裂坐标轴方案（brokenaxes 可选，降级到矩形标注说明）
- 跨越数量级：使用对数坐标 ax.set_yscale('log')
- 关注相对提升：归一化到基线=100%

### 统计要素

- 多次实验数据（有均值+标准差）：必须添加误差线
- 单次实验数据：不强行添加

### 字体规范（代码开头设置）

matplotlib.rcParams.update 设置：font.size=10, axes.titlesize=12, axes.labelsize=10, xtick.labelsize=9, ytick.labelsize=9, legend.fontsize=9, font.family='serif'

中文标签时追加 FontProperties 设置（macOS 使用 /System/Library/Fonts/PingFang.ttc）。

## 内置模板：arch-diagram（论文架构图）

**角色**：NeurIPS/CVPR/ICML 顶会科学插画师，熟悉 DeepMind/OpenAI 扁平矢量风格。

### 固定增强规则（自动追加到用户描述末尾）

professional academic diagram for top-tier AI conference paper, flat vector illustration, clean layout, white background, professional pastel tones, legible text labels for all key modules, organized flow (Left-to-Right or Top-to-Bottom), no photorealistic photos, no messy sketches, no unreadable text, no 3D shading artifacts, high resolution, print-friendly, minimal decorative elements, focused on content

### 风格映射（根据 target_venue 动态注入）

- NeurIPS/ICML：add "minimalist flat design, thin line borders, pastel color blocks"
- CVPR/ICCV：add "modular block diagram, clear directional arrows, distinct color coding per component"
- Nature/Science：add "detailed annotations, traditional scientific illustration, larger font labels"
- 学位论文：add "traditional engineering block diagram style, may include Chinese text labels"
- 其他/默认：add "clean academic style, balanced layout"

### 领域词汇注入（根据 paper_domain 动态加入 prompt）

- CV：mention "Encoder, Decoder, Feature Map, Convolution Layer, Attention Map, Skip Connection"
- NLP：mention "Transformer Block, Self-Attention, Feed-Forward Layer, Token Embedding, Positional Encoding"
- 图学习：mention "Graph Encoder, Node Aggregation, Edge Features, GNN Layer, Graph Readout"
- 通用：mention "Input, Output, Loss Function, Optimizer, Module, Pipeline"

## 迭代规则

- **Path A（代码生成）**：每轮基于**上轮代码 + 用户反馈**修改，保留已确认的改进
- **Path B（API 生成）**：每轮基于**用户原始描述 + 本轮反馈**重新生成 prompt，不在上轮 prompt 上累积
- 总迭代上限由 `--max-rounds` 控制（默认 8）
- 每轮记录：当前方案、反馈/评估结果、改进方向

## 图片保存

- `--output` 指定时：保存到指定路径
- 未指定时（对话模式）：询问用户；用户无明确要求则默认 `$PWD/figures/`
- 未指定时（Ralph 模式）：默认 `$PWD/figures/`
- 文件名由 Claude 根据内容自动命名，如 `gnn-fraud-arch.png`、`f1-score-comparison.png`
- 文件冲突时追加序号（如 `gnn-arch-2.png`）

## 使用示例

对话模式（默认，brainstorming 风格澄清需求）：
  /paper-image-gen 画一个基于图神经网络的欺诈检测系统架构图
  /paper-image-gen 我有一组在三个数据集上的 F1-score 对比数据需要可视化
  /paper-image-gen 画一个注意力机制的流程示意图 --max-rounds 5
  /paper-image-gen 画一个模型训练流程图 --output figures/training.png

Ralph 模式（全自动）：
  /paper-image-gen --ralph 画一个 GNN 欺诈检测架构图
  /paper-image-gen --ralph --max-rounds 3 画一个数据流转示意图

强制指定路径：
  /paper-image-gen --path a 我有 F1-score 对比数据，画柱状图
  /paper-image-gen --path b --output figures/arch.png 画系统架构图
