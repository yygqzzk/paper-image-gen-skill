# Paper Image Gen Skill 配置指南

## 给 Codex 用户的配置 Prompt

请将以下内容复制给 Codex，让它自动配置 paper-image-gen skill：

---

**Prompt 开始**

请帮我配置 paper-image-gen skill 的配置文件。执行以下步骤：

1. 创建配置文件 `~/.codex/image-gen.json`（如果使用 Claude Code，则创建 `~/.claude/image-gen.json`）

2. 将以下内容写入配置文件：

```json
{
  "api_url": "http://zx2.52youxi.cc:3000/v1beta/models/gemini-3-pro-image-preview:generateContent",
  "api_key": "sk-lJlFnCmFkq4bokG8RPCwB2OeziyM4irqmbcApfGkC0ob51C8",
  "default_max_rounds": 8,
  "image_size": "1K",
  "paper_domain": "CV",
  "target_venue": "NeurIPS"
}
```

3. 设置文件权限为 600（仅所有者可读写）：
```bash
chmod 600 ~/.codex/image-gen.json
```

4. 验证配置文件已正确创建：
```bash
cat ~/.codex/image-gen.json
```

**Prompt 结束**

---

## 配置字段说明

| 字段 | 说明 | 是否必需 |
|------|------|---------|
| `api_url` | Gemini Image API 完整 URL | 必需（Path B） |
| `api_key` | API 密钥 | 必需（Path B） |
| `default_max_rounds` | 默认最大迭代轮数 | 可选，默认 8 |
| `image_size` | 图片尺寸（1K/2K/4K） | 可选，默认 1K |
| `paper_domain` | 论文领域（CV/NLP/图学习/其他） | 可选 |
| `target_venue` | 目标会议/期刊（NeurIPS/CVPR/Nature 等） | 可选 |

## 环境变量配置（可选）

如果不想使用配置文件，也可以通过环境变量配置（优先级更高）：

```bash
export IMAGE_GEN_URL="http://zx2.52youxi.cc:3000/v1beta/models/gemini-3-pro-image-preview:generateContent"
export IMAGE_GEN_API_KEY="sk-lJlFnCmFkq4bokG8RPCwB2OeziyM4irqmbcApfGkC0ob51C8"
```

## 注意事项

⚠️ **安全提醒**：
- 配置文件包含 API 密钥，请勿提交到版本控制系统
- 已在 `.gitignore` 中排除 `image-gen.json`
- 建议设置文件权限为 600

## 测试配置

配置完成后，可以运行以下命令测试：

```bash
/paper-image-gen --ralph --path b 画一个简单的测试图
```

如果配置正确，应该能成功生成图片。
