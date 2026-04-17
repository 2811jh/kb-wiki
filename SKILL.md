---
name: kb-wiki
description: Use when 用户需要建立、导入、查询或维护基于 llm-wiki 理念的持久化研究知识库时，包括 UX 研究、用户访谈、竞品分析等场景
---

# kb-wiki Skill

## 概述

**kb-wiki** 是一个 LLM 驱动的持久化知识库管理 skill。核心理念：**LLM 渐进式构建和维护 Wiki（Markdown 文件集合），知识随每次导入复利增长，用户永远不需要自己编写 Wiki 内容。**

类比：Obsidian = IDE，LLM = 程序员，Wiki = 代码库。用户打开 Obsidian 实时浏览，LLM 在后台持续编辑维护。

---

## 三层架构

```
your-wiki/
├── Schema.md          ← Schema 层（LLM 的工作规范，用户可自定义演进）
├── raw/               ← 原始资料层（只读，LLM 读取来源，绝不修改）
│   ├── articles/
│   ├── papers/
│   ├── assets/
│   └── data/
└── wiki/              ← Wiki 层（LLM 完全掌控，自动生成和维护）
    ├── entities/      ← 实体页面（用户、产品、组织）
    ├── concepts/      ← 概念页面（痛点、行为模式、设计模式）
    ├── sources/       ← 资料摘要页面（每份原始资料对应一个）
    ├── synthesis/     ← 综合分析页面（对比分析、概览、洞察归档、跨资料结论）
    ├── .cache/        ← 文件转换缓存（Excel/Word/PPT/PDF → Markdown，自动管理）
    ├── index.md       ← 内容目录（每次 ingest 自动更新）
    └── log.md         ← 操作日志（append-only，知识库演进的时间线）
```

