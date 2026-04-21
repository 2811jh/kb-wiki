# kb-wiki

[![npm version](https://img.shields.io/npm/v/kb-wiki.svg)](https://www.npmjs.com/package/kb-wiki)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![node](https://img.shields.io/badge/node-%3E%3D22-brightgreen.svg)](https://nodejs.org)
[![skills](https://img.shields.io/badge/skills-agentskills.io-purple.svg)](https://agentskills.io)

**LLM 自动维护的持久化研究知识库 skill —— 你只负责提供资料和提问，LLM 负责构建整个知识库。**

> 📂 **把资料丢进 `raw/`，用自然语言提问 → LLM 自动写 wiki、建索引、标矛盾、做综合**
> 🧠 **基于 [llm-wiki](https://www.gleech.org/llm-wiki) 理念**，三层架构（raw / wiki / Schema）让 LLM 成为训练有素的 Wiki 维护者
> 🔍 **本地 qmd 搜索引擎**：BM25 + 向量 + LLM 重排序三层混合搜索，模型完全本地运行，数据不离开本机
> ♻️ **复利增长**：每次 ingest 自动更新 10-15 个交叉引用页面，每次 query 可归档为 synthesis，探索即积累

---

## 核心特性速览

| 特性 | 一句话说明 |
|------|-----------|
| 🗣️ **自然语言触发** | 不需要记 `/` 命令，直接说"帮我导入这篇文章"、"用户痛点是什么？"即可 |
| 📎 **会话启动自动扫描** | 打开对话时 LLM 自动检测 `raw/` 中的新资料并主动提醒 |
| 📥 **10 步自动 ingest** | 一次导入自动更新 sources/entities/concepts/synthesis + 矛盾标注 + 重建索引 |
| 🔍 **三层智能搜索** | BM25 关键词 + 向量语义 + LLM 重排序，自动选最优策略 |
| ⚠️ **矛盾自动标注** | 发现新资料与已有结论冲突时主动标注 `⚠️ 矛盾`，绝不静默覆盖 |
| ♻️ **探索即归档** | Query 发现的洞察可一键归档到 synthesis/，下次直接命中 |
| 🩺 **7 项健康检查** | 矛盾、孤立页面、缺失引用、过时论断、数据空白…自动体检并打分 |
| 📚 **多格式自动转换** | Excel/Word/PPT/PDF 自动转 Markdown，图片走 LLM 视觉能力 |
| 🪄 **Schema 可演进** | 知识库规范由 LLM 与用户共同迭代，适应任意领域 |
| 🔌 **MCP server 模式** | 可作为 MCP 工具集成到 Claude Desktop / Cursor 等客户端 |

---

## 快速安装

**方式一**：通过 Skills CLI 安装（推荐）

```bash
npx skills add 2811jh/kb-wiki
```

**方式二**：手动安装（如果 Skills CLI 不可用）

```bash
git clone https://github.com/2811jh/kb-wiki.git ~/.agents/skills/kb-wiki
```

安装完成后，在对话中输入以下命令初始化知识库：

```
/setup
```

---

## 核心理念：llm-wiki 三层架构

kb-wiki 基于 [llm-wiki](https://github.com/2811jh/kb-wiki) 理念构建，将知识库分为三层：

```
your-wiki/
├── Schema.md          ← Schema 层：告诉 LLM 如何工作（可自定义演进）
├── raw/               ← 原始资料层：只读，LLM 从这里读取来源
│   ├── articles/      ← 文章、访谈记录
│   ├── papers/        ← 学术论文
│   ├── assets/        ← 图片等媒体文件
│   └── data/          ← 数据文件
└── wiki/              ← Wiki 层（LLM 完全掌控）
    ├── entities/
    ├── concepts/
    ├── sources/
    ├── synthesis/
    ├── .cache/        ← 文件转换缓存（自动管理）
    ├── index.md
    └── log.md
```

**类比**：Obsidian = IDE，LLM = 程序员，Wiki = 代码库。你打开 Obsidian 实时浏览，LLM 在后台编辑维护。

**三层职责对照**：

| 层 | 谁可以写 | 用途 | 是否可演进 |
|----|---------|------|-----------|
| **Schema.md** | 用户 + LLM 协作 | 告诉 LLM 如何工作（命名规范、页面模板、领域规则） | ✅ 可与你的领域共同演进 |
| **raw/** | 仅用户 | 原始资料的真相，不可变 | ❌ LLM 绝不修改 |
| **wiki/** | 仅 LLM | 知识的提炼产物（实体页、概念页、综合分析） | LLM 自动维护，无需手编 |

**sources/ vs synthesis/ 的区别**：

- **sources/**：对**单一**原始资料的忠实摘要，一份资料对应一个 sources/ 页面，是"这份资料说了什么"
- **synthesis/**：跨**多个**来源的原创分析，是 LLM 综合多份资料后提炼出的洞察、对比、结论，是"综合来看意味着什么"
- 类比：sources/ 是原材料，synthesis/ 是成品；sources/ 是笔记，synthesis/ 是论文

---

## 功能一览

| 命令 | 触发关键字（自然语言示例） | 功能 |
|------|---------------------------|------|
| `/setup` | "初始化知识库"、"创建一个新知识库" | 首次初始化：创建目录、生成 Schema.md、配置 qmd、下载 AI 模型 |
| `/ingest <文件\|内容>` | "帮我导入这篇文章"、"raw 里有新文件"、"批量处理 articles 里的剪藏" | 10 步导入：摘要 → 实体 → 概念 → 矛盾 → 综合 → 索引重建 |
| `/query <问题>` | 任意提问，如"用户支付痛点是什么？"、"竞品对比" | 3 阶段混合搜索 + 综合答案 + 可选归档到 synthesis/ |
| `/lint [--quick]` | "检查知识库"、"知识库健康度怎么样"、"有矛盾吗" | 7 项健康检查 + 健康得分 + 修复建议 + 探索方向推荐 |
| `/status` | "知识库有多少页面了"、"看看索引状态如何" | 显示 wiki 页面统计 + qmd BM25/向量索引就绪状态 |

> 💡 **不需要输入 `/`**：所有命令都支持自然语言触发，详见下方 [自然语言触发章节](#自然语言触发--智能意图识别)。

---

## 自然语言触发 & 智能意图识别

kb-wiki 支持**自然语言交互**，你**不需要记任何 `/` 命令**。LLM 会自动识别你的意图并路由到对应工作流。

### 意图识别示例

| 你说的话 | LLM 自动识别为 | 实际执行 |
|---------|---------------|---------|
| "帮我处理这篇文章"、"导入 raw/articles/xxx.md" | `/ingest` | 10 步导入工作流 |
| "我刚剪藏了几篇，处理一下吧"、"raw 里有新文件" | `/ingest`（批量） | 自动扫描未处理文件 + 批量导入 |
| "用户支付的痛点是什么？" | `/query` | 三阶段混合搜索 + 综合答案 |
| "总结一下竞品分析"、"对比基岩版和 Java 版" | `/query` | 跨多源综合分析 |
| "检查一下知识库"、"有没有矛盾" | `/lint` | 7 项健康检查 |
| "知识库有多少页面了"、"现在索引状态如何" | `/status` | 输出统计与索引信息 |

### 会话启动自动扫描

每次开始新对话时，LLM 会**首先**做一件事（仅一次）：

1. 读取 `wiki/log.md`，提取所有已 ingest 的来源文件路径
2. 扫描 `raw/` 目录下所有文件
3. 对比找出**未处理的新文件**

如果发现未处理文件，LLM 会**主动**提醒：

```
📎 发现 raw/ 中有 2 篇新资料尚未导入：
  1. raw/articles/Web Clipper 剪藏文章.md（昨天）
  2. raw/papers/Nielsen 可用性原则.pdf（3 天前）

要我批量导入吗？还是你想先选择部分导入？
```

> 💡 这个机制让"剪藏 → 导入"的工作流完全无感：你只管在浏览器中用 Web Clipper 一键保存，下次打开对话时 LLM 就会主动提醒你处理。

### 显式 `/` 命令（精确控制）

如果你希望**明确控制行为**，仍可使用 `/` 命令。例如批量导入时希望走严格的 10 步流程：

```
/ingest raw/articles/                     # 批量导入整个目录
/ingest raw/articles/竞品分析.docx        # 导入指定文件
/query 不同年龄段用户对快捷支付的态度差异   # 精确查询
/lint --quick                             # 仅运行前 3 项检查
```

**路由优先级**：显式 `/` 命令直接执行，无需确认；自然语言会先识别意图，必要时确认后再执行。

---

## 工作流示意图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        kb-wiki 工作流全景                            │
└─────────────────────────────────────────────────────────────────────┘

  首次使用                    日常使用（循环）
  ───────                    ──────────────

  ┌──────────┐         ┌──────────────────────────────────────────┐
  │  /setup   │         │                                          │
  │  初始化   │         │   ① 用户放入资料         ② 用户提问      │
  │  知识库   │         │      ↓                      ↓           │
  └────┬─────┘         │  ┌────────┐            ┌─────────┐      │
       │               │  │/ingest │            │ /query  │      │
       ▼               │  │导入资料│            │查询知识 │      │
  创建目录结构          │  └───┬────┘            └────┬────┘      │
  编译 qmd             │      │                      │           │
  生成 Schema.md       │      ▼                      ▼           │
  下载 AI 模型         │  ┌─────────────┐    ┌──────────────┐    │
       │               │  │ LLM 自动执行 │    │ qmd 混合搜索  │    │
       ▼               │  │             │    │ BM25 + 向量   │    │
  ✅ 知识库就绪         │  │ · 创建摘要页 │    │ + LLM 重排序  │    │
                       │  │ · 更新实体页 │    └──────┬───────┘    │
                       │  │ · 更新概念页 │           │           │
                       │  │ · 标注矛盾   │           ▼           │
                       │  │ · 强化交叉引用│    ┌──────────────┐    │
                       │  │ · 修订综合结论│    │ LLM 综合答案  │    │
                       │  │ · 更新索引   │    │（带引用+置信度）│    │
                       │  └───┬─────────┘    └──────┬───────┘    │
                       │      │                      │           │
                       │      ▼                      ▼           │
                       │   wiki/ 持续增长      可选归档到         │
                       │   知识复利 📈         synthesis/        │
                       │                                          │
                       └──────────────────────────────────────────┘
                                      │
                              每 5 次 ingest
                                      │
                                      ▼
                               ┌────────────┐
                               │   /lint     │
                               │  健康检查   │
                               │             │
                               │ · 矛盾检测  │
                               │ · 孤立页面  │
                               │ · 缺失引用  │
                               │ · 数据空白  │
                               └────────────┘
```

```
用户做的事（很少）              LLM 做的事（很多）
─────────────                 ────────────────
📁 把资料放进 raw/             📝 读取 → 理解 → 写 10-15 个 wiki 页面
❓ 问问题                      🔍 搜索 → 综合 → 生成带引用的答案
👀 在 Obsidian 中浏览          🔧 维护交叉引用、标注矛盾、修订结论
                              📊 定期健康检查 → 发现知识空白
```

---

## 首次使用：/setup 流程

`/setup` 是一个**全自动引导式**流程，LLM 会按下面 13 个步骤逐步完成知识库的初始化。

### 步骤详解

| # | 步骤 | 内容 | 是否需要用户输入 |
|---|------|------|----------------|
| 1 | 检测 Node.js | 要求 ≥ 22；缺失则给出 nvm/winget 安装命令 | 自动 |
| 2 | 检测 Python + 安装转换依赖 | 要求 ≥ 3.10；自动 `pip install -r requirements.txt`（可跳过） | 自动 / 可选跳过 |
| 3 | 编译 qmd 搜索引擎 | 从内嵌源码 `pnpm install + npx tsc` 自动编译，回退到 npm | 自动 |
| 4 | 配置 HuggingFace 镜像 | 国内用户自动设置 `HF_ENDPOINT=https://hf-mirror.com` | 询问一次 |
| 5 | 输入知识库名称 | 例如 `ux-research` / `product-wiki` / `interview-notes` | ✅ |
| 6 | 选择知识库位置 | 默认 `~/Desktop/{name}`，或自定义路径 | ✅ |
| 7 | 创建目录结构 | 一次性创建 raw/{articles,papers,assets,data} + wiki/{entities,concepts,sources,synthesis,.cache} | 自动 |
| 8 | 生成 Schema.md | 写入完整知识库规范模板（13 节 + 4 种页面格式） | 自动 |
| 9 | 创建 index.md | 创建初始内容目录 | 自动 |
| 10 | 创建 log.md | 创建 append-only 操作日志 | 自动 |
| 11 | 配置 qmd 集合 | `qmd collection add` 注册当前知识库 | 自动 |
| 12 | 预下载 AI 模型 | 运行 `qmd embed` 触发模型自动下载（**强制步骤**） | 自动 |
| 13 | 输出欢迎信息 | 显示位置、目录结构、上手提示 | 自动 |

> ⚠️ **步骤 12 是强制步骤**：未完成模型下载的知识库视为**未创建完成**。原因：`/query` 的向量语义搜索和 LLM 重排序都依赖此模型；跳过后只能使用 BM25 关键词搜索，搜索质量严重下降。

### AI 搜索模型分层

模型保存在 `~/.cache/qmd/models/`，按"按需下载"原则分三个层级：

| 层级 | 功能 | 命令 | 所需模型 | 累计大小 |
|------|------|------|---------|---------|
| 层级 1 | BM25 关键词搜索 | `qmd search` | 无需模型 ✅ | 0 |
| 层级 2 | 向量语义搜索 | `qmd vsearch` | embeddinggemma-300M + qmd-query-expansion-1.7B | ~1.3GB |
| 层级 3 | 完整混合搜索 + 重排序 | `qmd query --rerank` | + Qwen3-Reranker-0.6B | ~2GB |

> 💡 中国大陆用户：`/setup` 会询问是否在国内使用，自动设置 `HF_ENDPOINT=https://hf-mirror.com` 镜像加速。

📖 **完整流程详见**：[skills/setup.md](skills/setup.md)

---

## /ingest：导入资料的 10 步工作流

每次导入新资料，LLM 自动执行 10 步流程，**单次操作影响 10-15 个 wiki 页面**：

```
1. 检测格式 + 读取原始资料 ──┐
2. 与用户讨论关键要点（可选）│
2.5 读取 Schema.md 命名规范 │  ← 防止命名漂移
3. 在 sources/ 写摘要页面    │
4. 更新 index.md             ├─→  影响 10-15 个 wiki 页面
5. 更新 entities/ 实体页     │
6. 更新 concepts/ 概念页     │
7. 检查并标注 ⚠️ 矛盾        │
8. 强化或修订 synthesis/     │
9. 在 log.md 追加记录       ─┘
10. 重建 qmd 索引 + 更新向量嵌入
```

### 三种触发方式

```bash
# 1. 单文件导入
/ingest raw/articles/user-interview-2024-03.md
/ingest raw/data/Q1-survey.xlsx
/ingest raw/papers/nielsen-heuristics.pdf

# 2. 批量导入（目录或 glob）
/ingest raw/articles/                # 整个目录
/ingest raw/articles/*.md            # 所有 Markdown
/ingest raw/papers/2024-*.pdf        # 按通配符

# 3. 直接粘贴文本
/ingest
（然后粘贴文章内容）
```

### 自动检测剪藏文章

如果文件 frontmatter 包含 `clipped: true` 或 `source_url`，自动识别为 Web Clipper 剪藏：
- 在 sources/ 摘要页中记录原始 URL
- 在 tags 中加入 `网络文章` 标签
- 检测远程图片，提醒用户用 `Ctrl+Shift+D` 本地化（避免链接失效）

### 完成后的汇报

```
✅ 导入完成：《用户访谈 - 2024-03》

📝 更新了 6 个 wiki 页面：

新建页面：
  - wiki/sources/访谈-2024年3月用户访谈.md
  - wiki/entities/用户-A.md

更新页面：
  - wiki/entities/用户-B.md（新增 2024-03 访谈内容）
  - wiki/concepts/痛点-支付流程.md（新增来源，更新综合结论）
  - wiki/concepts/痛点-加载速度.md（新增 2 条引述）
  - wiki/index.md（已更新）
  - wiki/log.md（已追加记录）

🔍 发现：
  - ⚠️ 矛盾标注：1 处（快捷支付安全性态度差异）
  - 💡 修订综合结论：1 处（支付优化双维度论断）

📊 知识库状态：sources: 3 | entities: 5 | concepts: 7 | synthesis: 0
```

📖 **完整流程详见**：[skills/ingest.md](skills/ingest.md)

---

## /query：查询知识库的 3 阶段智能搜索

`/query` 不是简单的关键词匹配，而是**强制 qmd 搜索 → 综合多源 → 标注矛盾 → 询问归档**的完整流程。

### 强约束规则

> ❌ **禁止**：凭借对 index.md 或之前对话的已知内容，直接选择文件读取
> ✅ **必须**：将用户查询交给 qmd，由搜索引擎客观排序后，再决定读哪些文件
>
> 即使你只有 5 个 wiki 页面，**也必须先用 qmd 搜索**，因为它能发现关键词不匹配但语义相关的页面。

### 7 步流程

```
1. 检查 qmd 索引状态 → 必要时自动 embed（不允许降级）
2. 用 qmd query "问题" 执行混合搜索
3. 读取 index.md（可选，用于补全盲区）
4. 通过 qmd get / multi-get 读取候选页面
5. 生成综合答案（带引用 + 置信度 + 矛盾标注）
6. 自评归档价值 + 询问用户是否归档
7. 如归档：写 synthesis/ + 反向链接 + 重建索引 + 记录 log.md
```

### 6 种答案形式（按需选择）

| 形式 | 适用场景 |
|------|---------|
| 📄 **Markdown 摘要页面**（默认） | 深度分析、需要归档的场景 |
| 📊 **对比表格** | 多个对象的横向比较（如竞品对比） |
| 🎤 **Marp 幻灯片** | 内部分享、汇报材料 |
| ✅ **行动项清单** | 转化研究洞察为待办事项 |
| 📈 **数据可视化（matplotlib）** | 涉及定量数据或趋势对比 |
| 🗺️ **Obsidian Canvas** | 关系网络、用户旅程、概念地图 |

### 答案示例（带引用 + 置信度 + 矛盾）

```markdown
## 支付流程用户痛点分析

基于 3 份资料（2 次用户访谈 + 1 份竞品分析），痛点集中在两个维度：

### 1. 步骤数量过多（置信度：高，2/2 访谈提及）
- 用户 A 表示需要 3 步确认（[[sources/访谈-2024年3月]]）
- 用户 C 同样提到"流程繁琐"（[[sources/访谈-2024年1月]]）

### 2. 加载速度慢（置信度：高，2/2 访谈独立提及）
- "有时候点了没反应" — 用户 A（[[sources/访谈-2024年3月]]）

> ⚠️ **矛盾**：[[sources/竞品-2024年2月]] 显示竞品快捷支付因安全顾虑接受度低，
> 但我们的用户对此未表达明显担忧。安全性认知差异的原因尚待研究。
```

### 复利效应：探索即归档

每次有价值的 query → 一键归档到 `wiki/synthesis/`，下次再问相似问题：
- ✅ qmd 直接命中 synthesis 页面，无需重做分析
- ✅ 归档时自动添加反向链接（concepts/ ↔ synthesis/）
- ✅ 自动记入 log.md，可被 `/lint` 跟踪
- ✅ 自动重建 qmd 索引（包括向量嵌入）

> 💡 **核心洞察**：用户的探索性提问会像导入新资料一样在知识库中**复利积累**。对比分析、发现的关联、综合洞察——这些不再消失在聊天记录中。

📖 **完整流程详见**：[skills/query.md](skills/query.md)

---

## /lint：知识库的 7 项健康检查

`/lint` 是知识库的**定期体检**，每完成 5 次 ingest 后 LLM 会自动提醒运行。

### 7 项检查项

| # | 检查项 | 检测目标 |
|---|-------|---------|
| 1 | 🔴 **矛盾论断检测** | 不同页面间相互冲突的论断（按 🔴 高 / 🟡 中 / 🟢 低 三级分类） |
| 2 | 🔄 **过时论断检测** | 被新资料取代但未更新的旧结论 |
| 3 | 📄 **孤立页面检测** | 没有任何入站链接（被引用）的页面 |
| 4 | 🔗 **缺失页面检测** | 在其他页面被 `[[引用]]` 但实际不存在的页面 |
| 5 | 🔗 **缺失交叉引用检测** | 语义高度相关但没有互相链接的页面对 |
| 6 | ❓ **数据空白检测** | 缺失的重要信息 + 单一来源风险 + 推荐补充方向 |
| 7 | 📋 **log.md 完整性检查** | 日志格式正确、记录完整、与 index.md 统计一致 |

### 健康得分

每次 lint 自动计算：

```
健康得分 = 100 - (矛盾数 × 5) - (孤立页面数 × 3) - (缺失引用数 × 2)
                - (过时内容数 × 4) - (数据空白数 × 3)
```

| 得分 | 状态 | 建议 |
|------|------|------|
| ≥ 80 | ✅ 健康 | 保持当前节奏 |
| 60-79 | ⚠️ 需关注 | 集中解决矛盾和数据空白 |
| < 60 | 🔴 暂停 ingest | 优先执行 lint 修复 |

### 矛盾解决工作流

对每个未解决的矛盾，LLM 会引导识别**分歧维度**：

- [ ] 样本差异（不同用户群、不同地区）
- [ ] 时间差异（数据采集时间不同）
- [ ] 方法差异（定性 vs 定量、自述 vs 行为）
- [ ] 定义差异（双方对同一概念的理解不同）
- [ ] 真实矛盾（同一条件下的不同结论）

并提出定向验证建议和跟进 query。

### Lint 报告示例

```
# Lint 报告
**执行时间**：2024-04-20  **总页面数**：45（sources:12 / entities:18 / concepts:10 / synthesis:5）

## 总览
| 检查项 | 状态 | 问题数 |
|--------|------|--------|
| 矛盾论断 | ⚠️ 需关注 | 2 |
| 孤立页面 | ⚠️ 需关注 | 3 |
| 缺失引用 | 🔴 需修复 | 1 |
| ... | ... | ... |

**综合健康评分**：82/100（良好）

## 修复建议（按优先级）
🔴 立即处理：1 项
🟡 本周处理：2 项
🟢 下次 ingest 顺手处理：1 项

## 推荐的下一步探索
- 需要寻找的资料：Android 用户测试报告 / 40岁以上用户访谈
- 建议跟进的 query：/query 用户对安全性和便捷性的权衡如何？
```

📖 **完整流程详见**：[skills/lint.md](skills/lint.md)

---

## /status：查看知识库与索引状态

快速查看知识库的整体状态，用于了解规模和搜索就绪情况：

```
📊 知识库：ux-research
📂 路径：~/Desktop/ux-research

📚 wiki 页面统计：45
  - sources/    : 12 份资料摘要
  - entities/   : 18 个实体
  - concepts/   : 10 个概念
  - synthesis/  :  5 份综合分析

🔍 qmd 索引状态：
  - BM25:    ✅ 已建立（最近更新：今天 14:30）
  - Vectors: ✅ 已嵌入（45 / 45 个文件）
  - Pending: 0 need embedding

📝 最近操作（log.md）：
  - 2024-04-20  ingest  竞品分析-2024年4月
  - 2024-04-18  query   归档：洞察-付费障碍三种类型
  - 2024-04-15  lint    健康得分 82/100
```

> 💡 当 `Vectors: 0 embedded` 或 `Pending` 不为 0 时，需要运行 `qmd embed` 补齐向量索引，否则 `/query` 会缺失语义搜索能力。

---

## 页面架构与命名规范

### 4 种页面类型

`wiki/` 下的所有页面归为 4 种类型，每种有不同的职责和格式：

| 类型 | 目录 | 职责 | 起步前缀 | 示例文件名 |
|------|------|------|---------|-----------|
| 📥 **资料摘要** | `sources/` | 一份原始资料对应一个摘要页（单源） | `问卷-` `访谈-` `竞品-` `报告-` … | `访谈-2024年3月用户访谈.md` |
| 👤 **实体页** | `entities/` | 用户、产品、组织、竞品等具体对象 | `用户-` `产品-` `组织-` `服务器-` … | `用户-回流玩家群体.md` |
| 💡 **概念页** | `concepts/` | 痛点、行为模式、需求、设计概念等抽象主题 | `痛点-` `行为-` `需求-` `模式-` … | `痛点-加载速度.md` |
| 🧠 **综合分析** | `synthesis/` | 跨多源原创洞察、对比、综合结论（多源） | `对比-` `洞察-` `概览-` `路线-` … | `对比-基岩与Java版.md` |

### `{类型前缀}-{描述}.md` 命名机制

文件名采用**纯中文** + **类型前缀**形式，让 Obsidian 图谱自动按主题聚类：

```
✅ 推荐：痛点-支付流程.md
        访谈-2024年3月.md
        对比-竞品支付方式.md

❌ 避免：payment-pain.md           （无类型前缀，难分类）
        我对支付流程的研究.md       （描述过长，缺少前缀）
```

### 活约定（前缀自演进）

LLM 创建页面时按以下流程命名：

```
1. 扫描同目录已有文件名 → 提取已用前缀列表
2. 判断新页面是否匹配已有前缀 → 是 → 复用（保持一致性）
3. 不匹配 → LLM 自主创建新前缀（2-3 字，概括内容本质）
4. 新前缀连续使用 3 次以上 → 建议正式记入 Schema.md
```

> 💡 **前缀是活约定，不是死目录**：导入会议纪要可创建 `会议-` 前缀；导入视频笔记可创建 `视频-` 前缀。LLM 拥有自主命名权，但优先复用已有前缀以保持一致性。

### YAML Frontmatter 字段

所有 wiki 页面都需要包含 frontmatter，提供元数据供 Obsidian / Dataview / qmd 使用：

```yaml
---
title: 痛点-加载速度          # 页面标题（与 H1 一致）
slug: loading-speed-pain      # 英文标识符，便于程序化引用（不影响文件名）
type: concept                 # 页面类型：source / entity / concept / synthesis
date: 2024-04-15              # 创建日期
updated: 2024-04-20           # 最后更新日期
tags: [痛点, 性能, 移动端]     # 分类标签（Dataview 查询用）
sources: [sources/访谈-2024年3月用户访谈]
related: [entities/用户-A, concepts/痛点-支付流程]
aliases: [加载慢, 卡顿]        # 可选：别名（提升搜索命中）
severity: high                # 可选：仅痛点类页面，标识严重程度
frequency: high               # 可选：仅痛点类页面，标识出现频率
---
```

> ⚠️ **YAML 安全规则**：值中含 `[ ] : # { } , & * ? | < > = !` 等特殊字符时，**必须用双引号包裹**，否则 Obsidian 解析失败、frontmatter 显示为红色原始文本。
> ```yaml
> # ❌ 失败：嵌套方括号导致 YAML 解析错误
> sources: [raw/articles/[UX][G79]报告.pdf]
> # ✅ 正确：用引号包裹
> sources: ["raw/articles/[UX][G79]报告.pdf"]
> ```

### 交叉引用格式

```markdown
[[页面名]]                              ← 同目录引用（推荐，Obsidian 兼容）
[[entities/用户-A]]                     ← 跨目录引用
[用户 A 完整画像](../entities/用户-A.md) ← 标准 Markdown（备选）
```

### index.md 的特殊规则

> ⚠️ **index.md 禁止使用 `[[wiki-link]]`**，必须使用纯文本列表
> 原因：index.md 链接到所有页面，会在 Obsidian 图谱中形成巨大的星形中心，掩盖页面之间真正有意义的关联

```markdown
## sources/（资料摘要）
- 访谈-2024年3月用户访谈 – 2位用户对支付流程和加载速度的反馈
- 竞品-2024年2月竞品分析 – 3个竞品支付流程对比分析
```

---

## 支持的文件格式

| 格式 | 扩展名 | 处理方式 | 依赖 |
|------|--------|---------|------|
| Markdown | `.md`, `.txt` | 直接读取 | 无 |
| CSV | `.csv` | 直接读取 | 无 |
| Excel | `.xlsx`, `.xls` | 自动转换为 Markdown | Python + openpyxl |
| Word | `.docx` | 自动转换为 Markdown | Python + python-docx |
| PowerPoint | `.pptx` | 自动转换为 Markdown | Python + python-pptx |
| PDF | `.pdf` | 自动转换为 Markdown | Python + PyMuPDF |
| 图片 | `.png`, `.jpg`, `.gif`, `.webp` | LLM 视觉能力直接查看 | 无 |

> 📦 转换工具的 Python 依赖在 `/setup` 阶段自动安装。不需要转换的用户可以跳过。
> 转换脚本位于 `scripts/convert/`，每种格式独立一个脚本，方便维护。

---

## qmd 检索引擎深度解析

`qmd` 是 kb-wiki 配套的本地 Markdown 检索引擎，基于 Rust + TypeScript 实现，完整源码内嵌在 `scripts/qmd/`，`/setup` 时通过 `pnpm build` 自动编译。它是 `/query` 智能搜索的底层支撑。

### 三种检索模式

| 模式 | 命令 | 速度 | 召回质量 | 触发场景 |
|------|------|------|---------|---------|
| 🔤 **BM25 关键词** | `qmd bm25 "查询词"` | ⚡ <100ms | 中（依赖关键词命中） | 精确术语、文件名、引用 |
| 🧠 **向量语义** | `qmd vector "查询词"` | ⚡ <300ms | 高（同义词/语义相似） | 概念查询、跨语言、近义关键词 |
| ⚖️ **Hybrid 混合** | `qmd hybrid "查询词"` | 🐢 ~800ms | **最高**（BM25 + Vector + Rerank） | `/query` 默认调用 |

> 💡 `/query` 智能搜索默认走 Hybrid 模式；当 Hybrid 召回数 < 3 条时，自动 Fallback 到 RAG（直接读取相关文件原文）；最坏情况降级为 BM25 + 文件名匹配。

### 内嵌的 AI 模型

| 模型 | 任务 | 体积 | 调用方式 |
|------|------|------|---------|
| **EmbeddingGemma-300M** | 文本向量化（768 维） | ~600MB | 本地 ONNX，离线运行 |
| **Qwen3-Reranker-0.6B** | 候选结果重排（1-100 分） | ~1.2GB | 本地 ONNX，离线运行 |

> 🌍 模型会从 HuggingFace 自动下载；国内用户可在 `/setup` 时切换到 `hf-mirror.com` 镜像。模型下载完成后**全部离线运行**，不依赖网络也无数据外泄风险。

### CLI 与 MCP 双模式

`qmd` 同时支持两种调用方式：

```bash
# CLI 模式：人类直接用
qmd hybrid "支付流程痛点"
qmd embed                    # 增量构建/更新向量索引
qmd index                    # 重建 BM25 索引
qmd status                   # 查看索引状态

# MCP 模式：作为 MCP Server 供 LLM 调用
qmd mcp                      # 启动 MCP Server（被 Cursor / Claude Desktop 等连接）
```

### 增量索引机制

```
首次 /setup
  ├─ qmd index       全量构建 BM25 倒排索引（~3 秒/100 文件）
  └─ qmd embed       全量构建向量索引（~30 秒/100 文件，依赖 GPU/CPU）

后续 /ingest 后
  ├─ 检测变更文件     基于 mtime + content hash
  ├─ qmd index --inc 仅重索引变更文件（毫秒级）
  └─ qmd embed --inc 仅重新嵌入变更段落（秒级）
```

### Reranker 工作流

混合检索的最关键环节是 **Reranker**：

```
1. BM25 召回 Top-30 关键词候选
2. Vector 召回 Top-30 语义候选
3. 去重合并 → 60 → 40 候选段
4. Qwen3-Reranker 对 40 段评分（query 与 doc 的相关性 1-100 分）
5. 取 Top-K（默认 K=10）返回给 LLM
```

> 💡 Reranker 比单纯的向量相似度精准得多——它能判断"虽然语义相近但实际无关"的负样本（例如查询"支付失败"时排除掉"登录失败"的高语义相似项）。

### 性能与索引规模

| 指标 | 数值 |
|------|------|
| 单次混合查询 | ~800ms（含 Rerank） |
| 单次 BM25 查询 | <100ms |
| 单次 Vector 查询 | <300ms |
| BM25 索引大小 | 文档总量的 ~30% |
| 向量索引大小 | 文档总量的 ~150%（768 维 fp32） |
| 推荐文档规模上限 | 100,000 段（~50 万行 Markdown） |

### 索引故障排查

| 症状 | 根因 | 修复 |
|------|------|------|
| `/query` 提示「向量索引为空」 | 仅运行了 `qmd index`，未运行 `qmd embed` | `qmd embed` 全量嵌入 |
| `qmd embed` 提示「模型下载失败」 | 网络/防火墙阻断 HuggingFace | 切换 `HF_ENDPOINT=https://hf-mirror.com` |
| `qmd hybrid` 召回为空 | 索引文件损坏或不一致 | `qmd index --rebuild && qmd embed --rebuild` |
| 召回结果与查询主题不匹配 | 关键词在文档中确实不存在 | `/query` 自动降级到 RAG/文件名匹配，参考结果手动确认 |

---

## 推荐工具链

| 工具 | 用途 | 安装 |
|------|------|------|
| **Obsidian** | 实时浏览 wiki，图谱视图可视化页面关联结构 | [obsidian.md](https://obsidian.md) |
| **Obsidian Web Clipper** | 浏览器文章一键转 Markdown | [Chrome](https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf) / [Firefox](https://addons.mozilla.org/en-US/firefox/addon/web-clipper-obsidian/) |
| **qmd** | 本地 Markdown 搜索引擎（BM25 + 向量），完整源码内嵌在 `scripts/qmd/` | `/setup` 时自动编译 |
| **Marp** | 将 wiki 页面转为幻灯片 | Obsidian 插件：[Marp Slides](https://obsidian.md/plugins?id=marp-slides) |
| **Dataview** | Obsidian 中查询 wiki 数据 | Obsidian 插件：[Dataview](https://obsidian.md/plugins?id=dataview) |
| **git** | 知识库版本控制 | [git-scm.com](https://git-scm.com/downloads)，然后 `git init` 在知识库根目录 |

### Obsidian 配置建议

#### 附件文件夹设置

在 Obsidian 中打开 **设置 → 文件与链接**，将"附件文件夹路径"设为 `raw/assets`。这样所有通过 Web Clipper 剪藏或粘贴保存的图片会自动存入 `raw/assets/` 目录。

#### 本地下载图片

在 **设置 → 快捷键** 中，搜索 "Download"，找到 "Download attachments for current file"，绑定快捷键（推荐 `Ctrl+Shift+D`）。剪藏文章后按快捷键，所有远程图片会下载到本地 `raw/assets/` 目录，避免 URL 失效。

#### 关于 LLM 与图片

LLM 无法在一次操作中读取含有内联图片的 Markdown 文件。解决方法：让 LLM 先读取文本内容，然后单独查看部分或全部引用的图片以获取额外上下文。虽然略显笨拙，但效果足够好。

#### 图谱视图

打开 Obsidian 的 **图谱视图（Graph View）**，可以可视化浏览 wiki 中所有页面之间的链接关系——哪些页面是枢纽节点、哪些页面相互关联、哪些页面是孤立的。这是观察知识库形状最直观的方式。

---

## 与传统 RAG 的区别

| | 传统 RAG | kb-wiki |
|---|---|---|
| 知识形式 | 原始文档向量索引 | LLM 提炼的结构化 Wiki |
| 矛盾处理 | 原样返回冲突内容 | 标注并综合矛盾 |
| 知识增长 | 线性堆积 | 复利式增长（交叉引用强化） |
| 可读性 | 机器友好 | 人类可直接阅读 |
| 维护者 | 人类 | LLM |
| 查询质量 | 依赖相似度 | 依赖语义理解 + 知识综合 |
| 输入格式 | 纯文本/PDF | Markdown, Excel, Word, PPT, PDF, 图片 |

---

## 为什么有效

维护知识库最繁琐的部分不是阅读和思考——而是**簿记工作**：更新交叉引用、保持摘要最新、标注新数据与旧结论的矛盾、在数十个页面间维护一致性。

**人类会放弃 wiki，因为维护负担的增长速度快于知识价值的增长速度。**

LLM 改变了这个等式：
- 🤖 **不会厌倦**：更新第 100 个交叉引用和第 1 个一样准确
- 🤖 **不会遗忘**：不会忘记更新某个角落里的引用
- 🤖 **一次触及 15 个文件**：单次 ingest 自动更新 10-15 个 wiki 页面

**Wiki 之所以能持续保持维护状态，是因为维护成本趋近于零。**

**分工**：
- 🧑 **人类的工作**：策划来源、引导分析方向、提出正确的问题、思考信息的意义
- 🤖 **LLM 的工作**：其他一切

---

## 进阶用法

### git 版本控制

```bash
cd ~/Desktop/ux-research  # 你的知识库根目录
git init
echo "raw/assets/*.mp4" >> .gitignore  # 忽略大文件
git add .
git commit -m "feat: 初始化知识库"
```

### qmd MCP 模式（给 Claude Desktop）

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "kb-wiki": {
      "command": "qmd",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

### 多人协作

```bash
# 共享知识库（推荐方案）
# 1. 将知识库推送到私有 git 仓库
# 2. 团队成员 clone 后各自配置 qmd 集合
# 3. 通过 PR/merge 合并各自的 ingest 内容
```

---

## 许可证

MIT © [2811jh](https://github.com/2811jh)