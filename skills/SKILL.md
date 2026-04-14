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
├── CLAUDE.md          ← Schema 层（LLM 的工作规范，用户可自定义演进）
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
    ├── index.md       ← 内容目录（每次 ingest 自动更新）
    └── log.md         ← 操作日志（append-only，知识库演进的时间线）
```

**三层职责**：
- **raw/**：原始输入，不可变，是知识的来源
- **wiki/**：知识的提炼产物，LLM 负责构建和维护所有交叉引用、矛盾标注、综合结论
- **CLAUDE.md**：规范层，让 LLM 成为训练有素的 Wiki 维护者而非通用聊天机器人，随使用逐步演进

---

## 意图识别 & 命令路由

用户**不需要**输入 `/` 命令。LLM 应根据用户的自然语言自动识别意图，执行对应工作流。同时也支持显式 `/` 命令作为精确控制方式。

| 用户可能说的话（自然语言） | 等价命令 | 执行内容 | 参考文档 |
|--------------------------|---------|---------|---------|
| "帮我初始化知识库"、"创建一个新的知识库" | `/setup` | 首次初始化：创建目录、生成 CLAUDE.md、配置 qmd | [setup.md](setup.md) |
| "帮我处理这篇文章"、"导入这个文件"、"我放了一篇新论文在 raw/ 里" | `/ingest` | 导入资料，自动更新 10-15 个 wiki 页面 | [ingest.md](ingest.md) |
| "用户支付的痛点是什么？"、"总结一下竞品分析"、任何针对知识库的提问 | `/query` | 搜索知识库，综合答案，可选归档到 synthesis/ | [query.md](query.md) |
| "检查一下知识库"、"有没有矛盾的内容"、"知识库健康状况" | `/lint` | 健康检查：矛盾、孤立页面、过时论断、缺失引用 | [lint.md](lint.md) |
| "知识库有多少页面了"、"看看索引状态" | `/status` | 显示 wiki 统计 + qmd 索引状态 | — |

> **路由优先级**：如果用户输入了显式 `/` 命令（如 `/ingest raw/articles/xxx.md`），直接执行对应工作流，无需确认。如果是自然语言，LLM 应先识别意图，必要时向用户确认后再执行。

---

## 首次使用流程

当用户首次运行 `/setup` 时，按以下步骤执行（详见 [setup.md](setup.md)）：

### 步骤 1：检测依赖

```bash
node --version   # 必须 >= 22
qmd --version    # 检查 qmd 是否已安装
```

如果 Node.js 版本不满足，告知用户升级。如果 qmd 未安装，执行：

```bash
npm install -g @tobilu/qmd
```

### 步骤 2：收集配置信息

询问用户：
1. **知识库名称**：建议使用英文小写，如 `ux-research`、`product-wiki`
2. **知识库位置**：
   - 默认：桌面（`~/Desktop/<知识库名称>`）
   - 可选：自定义完整路径

### 步骤 3：创建目录结构

```bash
mkdir -p <知识库路径>/raw/articles
mkdir -p <知识库路径>/raw/papers
mkdir -p <知识库路径>/raw/assets
mkdir -p <知识库路径>/raw/data
mkdir -p <知识库路径>/wiki/entities
mkdir -p <知识库路径>/wiki/concepts
mkdir -p <知识库路径>/wiki/sources
mkdir -p <知识库路径>/wiki/synthesis
```

### 步骤 4：生成初始文件

1. 将 `templates/CLAUDE.md.template` 中 `{{WIKI_NAME}}` 替换为实际名称，复制为 `<知识库路径>/CLAUDE.md`
2. 创建 `<知识库路径>/wiki/index.md`（空目录文件）
3. 创建 `<知识库路径>/wiki/log.md`（空日志文件）

**index.md 初始内容**：

```markdown
# {{WIKI_NAME}} 知识库索引

> 最后更新：{{当前日期}}
> 总页面数：0

## entities/（实体页面）

*暂无内容，等待第一次 ingest*

## concepts/（概念页面）

