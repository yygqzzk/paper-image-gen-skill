# Paper Image Gen Skill

为学术论文生成高质量配图的 Claude Code / Codex Skill，支持实验数据可视化和架构示意图两种场景。

## ✨ 特性

- 🎨 **双路径生成**：支持 Python 代码生成（实验绘图）和 API 生成（架构图）
- 🤖 **智能模式切换**：对话模式（交互式澄清需求）和 Ralph 自动模式（全自动迭代）
- 📊 **学术标准**：符合顶级会议/期刊（NeurIPS、CVPR、Nature 等）的图表规范
- 🔄 **迭代优化**：自动评估生成质量，支持多轮迭代改进
- 🌐 **平台兼容**：同时支持 Claude Code 和 Codex

## 📦 安装

### 1. 复制 Skill 文件

```bash
# 克隆仓库
git clone https://github.com/yygqzzk/paper-image-gen-skill.git

# 复制到 Claude Code skills 目录
cp -r paper-image-gen-skill ~/.claude/skills/paper-image-gen

# 复制脚本文件（Path B 需要）
cp paper-image-gen-skill/scripts/image-gen.py ~/.claude/scripts/
chmod +x ~/.claude/scripts/image-gen.py

# 或复制到 Codex skills 目录
cp -r paper-image-gen-skill ~/.codex/skills/paper-image-gen
cp paper-image-gen-skill/scripts/image-gen.py ~/.codex/scripts/
chmod +x ~/.codex/scripts/image-gen.py
```

### 2. 配置 API（仅 Path B 需要）

首次使用 API 生成架构图时，会自动引导配置：

```bash
# 配置文件位置
~/.claude/image-gen.json
```

配置内容：
```json
{
  "api_url": "your-gemini-image-api-url",
  "api_key": "your-api-key",
  "default_max_rounds": 8,
  "paper_domain": "CV",
  "target_venue": "NeurIPS"
}
```

也可以使用环境变量（优先级更高）：
```bash
export IMAGE_GEN_URL="your-api-url"
export IMAGE_GEN_API_KEY="your-api-key"
```

### 3. 安装 Python 依赖（Path A 需要）

```bash
pip install matplotlib numpy seaborn pandas
```

## 🚀 使用方法

### 对话模式（默认）

交互式澄清需求，适合复杂场景：

```bash
/paper-image-gen 画一个基于图神经网络的欺诈检测系统架构图
/paper-image-gen 我有一组在三个数据集上的 F1-score 对比数据需要可视化
/paper-image-gen 画一个注意力机制的流程示意图 --max-rounds 5
```

### Ralph 自动模式

全自动迭代优化，适合快速生成：

```bash
/paper-image-gen --ralph 画一个 GNN 欺诈检测架构图
/paper-image-gen --ralph --max-rounds 3 画一个数据流转示意图
```

### 强制指定生成路径

```bash
# 强制使用 Python 代码生成
/paper-image-gen --path a 我有 F1-score 对比数据，画柱状图

# 强制使用 API 生成
/paper-image-gen --path b --output figures/arch.png 画系统架构图
```

## 📊 支持的图表类型

### Path A：实验绘图（Python 代码）

适合有数据的实验结果可视化：

- **数值对比**：柱状图、雷达图、帕累托前沿图、堆叠柱状图
- **趋势收敛**：带置信阴影折线图、局部放大折线图
- **模型评估**：ROC 曲线、PR 曲线
- **矩阵可视化**：热力图、散点图、气泡图
- **统计分布**：小提琴图、箱线图
- **复合布局**：双 Y 轴图、分面网格图

### Path B：架构图（API 生成）

适合论文架构、流程图、系统设计：

- 模型架构图（Transformer、GNN、CNN 等）
- 系统流程图
- 数据流转示意图
- 算法流程图

## 🎯 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--ralph` | 启用 Ralph 自动模式（全自动迭代） | 对话模式 |
| `--max-rounds N` | 最大迭代轮数 | 8 |
| `--output PATH` | 指定输出路径 | `$PWD/figures/` |
| `--path [a\|b]` | 强制指定生成路径（a=Python, b=API） | 自动推荐 |

## 📐 学术标准

### 支持的会议/期刊

- **AI 顶会**：NeurIPS、ICML、CVPR、ICCV
- **顶级期刊**：Nature、Science
- **学位论文**：硕士/博士论文
- **通用标准**：适用于其他学术场景

### 图表规范

- **分辨率**：300 DPI（印刷标准）
- **图幅尺寸**：
  - 双栏（默认）：6.75 × 4.0 英寸
  - 单栏：3.25 × 2.5 英寸
- **配色**：色盲友好配色方案
- **字体**：符合各会议/期刊要求

## 🔄 工作流程

### 对话模式流程

1. **需求澄清**：通过选择题形式明确 4 个核心维度
   - 图片类型（实验绘图/架构图）
   - 论文领域（CV/NLP/图学习/其他）
   - 目标会议/期刊（可选）
   - 核心内容（具体元素、数据等）

2. **路径推荐**：根据图片类型推荐最佳生成路径

3. **生成与迭代**：
   - Path A：生成 Python 代码 → 执行 → 展示图片 → 用户反馈 → 迭代
   - Path B：生成 prompt → 调用 API → 展示图片 → 用户反馈 → 迭代

### Ralph 自动模式流程

1. **自动分析**：直接分析用户描述，跳过需求澄清
2. **自动生成**：选择路径并生成图片
3. **自动评估**：5 维度评估（匹配度、布局、可读性、学术性、准确性）
4. **自动迭代**：不满意则自动优化，满意或连续 2 轮无提升则交付

## 💡 使用示例

### 示例 1：实验结果对比图

```bash
/paper-image-gen 我有三个模型在 CORA、Citeseer、Pubmed 数据集上的 F1-score，分别是：
GCN: 0.81, 0.70, 0.79
GAT: 0.83, 0.72, 0.80
GraphSAGE: 0.82, 0.71, 0.78
请画一个对比柱状图
```

### 示例 2：训练曲线

```bash
/paper-image-gen --ralph 画一个模型训练的 loss 曲线，包含训练集和验证集，显示收敛过程
```

### 示例 3：模型架构图

```bash
/paper-image-gen 画一个基于 Transformer 的文本分类模型架构图，包含：
- 输入层（Token Embedding + Positional Encoding）
- 多层 Transformer Encoder
- 分类头（MLP + Softmax）
目标会议：NeurIPS
```

## 🛠️ 技术细节

### Path A：Python 代码生成

- **依赖库**：matplotlib、numpy（必需），seaborn、pandas（可选）
- **执行方式**：Claude 直接执行生成的代码
- **输出格式**：PNG，300 DPI
- **错误处理**：自动修复语法错误，依赖缺失时降级或提示安装

### Path B：API 生成

- **API 要求**：兼容 Gemini Image Generation API
- **Prompt 模板**：内置学术风格模板，自动注入领域词汇
- **错误处理**：网络错误重试，API 限流自动等待

## 📝 配置文件说明

配置文件 `~/.claude/image-gen.json` 支持以下字段：

```json
{
  "api_url": "API 地址（Path B 必需）",
  "api_key": "API 密钥（Path B 必需）",
  "default_max_rounds": 8,
  "paper_domain": "CV",
  "target_venue": "NeurIPS"
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Claude Code](https://claude.ai/code)
- [Codex](https://codex.ai)

---

**作者**：yygqzzk
**版本**：1.0.0
**更新日期**：2026-03-23