**三层职责**：
- **raw/**：原始输入，不可变，是知识的来源
- **wiki/**：知识的提炼产物，LLM 负责构建和维护所有交叉引用、矛盾标注、综合结论
- **Schema.md**：规范层，让 LLM 成为训练有素的 Wiki 维护者而非通用聊天机器人，随使用逐步演进

**sources/ vs synthesis/ 的区别**：
- **sources/**：对**单一**原始资料的忠实摘要。一份资料对应一个 sources/ 页面。内容紧贴原文，是"这份资料说了什么"。
- **synthesis/**：跨**多个**来源的原创分析。是 LLM（或用户引导下的 LLM）综合多份资料后提炼出的洞察、对比、结论。内容是"综合来看意味着什么"。

> 类比：sources/ 是原材料，synthesis/ 是成品。sources/ 是笔记，synthesis/ 是论文。

---

## 意图识别 & 命令路由

用户**不需要**输入 `/` 命令。LLM 应根据用户的自然语言自动识别意图，执行对应工作流。同时也支持显式 `/` 命令作为精确控制方式。

| 用户可能说的话（自然语言） | 等价命令 | 执行内容 | 参考文档 |
|--------------------------|---------|---------|---------|
| "帮我初始化知识库"、"创建一个新的知识库" | `/setup` | 首次初始化：创建目录、生成 Schema.md、配置 qmd | [setup.md](skills/setup.md) |
| "帮我处理这篇文章"、"导入这个文件"、"我放了一篇新论文在 raw/ 里" | `/ingest` | 导入资料，自动更新 10-15 个 wiki 页面 | [ingest.md](skills/ingest.md) |
| "用户支付的痛点是什么？"、"总结一下竞品分析"、任何针对知识库的提问 | `/query` | 搜索知识库，综合答案，可选归档到 synthesis/ | [query.md](skills/query.md) |
| "检查一下知识库"、"有没有矛盾的内容"、"知识库健康状况" | `/lint` | 健康检查：矛盾、孤立页面、过时论断、缺失引用 | [lint.md](skills/lint.md) |
| "知识库有多少页面了"、"看看索引状态" | `/status` | 显示 wiki 统计 + qmd 索引状态 | — |

> **路由优先级**：如果用户输入了显式 `/` 命令（如 `/ingest raw/articles/xxx.md`），直接执行对应工作流，无需确认。如果是自然语言，LLM 应先识别意图，必要时向用户确认后再执行。

---

## 首次使用流程

运行 `/setup` 后，LLM 将自动引导完成知识库初始化（详见 [setup.md](skills/setup.md)）：

1. **环境检测**：检测 Node.js (≥22)、Python (≥3.10，用于文件格式转换)
2. **编译 qmd 搜索引擎**：从内嵌源码自动编译，配置 HuggingFace 镜像（中国大陆）
3. **创建知识库**：收集名称和路径 → 创建目录结构 → 生成 Schema.md / index.md / log.md
4. **配置搜索索引**：注册 qmd 集合 → 预下载 AI 模型（向量搜索 + LLM 重排序，约 1.3GB）
5. **完成**：输出欢迎信息和使用指南

> 💡 Python 为可选依赖（仅 Office/PDF 转换需要）。**AI 模型下载为强制步骤**，未完成模型下载的知识库视为未创建完成——`/query` 的向量语义搜索和 LLM 重排序都依赖此模型。

### 支持的文件格式

| 格式 | 扩展名 | 处理方式 |
|------|--------|---------|
| Markdown / 文本 | `.md`, `.txt`, `.csv` | LLM 直接读取 |
| Excel | `.xlsx`, `.xls` | 自动转换为 Markdown（需 Python） |
| Word | `.docx` | 自动转换为 Markdown（需 Python） |
| PowerPoint | `.pptx` | 自动转换为 Markdown（需 Python） |
| PDF | `.pdf` | 自动转换为 Markdown（需 Python） |
| 图片 | `.png`, `.jpg`, `.gif`, `.webp` | LLM 视觉能力直接查看 |

---

## Lint 提醒规则

**每完成 5 次 `/ingest` 操作后，自动在回复末尾追加提醒：**

```
---
💡 **知识库健康提醒**：你已经导入了 5 份新资料，
建议运行 `/lint` 检查知识库健康状态（矛盾、孤立页面、缺失引用等）。
这将帮助你保持知识库的一致性和质量。
---
```

**计数方法**：读取 `wiki/log.md`，统计距上一次 lint 操作之后的 ingest 记录数量。

```bash
# 示例：统计距上次 lint 的 ingest 次数
grep "^## \[" wiki/log.md | tail -20 | grep "ingest" | wc -l
```

---

## 重要原则

> **文件命名**：wiki 页面采用 `{类型前缀}-{描述}.md` 纯中文格式（如 `痛点-加载速度.md`、`问卷-春节满意度.md`、`用户-流失玩家.md`），类型前缀确保分类清晰，便于 Obsidian 图谱识别。

### LLM 的职责

1. **LLM 负责写，用户负责读**：用户永远不需要手动编写任何 Wiki 内容。用户负责寻找资料来源、进行探索性提问，以及引导分析方向。
2. **raw/ 目录只读**：绝不修改 `raw/` 中的任何文件，它们是原始来源的真相
3. **wiki/ 目录 LLM 完全掌控**：可以自由创建、修改、合并 wiki 页面
4. **log.md 只追加**：日志记录只能追加，不能删改历史
5. **交叉引用是价值所在**：每次 ingest 都要检查并强化已有页面之间的关联
6. **标注矛盾，不隐藏矛盾**：发现矛盾时，明确标注，不要静默覆盖

### 知识质量原则

7. **综合结论要反映所有来源**：`synthesis/` 页面应综合所有相关资料，不偏向单一来源
8. **探索即积累，查询也是复利**：好的 query 分析结论应归档到 `synthesis/`，让每次探索都像导入新资料一样在知识库中持续积累。对比分析、发现的关联、综合洞察——这些不应消失在聊天记录中，而是成为知识库永久的一部分。
9. **index.md 是导航补充**：ingest 后必须更新 index.md；查询时以 qmd 搜索为主，index.md 仅用于补全搜索盲区
10. **Lint 是知识库的定期体检**：不要等到问题积累太多才做健康检查

### Schema 演进原则

11. **Schema.md 是可演进的**：用户可以根据自己的领域、偏好修改 Schema.md，告诉 LLM 不同的工作方式。这是 kb-wiki 适应不同使用场景的关键机制。

---

## 子文档索引

| 文档 | 内容 |
|------|------|
| [setup.md](skills/setup.md) | 完整安装引导流程 |
| [ingest.md](skills/ingest.md) | 导入资料详细工作流（10 步） |
| [query.md](skills/query.md) | 查询知识库详细工作流 |
| [lint.md](skills/lint.md) | 健康检查详细流程（7 项检查） |
| [qmd-reference.md](skills/qmd-reference.md) | qmd 工具完整命令参考 |
| [obsidian-tips.md](skills/obsidian-tips.md) | Obsidian 集成指南（Web Clipper、图谱视图、Dataview、Marp、Git） |

---

## 关于 llm-wiki 理念

本 skill 完整实现了 llm-wiki 的 11 条核心理念：

1. LLM 渐进式构建和维护持久化 Wiki，添加新资料时更新实体页面、修订主题摘要、标注矛盾、强化综合结论
2. Wiki 是持久的不断复利增长的知识产物，交叉引用已建立，矛盾已标记，综合结论反映所有阅读内容
3. 用户永远不需要自己编写 Wiki 内容，LLM 负责一切编写和维护
4. 用户能一边打开 LLM 智能体，一边打开 Obsidian，LLM 编辑，用户实时浏览
5. 三层架构：Raw sources + Wiki 层 + Schema 层（Schema.md）
6. 三种操作：Ingest、Query、Lint
7. 两个特殊文件：index.md（内容目录）+ log.md（append-only 操作日志）
8. 核心搜索工具：qmd（本地搜索引擎，BM25 + 向量 + LLM 重排序，CLI + MCP 双模式）
9. 技巧：Obsidian Web Clipper、本地图片、图谱视图、Marp、Dataview、git
10. 为什么有效：繁重的维护工作由 LLM 完成，人类负责策划来源和引导分析
11. 目录结构、Schema 约定等取决于用户领域，通过 Schema.md 自定义演进