*暂无内容，等待第一次 ingest*

## sources/（资料摘要）

*暂无内容，等待第一次 ingest*

## synthesis/（综合分析）

*暂无内容，等待第一次 ingest*
```

**log.md 初始内容**：

```markdown
# 操作日志

> 格式：`## [YYYY-MM-DD] ingest/query/lint | 标题`
> 此文件只允许追加，不允许删改历史记录。

## [{{当前日期}}] setup | 知识库初始化完成
```

### 步骤 5：配置 qmd 集合

```bash
qmd collection add <知识库路径>/wiki --name <知识库名称>
qmd update
```

### 步骤 6：输出欢迎信息

告知用户：
- 知识库位置
- 如何开始：将资料放入 `raw/articles/`，然后运行 `/ingest`
- 如何查询：运行 `/query 你的问题`
- 建议用 Obsidian 打开知识库根目录，实时浏览 wiki

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

### LLM 的职责

1. **LLM 负责写，用户负责读**：用户永远不需要手动编写任何 Wiki 内容。用户负责寻找资料来源、进行探索性提问，以及引导分析方向。
2. **raw/ 目录只读**：绝不修改 `raw/` 中的任何文件，它们是原始来源的真相
3. **wiki/ 目录 LLM 完全掌控**：可以自由创建、修改、合并 wiki 页面
4. **log.md 只追加**：日志记录只能追加，不能删改历史
5. **交叉引用是价值所在**：每次 ingest 都要检查并强化已有页面之间的关联
6. **标注矛盾，不隐藏矛盾**：发现矛盾时，明确标注，不要静默覆盖

### 知识质量原则

7. **综合结论要反映所有来源**：`synthesis/` 页面应综合所有相关资料，不偏向单一来源
8. **好的 query 结果值得归档**：有价值的分析结论应保存到 `synthesis/`，避免重复工作
9. **index.md 是导航核心**：查询时先读 index.md 定位相关页面，ingest 后必须更新 index.md
10. **Lint 是知识库的定期体检**：不要等到问题积累太多才做健康检查

### Schema 演进原则

11. **CLAUDE.md 是可演进的**：用户可以根据自己的领域、偏好修改 CLAUDE.md，告诉 LLM 不同的工作方式。这是 kb-wiki 适应不同使用场景的关键机制。

---

## 子文档索引

| 文档 | 内容 |
|------|------|
| [setup.md](setup.md) | 完整安装引导流程 |
| [ingest.md](ingest.md) | 导入资料详细工作流（10 步） |
| [query.md](query.md) | 查询知识库详细工作流 |
| [lint.md](lint.md) | 健康检查详细流程（7 项检查） |
| [qmd-reference.md](qmd-reference.md) | qmd 工具完整命令参考 |

---

## 关于 llm-wiki 理念

本 skill 完整实现了 llm-wiki 的 11 条核心理念：

1. LLM 渐进式构建和维护持久化 Wiki，添加新资料时更新实体页面、修订主题摘要、标注矛盾、强化综合结论
2. Wiki 是持久的不断复利增长的知识产物，交叉引用已建立，矛盾已标记，综合结论反映所有阅读内容
3. 用户永远不需要自己编写 Wiki 内容，LLM 负责一切编写和维护
4. 用户能一边打开 LLM 智能体，一边打开 Obsidian，LLM 编辑，用户实时浏览
5. 三层架构：Raw sources + Wiki 层 + Schema 层（CLAUDE.md）
6. 三种操作：Ingest、Query、Lint
7. 两个特殊文件：index.md（内容目录）+ log.md（append-only 操作日志）
8. 可选 CLI 工具：qmd（本地搜索引擎，CLI + MCP 双模式）
9. 技巧：Obsidian Web Clipper、本地图片、图谱视图、Marp、Dataview、git
10. 为什么有效：繁重的维护工作由 LLM 完成，人类负责策划来源和引导分析
11. 目录结构、Schema 约定等取决于用户领域，通过 CLAUDE.md 自定义演进
