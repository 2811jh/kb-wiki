# Setup 工作流：初始化知识库

> 本文档供 LLM 执行 `/setup` 命令时参考。首次运行时完整执行以下流程。

---

## 完整流程

### 步骤 1：检测 Node.js 环境

```bash
node --version
```

**判断逻辑**：
- 版本 >= 22：继续
- 版本 < 22 或未安装：告知用户需要升级

告知用户的信息：
```
❌ 需要 Node.js >= 22，当前版本为 <版本号>。
请前往 https://nodejs.org 下载最新 LTS 版本后重新运行 /setup。
```

各平台快速安装命令：

Windows（PowerShell，推荐使用 nvm-windows）：
```powershell
winget install CoreyButler.NVMforWindows
nvm install 22
nvm use 22
```

macOS（推荐使用 nvm）：
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22
nvm use 22
```

Linux（Ubuntu/Debian）：
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

或直接前往 https://nodejs.org 下载 v22 LTS 安装包。

---

### 步骤 2：检测 Python 环境 + 安装文件转换依赖

kb-wiki 支持导入 Excel、Word、PowerPoint、PDF 等非文本格式文件。这些格式的转换需要 Python 环境。

```bash
python --version
# 或者
python3 --version
```

**判断逻辑**：
- Python >= 3.10：继续安装依赖
- 未安装 Python：告知用户（非强制，不影响核心功能）

**安装转换工具依赖**：

```bash
pip install -r <SKILL_PATH>/scripts/convert/requirements.txt
```

> 💡 如果用户没有 Python 或不需要非文本格式转换，可以跳过此步骤。
> 核心功能（.md 文件的 ingest/query/lint）不依赖 Python。
> 后续需要时可随时运行 `pip install -r <SKILL_PATH>/scripts/convert/requirements.txt` 补装。

**安装成功确认**：

```bash
python -c "import docx, openpyxl, pptx, fitz; print('✅ 所有转换依赖已就绪')"
```

**如果安装失败**：

```
⚠️ 文件转换依赖安装失败。
核心功能不受影响：
  - .md / .txt / .csv 文件的 /ingest：✅ 正常
  - /query、/lint：✅ 正常
  - .xlsx / .docx / .pptx / .pdf 的自动转换：❌ 不可用

后续需要时，请手动运行：
  pip install -r <SKILL_PATH>/scripts/convert/requirements.txt
```

---

### 步骤 3：安装并编译 qmd 搜索引擎

qmd 的完整源码已内嵌在 skill 的 `scripts/qmd/` 目录中，但首次使用需要安装依赖并编译。

**自动执行以下命令**（LLM 直接执行，无需用户操作）：

**2.0 确定 skill 安装路径**

LLM 应按以下优先级查找 kb-wiki skill 的安装路径：

```bash
# 检查常见安装位置（按优先级）
# 1. Claude Code：.claude/skills/kb-wiki/
# 2. 通用 agents：.agents/skills/kb-wiki/
# 3. 用户主目录：~/.skills/kb-wiki/

ls ~/.claude/skills/kb-wiki/scripts/qmd/ 2>/dev/null || \
ls ~/.agents/skills/kb-wiki/scripts/qmd/ 2>/dev/null || \
ls ~/.skills/kb-wiki/scripts/qmd/ 2>/dev/null
```

找到后记录为 `SKILL_PATH`，后续 qmd 路径为：
`SKILL_PATH/scripts/qmd/dist/cli/qmd.js`

Windows 等价：
```powershell
# 检查常见安装位置
Test-Path "$env:USERPROFILE\.agents\skills\kb-wiki\scripts\qmd"
Test-Path "$env:USERPROFILE\.claude\skills\kb-wiki\scripts\qmd"
```

```bash
# 2.1 检测 pnpm 是否可用
pnpm --version
# 如果 pnpm 不可用，先安装：
npm install -g pnpm

# 2.2 进入 qmd 目录安装依赖
cd <SKILL_PATH>/scripts/qmd
pnpm install --no-frozen-lockfile

# 2.3 编译 TypeScript
npx tsc -p tsconfig.build.json

# 2.4 验证编译成功
node dist/cli/qmd.js --version
```

> ⚠️ 注意：`<SKILL_PATH>` 是 `npx skills add` 安装 skill 到本地的路径。LLM 应自动检测此路径（通常在 `~/.skills/` 或 `.agents/skills/` 下）。

**编译成功**：
```
✅ qmd 搜索引擎编译成功（版本：x.x.x）！
   qmd 是本地 Markdown 搜索引擎（BM25 + 向量混合搜索），完全在本地运行。
```

**如果 pnpm install 失败**，尝试回退到 npm：
```bash
npm install
npx tsc -p tsconfig.build.json
```

**如果仍然失败**，告知用户：
```
⚠️ qmd 编译失败。常见原因：
   - 缺少 C++ 编译工具（Windows: Visual Studio Build Tools, macOS: xcode-select --install）
   - Node.js 版本 < 22（当前版本：<版本号>）
   
   不影响知识库的基本功能（ingest/lint 仍可正常使用），
   但 /query 的混合搜索功能暂时不可用。
   解决问题后可重新运行 /setup 来编译 qmd。
```

**LLM 调用 qmd 的方式**（编译成功后，所有后续命令统一用此方式）：

```bash
# 直接用 node 调用编译后的入口
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js <命令> [参数]

# 例如：
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js query "用户痛点"
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js update
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js collection list
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js embed
```

> 💡 LLM 应在 setup 完成后记住 qmd 的完整调用路径，后续 ingest/query 时直接使用。

### 步骤 4：配置 HuggingFace 镜像（中国大陆用户）

qmd 的完整搜索功能需要下载 AI 模型（约 2GB），模型托管在 HuggingFace 上。中国大陆用户需要设置镜像：

**询问用户**：
```
你是否在中国大陆使用？如果是，需要配置 HuggingFace 镜像以下载 AI 搜索模型。
```

**如果用户确认**，帮助设置环境变量：

Windows PowerShell：
```powershell
[System.Environment]::SetEnvironmentVariable('HF_ENDPOINT', 'https://hf-mirror.com', 'User')
```

macOS/Linux（追加到 ~/.bashrc 或 ~/.zshrc）：
```bash
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.zshrc
source ~/.zshrc
```

**模型下载说明**（告知用户）：
```
qmd 的搜索功能分三个层级，模型在首次使用时自动下载到 ~/.cache/qmd/models/：

层级 1 - BM25 关键词搜索：无需模型，安装后即可使用
层级 2 - 向量语义搜索：需要 Embedding 模型（~300MB）
层级 3 - 完整混合搜索：需要全部 3 个模型（~2GB）
  - embeddinggemma-300M（向量嵌入，~300MB）
  - qmd-query-expansion-1.7B（查询扩展 HyDE/Vec/Lex，~1GB）
  - Qwen3-Reranker-0.6B（结果重排序，~600MB）

模型会在首次使用对应功能时自动下载，无需手动操作。
```

> 💡 说明：`qmd embed`（步骤 12）会自动下载层级 2 所需的模型（~1.3GB）。层级 3 的重排序模型（~600MB）在首次执行 `qmd query` 时按需下载。

---

### 步骤 5：询问知识库名称

提示用户：

```
请为你的知识库起一个名称。
建议使用英文小写，用连字符分隔，例如：
  - ux-research（UX 研究）
  - product-wiki（产品知识库）
  - competitive-analysis（竞品分析）
  - interview-notes（用户访谈）

知识库名称：
```

记录用户输入为 `WIKI_NAME`。

---

### 步骤 6：询问知识库位置

提示用户：

```
知识库将创建在哪个位置？

1. 桌面（推荐）：~/Desktop/{{WIKI_NAME}}
2. 自定义路径

请选择（1 或 2）：
```

**如果选择 1（桌面）**：
- macOS/Linux：路径为 `~/Desktop/{{WIKI_NAME}}`
- Windows：路径为 `%USERPROFILE%\Desktop\{{WIKI_NAME}}`

**如果选择 2（自定义）**：
```
请输入完整路径（例如：/Users/name/Documents/research）：
```

记录最终路径为 `WIKI_PATH`。

确认信息：
```
📂 知识库将创建在：{{WIKI_PATH}}
确认？（回车确认，或输入新路径）：
```

---

### 步骤 7：创建目录结构

执行以下目录创建命令（macOS/Linux）：

```bash
mkdir -p "{{WIKI_PATH}}/raw/articles"
mkdir -p "{{WIKI_PATH}}/raw/papers"
mkdir -p "{{WIKI_PATH}}/raw/assets"
mkdir -p "{{WIKI_PATH}}/raw/data"
mkdir -p "{{WIKI_PATH}}/wiki/entities"
mkdir -p "{{WIKI_PATH}}/wiki/concepts"
mkdir -p "{{WIKI_PATH}}/wiki/sources"
mkdir -p "{{WIKI_PATH}}/wiki/synthesis"
mkdir -p "{{WIKI_PATH}}/wiki/.cache"
```

Windows 等价命令：

```powershell
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\raw\articles"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\raw\papers"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\raw\assets"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\raw\data"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\wiki\entities"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\wiki\concepts"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\wiki\sources"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\wiki\synthesis"
New-Item -ItemType Directory -Force -Path "{{WIKI_PATH}}\wiki\.cache"
```

---

### 步骤 8：生成 Schema.md

将以下占位符替换后写入 `{{WIKI_PATH}}/Schema.md`：

| 占位符 | 替换为 |
|--------|--------|
| `{{WIKI_NAME}}` | 用户输入的知识库名称 |
| `{{WIKI_PATH}}` | 知识库完整路径 |
| `{{CURRENT_DATE}}` | 当前日期（格式：YYYY-MM-DD） |

以下是 Schema.md 的完整模板内容（将 `{{WIKI_NAME}}`、`{{WIKI_PATH}}`、`{{CURRENT_DATE}}` 替换为实际值后写入文件）：

````markdown
# {{WIKI_NAME}} 知识库规范（Schema.md）

> **这是知识库的 Schema 层文件**，告诉 LLM 如何工作。
> 创建于：{{CURRENT_DATE}}
> 知识库路径：{{WIKI_PATH}}
>
> **演进说明**：这个文件是可以修改的。随着你使用知识库，你和 LLM 可以共同修改这里的规范，
> 使其更贴合你的研究领域、工作习惯和偏好。这是 kb-wiki 适应个人需求的核心机制。

---

## 1. 知识库概述

**名称**：{{WIKI_NAME}}

**用途**：[请描述这个知识库的主要用途，例如：UX 研究知识库，用于积累和查询用户访谈、竞品分析、用户体验研究资料]

**主要领域**：[例如：用户体验研究 / 产品设计 / 竞品分析 / 用户行为研究]

**目标用户**：[例如：UX 研究员、产品经理、设计师]

**语言**：中文（所有 wiki 页面使用中文，资料可以是任何语言）

> **Schema.md 的核心目标**：让 LLM 成为训练有素的 Wiki 维护者，而非通用聊天机器人。这份规范定义了 LLM 的工作方式。

---

## 2. 目录结构说明

```
{{WIKI_PATH}}/
├── Schema.md              ← 本文件（Schema 层，告诉 LLM 如何工作）
│
├── raw/                   ← 原始资料层（只读，LLM 不可修改）
│   ├── articles/          ← 文章、访谈记录、新闻稿
│   ├── papers/            ← 学术论文、研究报告
│   ├── assets/            ← 图片、截图等媒体文件
│   └── data/              ← 数据文件（CSV、JSON 等）
│
└── wiki/                  ← Wiki 层（LLM 完全掌控）
    ├── entities/          ← 实体页面
    │                         用户画像、产品功能、组织、竞品等
    ├── concepts/          ← 概念页面
    │                         用户痛点、行为模式、设计模式、研究发现等
    ├── sources/           ← 资料摘要页面
    │                         每份原始资料对应一个摘要页，不可替代原始资料
    ├── synthesis/         ← 综合分析页面
    │                         对比分析、概览、跨资料结论、洞察归档、行动建议
    ├── index.md           ← 内容目录（每次 ingest 必须更新）
    └── log.md             ← 操作日志（append-only，知识库演进的时间线，帮助 LLM 理解近期动态）
```

---

## 3. 重要原则

### LLM 的职责边界

1. **raw/ 目录绝对只读**：永远不要修改 `raw/` 中的任何文件。这是原始来源的真相，不可改变。
2. **wiki/ 目录 LLM 完全掌控**：可以自由创建、修改、重组 `wiki/` 中的所有页面。
3. **用户不需要手动编写 Wiki**：所有 wiki 内容由 LLM 生成和维护。用户只负责提供资料、进行探索和提问。
4. **log.md 只追加**：只在末尾添加记录，不删改已有历史记录。

### 知识质量原则

5. **交叉引用是价值所在**：每次 ingest 都要主动创建页面之间的关联，这是知识复利的核心。
6. **标注矛盾，不隐藏矛盾**：发现不一致时，明确标注 `⚠️ 矛盾`，不要静默覆盖。
7. **综合结论要反映所有来源**：`synthesis/` 页面要综合所有相关资料，不偏向单一来源。
8. **好的查询结果值得归档**：有价值的分析结论保存到 `synthesis/`，避免重复工作。

---

## 4. Ingest 工作流（导入新资料）

当用户运行 `/ingest` 时，按以下 10 步执行：

1. **读取资料**：读取 `raw/` 中的原始文件，或用户提供的文本内容
2. **理解要点**：提取关键发现、重要引述、涉及的用户/产品/概念
3. **写摘要页面**：在 `wiki/sources/` 创建摘要页面（格式见下方第 8 节）
4. **更新 index.md**：在对应分类下添加新页面条目（格式：`- 页面名 – 摘要`，**纯文本，禁止 `[[]]`**）
5. **更新 entities/**：更新或创建本次资料涉及的实体页面（用户、产品、组织等）
6. **更新 concepts/**：更新或创建本次资料涉及的概念页面（痛点、行为模式等）
7. **检查矛盾**：对比新资料与现有 wiki 内容，用 `⚠️ 矛盾` 标注发现的冲突
8. **更新综合结论**：在 `synthesis/` 相关页面中强化或修订已有结论
9. **记录日志**：在 `wiki/log.md` 末尾追加记录（格式：`## [YYYY-MM-DD] ingest | 资料标题`）
10. **重建索引**：运行 `qmd update` 重建搜索索引，然后运行 `qmd embed` 更新向量嵌入

**完成后汇报**：告知用户更新了哪些页面（新建/更新），发现了哪些矛盾，修订了哪些综合结论。

---

## 5. Query 工作流（查询知识库）

当用户运行 `/query` 时，按以下步骤执行：

1. **执行 qmd 搜索**：先运行 `qmd status` 确认索引状态，然后优先使用 `qmd query "问题"` 混合搜索（向量索引未就绪时回退到 `qmd search`）
2. **读取 index.md**：补充搜索盲区，了解知识库全貌
3. **读取相关页面**：通过 `qmd get` 或 `qmd multi-get` 读取搜索结果中的页面
4. **生成综合答案**：基于多个页面的内容，综合生成答案（带引用，标注置信度）
5. **标注矛盾**：如果不同来源有冲突，明确指出
6. **询问是否归档**：询问用户是否将本次分析归档到 `wiki/synthesis/`
7. **归档并记录**（如确认）：创建 synthesis 页面，更新 index.md，在 log.md 追加记录

**答案格式**：优先使用 Markdown，可根据需求切换为表格、Marp 幻灯片、行动项清单等形式。

---

## 6. Lint 工作流（健康检查）

当用户运行 `/lint` 时，执行以下 7 项检查：

1. **矛盾论断检测**：找出不同页面间相互冲突的论断
2. **过时论断检测**：找出被更新资料取代但未更新的旧结论
3. **孤立页面检测**：找出没有入站链接的页面
4. **缺失页面检测**：找出被引用但实际不存在的页面
5. **缺失交叉引用检测**：找出语义相关但未互链的页面对
6. **数据空白检测**：识别缺失的重要信息和研究方向
7. **日志完整性检查**：确认 log.md 格式正确，记录完整

**输出**：结构化的 Lint 报告，包含总览表格、详细问题列表、修复建议（按优先级）、推荐探索方向。

**完成后记录**：在 log.md 追加 `## [YYYY-MM-DD] lint | N issues found`

---

## 7. Lint 提醒规则

每完成 **5 次** `/ingest` 操作后，在回复末尾自动追加：

```
---
💡 **知识库健康提醒**：你已经导入了 5 份新资料（自上次健康检查以来）。
你可以对我说"对知识库进行健康检查"，我会帮你检测矛盾、孤立页面、缺失引用等问题。
---
```

**计数方法**：读取 `wiki/log.md`，统计最后一条 `lint` 记录之后的 `ingest` 记录数量。

```bash
grep "^## \[" wiki/log.md | tail -20
```

---

## 8. 页面格式规范

### 文件命名规范

Wiki 页面文件名采用 **`{类型前缀}-{描述}.md`** 纯中文格式，类型前缀确保分类清晰，便于 Obsidian 图谱识别。

**格式**：`{类型前缀}-{描述}.md`

#### 命名流程（LLM 每次创建页面时执行）

```
1. 扫描同目录下已有文件名 → 提取已用前缀列表
2. 判断新页面是否匹配已有前缀 → 是 → 复用（保持一致性）
3. 不匹配 → LLM 自主创建新前缀（2-3 个字，概括该类内容的本质）
4. 新前缀自动成为该知识库的惯例，后续同类页面沿用
```

> 💡 **核心原则**：前缀是**活约定**而非死目录。LLM 拥有自主命名权，但必须优先复用已有前缀保持一致性。

#### 初始前缀参考

以下为**建议起步前缀**，LLM 可根据实际资料内容自主调整或新增：

| 目录 | 常见前缀（仅供参考） | 示例 |
|------|---------------------|------|
| concepts/ | `痛点-`、`行为-`、`需求-` … | `痛点-加载速度.md`、`行为-社交驱动流失.md` |
| sources/ | `问卷-`、`访谈-`、`竞品-`、`报告-` … | `问卷-春节满意度.md`、`访谈-回流玩家.md` |
| entities/ | `用户-`、`产品-`、`组织-` … | `用户-女性玩家.md`、`产品-基岩版.md` |
| synthesis/ | `对比-`、`洞察-`、`概览-` … | `对比-基岩与Java版.md`、`洞察-付费障碍.md` |

> **省略号 `…` 表示 LLM 可自由扩展**。例如导入了一份会议纪要，LLM 可创建 `会议-` 前缀；导入了一段视频笔记，可创建 `视频-` 前缀。

#### 前缀管理规则

1. **优先复用**：创建新页面时，先看同目录已有哪些前缀，优先使用已有的
2. **自主新建**：没有合适前缀时，LLM 自主创建（2-3 个字，简洁概括）
3. **描述简洁**：前缀后的描述部分 2-8 个字，代表页面核心主题
4. **纯中文**：不附加英文 slug
5. **避免特殊字符**：`/ \ : * ? " < > |` 不可出现在文件名中
6. **Schema.md 记录**：如果某个新前缀被连续使用 3 次以上，建议在 Schema.md 中正式记录

### 所有 wiki 页面必须包含 YAML frontmatter

```yaml
---
title: 页面标题（与 H1 一致）
slug: english-slug（英文标识符，用于 qmd 搜索和程序化引用，不影响文件名）
type: source | entity | concept | synthesis（页面类型）
date: YYYY-MM-DD（创建日期）
updated: YYYY-MM-DD（最后更新日期，每次修改时更新）
tags: [标签1, 标签2, 标签3]
sources: [sources/相关摘要1, sources/相关摘要2]
related: [entities/实体页, concepts/概念页, synthesis/综合页]
aliases: [别名1, 别名2]（可选，页面的其他称呼，便于搜索和引用）
severity: high | medium | low（可选，仅痛点/问题类页面使用，标识严重程度）
frequency: high | medium | low（可选，仅痛点/问题类页面使用，标识出现频率）
---
```

**字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 页面标题，与 H1 一致 |
| `slug` | ✅ | 英文标识符，用于 qmd 搜索和程序化引用（如 `search-pain-points`），不影响文件名 |
| `type` | ✅ | 页面类型：`source` / `entity` / `concept` / `synthesis` |
| `date` | ✅ | 创建日期 |
| `updated` | ✅ | 最后更新日期，每次修改时更新 |
| `tags` | ✅ | 分类标签，便于 Dataview 查询 |
| `sources` | ✅ | 引用的 sources/ 摘要页面列表 |
| `related` | ✅ | 关联页面列表（跨目录交叉引用） |
| `aliases` | 可选 | 页面的其他称呼（如"NPS"和"净推荐值"互为 alias），便于搜索命中 |
| `severity` | 可选 | 仅用于痛点/问题类概念页，标识严重程度 |

> ⚠️ **YAML 安全规则**：frontmatter 值中含有 `[ ] : #` 等特殊字符时，**必须用双引号包裹**。
> 否则 Obsidian 无法解析 frontmatter，会显示为红色原始文本。
> ```yaml
> # ❌ 解析失败（嵌套方括号）
> sources: [raw/articles/[UX][G79]报告.pdf]
>
> # ✅ 正确
> sources: ["raw/articles/[UX][G79]报告.pdf"]
> ```
| `frequency` | 可选 | 仅用于痛点/问题类概念页，标识出现频率 |

### 交叉引用格式

优先使用 Obsidian 风格（方便在 Obsidian 中导航）：

```markdown
[[页面名]]              ← 同目录引用
[[entities/用户-A]]    ← 跨目录引用（推荐写法）
```

标准 Markdown 格式（作为备选）：

```markdown
[用户 A 的完整画像](../entities/用户-A.md)
```

### 特殊标注格式

```markdown
> ⚠️ **矛盾**：[[sources/资料A]] 认为 X，但 [[sources/资料B]] 显示 Y。
> 可能原因：...  建议：通过 [...] 方式进一步验证。

> 💡 **综合结论**：基于 N 份资料，[结论]。
> 置信度：高/中/低（来源数量和一致性）

> ❓ **待验证**：[论断] 目前仅有 1 份资料支撑，需要更多证据。

> 🔄 **已更新**：此结论已被 [[sources/新资料]] 取代，
> 最新观点见 [[concepts/新页面]] 第 X 节。
```

### sources/ 摘要页面结构

> 💡 文件名示例：`问卷-12月满意度调研.md`、`访谈-回流玩家.md`、`竞品-玩家竞品游玩情况.md`

```markdown
---
title: 问卷-12月满意度调研
slug: source-english-slug
type: source
date: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [资料类型, 主题标签]
sources: [raw/articles/原始文件名.md]
related: [entities/..., concepts/...]
aliases: [资料简称]
---

# 问卷-12月满意度调研

## 来源信息
- 原始文件、日期、类型、作者/对象

## 核心发现
- 分主题列出主要发现

## 关键引述
> "原文引用" —— 来源

## 与现有知识的关联
- 强化或挑战哪些已有页面

## 综合意义
> 💡 **综合结论**：...
```

### entities/ 实体页面结构

> 💡 文件名示例：`用户-回流玩家群体.md`、`产品-基岩版.md`、`服务器-山头服.md`

```markdown
---
title: 用户-回流玩家群体
slug: entity-english-slug
type: entity
date: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [实体类型, 标签]
sources: [sources/...]
related: [concepts/...]
aliases: [实体别名, 英文名]
---

# 用户-回流玩家群体

## 基本信息
- 关键属性列表

## 与本知识库相关的核心信息
- 分主题展示，每条都有来源引用

## 来源资料
- [[sources/...]]（日期）：一行说明
```

### concepts/ 概念页面结构

> 💡 文件名示例：`痛点-加载速度.md`、`行为-重复点击.md`、`需求-快捷支付.md`

```markdown
---
title: 痛点-加载速度
slug: concept-english-slug
type: concept
date: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [概念类型, 标签]
sources: [sources/...]
related: [entities/..., concepts/..., synthesis/...]
aliases: [概念别名]
severity: high | medium | low（可选，仅痛点/问题类使用）
frequency: high | medium | low（可选，仅痛点/问题类使用）
---

# 痛点-加载速度

## 当前认知（基于 N 份资料）
综合描述 + 💡 综合结论

## 具体表现/证据
分来源列出，每条有引用

## 矛盾与待解问题
⚠️ 矛盾标注 + ❓ 待验证

## 资料来源
来源列表
```

---

## 9. index.md 格式规范

> ⚠️ **关键规则：index.md 禁止使用 `[[wiki-link]]`，必须使用纯文本。**
> 原因：index.md 链接到所有页面，会在 Obsidian 图谱中形成巨大的星形中心节点，掩盖页面之间真正有意义的关联。

```markdown
# {{WIKI_NAME}} 知识库索引

> 最后更新：YYYY-MM-DD | 页面总数：N（sources: x | entities: x | concepts: x | synthesis: x）
>
> ℹ️ 本页使用纯文本列表（非 wiki-link），避免在 Obsidian 图谱中产生干扰性的星形连线。

---

## sources/（资料摘要）

- 资料名-1 – 一行摘要描述
- 资料名-2 – 一行摘要描述

---

## entities/（实体页面）

- 实体名-1 – 一行描述
- 实体名-2 – 一行描述

---

## concepts/（概念页面）

- 概念名-1 – 一行描述

---

## synthesis/（综合分析）

- 分析名-1 – 一行描述
```

**规则**：
- 每次 ingest 后必须更新 index.md
- 每行格式：`- 页面名 – 一行摘要`（**纯文本，禁止 `[[]]`**）
- 使用 `–`（en-dash）分隔页面名和摘要，便于阅读
- 查询时先读 index.md 定位相关页面

---

## 10. log.md 格式规范

```markdown
# 操作日志

> 此文件记录所有 ingest、query（归档）、lint 操作。
> 格式：## [YYYY-MM-DD] ingest/query/lint | 标题
> 规则：只允许追加，不允许删改历史记录。
> 解析：grep "^## \[" log.md | tail -10

---

## [2026-01-15] ingest | 用户访谈 - 2026年1月

- 来源文件：raw/articles/user-interview-2026-01.md
- 更新页面：sources/访谈-2026年1月用户访谈（新建）、entities/用户-A（更新）
- 矛盾标注：0 处
- 修订综合结论：1 处

## [2026-01-20] query | 支付流程用户痛点

- 归档到：synthesis/洞察-支付流程痛点.md

## [2026-01-25] lint | 3 issues found

- 矛盾: 1 | 孤立页面: 1 | 数据空白: 1
```

**格式要求**：
- 标题行必须以 `## [YYYY-MM-DD]` 开头（行首，无缩进）
- 支持 `grep "^## \[" log.md | tail -5` 解析最近操作
- 支持 `grep "^## \[" log.md | grep "ingest" | wc -l` 统计 ingest 次数

---

## 11. qmd 工具使用说明

```bash
# 集合名称（由 /setup 配置）
集合名称：{{WIKI_NAME}}
集合路径：{{WIKI_PATH}}/wiki

# 常用命令
qmd query "问题"                           ← 混合搜索（推荐，大多数场景）
qmd search "关键词" --collection {{WIKI_NAME}}  ← 精确关键词搜索
qmd vsearch "描述" --collection {{WIKI_NAME}}   ← 语义搜索（需 qmd embed）
qmd get wiki/concepts/页面.md             ← 读取单个页面
qmd multi-get "wiki/entities/*.md"        ← 批量读取
qmd ls --collection {{WIKI_NAME}}         ← 列出所有 wiki 页面
qmd update                                 ← 重建索引（每次 ingest 后）
qmd embed --chunk-strategy auto            ← 生成向量嵌入（用于语义搜索）
qmd status                                 ← 查看索引状态
qmd mcp                                    ← 启动 MCP server（stdio 模式）
```

---

## 12. 如何演进此规范

这个文件（Schema.md）是**可以也应该被修改的**。随着你使用知识库，你和 LLM 可以共同修改这里的规范。

**常见演进场景**：

### 添加新的目录分类

如果你需要新的分类（如 `wiki/personas/` 用于用户画像），在本文件中添加目录说明：
```markdown
│   ├── personas/          ← 用户画像（完整人物志，区别于 entities/ 的简要实体页）
```

### 修改页面格式

如果你的领域有特定的信息结构，修改第 8 节的页面格式规范。

### 自定义 Lint 检查规则

在第 6 节 Lint 工作流中，添加或删除检查项。

### 调整 Lint 提醒频率

修改第 7 节的触发条件（默认每 5 次 ingest 提醒一次）。

### 修改语言设置

如果需要英文或其他语言的 wiki，修改概述部分的语言设置。

### 适配不同的 LLM

如果你使用的是 GPT-4、Gemini 或其他 LLM 而非 Claude，可能需要调整页面格式和工作流指令以适应该 LLM 的特点。例如，不同 LLM 对 Markdown 结构的偏好、上下文窗口大小、工具使用方式可能不同。可以将此文件重命名为 AGENTS.md 或 Schema.md 以外的适合的名字。

### 替换工具链

kb-wiki 的所有工具（qmd、Obsidian 等）都是推荐但非必须的。你可以根据自己的偏好替换为其他工具：
- 搜索引擎：替换 qmd 为其他 Markdown 搜索工具
- 编辑器：替换 Obsidian 为 VS Code、Logseq、Notion 等
- 版本控制：替换 git 为其他方案

确切的目录结构、规范约定、页面格式、工具链——所有这些都取决于你的领域、你的偏好以及你选择的 LLM。

---

> **提示**：每次修改 Schema.md 时，建议在 log.md 中追加一条记录：
> `## [YYYY-MM-DD] setup | 更新 Schema.md - [修改摘要]`
````

将结果写入 `{{WIKI_PATH}}/Schema.md`。

---

### 步骤 9：创建 index.md

在 `{{WIKI_PATH}}/wiki/index.md` 写入：

> 💡 以下模板中的 `{{WIKI_NAME}}` 替换为实际知识库名称，`{{当前日期}}` 替换为当天日期（如 2026-04-16）。

```markdown
# {{WIKI_NAME}} 知识库索引

> 最后更新：{{CURRENT_DATE}} | 页面总数：0（sources: 0 | entities: 0 | concepts: 0 | synthesis: 0）
>
> ℹ️ 本页使用纯文本列表（非 wiki-link），避免在 Obsidian 图谱中产生干扰性的星形连线。

---

## sources/（资料摘要）

*暂无内容，等待第一次 /ingest*

---

## entities/（实体页面）

*暂无内容，等待第一次 /ingest*

---

## concepts/（概念页面）

*暂无内容，等待第一次 /ingest*

---

## synthesis/（综合分析）

*暂无内容，等待第一次 /ingest*
```

---

### 步骤 10：创建 log.md

在 `{{WIKI_PATH}}/wiki/log.md` 写入：

```markdown
# 操作日志

> 此文件记录所有 ingest、query（归档）、lint 操作。
> **格式**：`## [YYYY-MM-DD] ingest/query/lint | 标题`
> **规则**：只允许追加，不允许删改历史记录。
> **用途**：可用 `grep "^## \[" log.md | tail -10` 查看最近操作。

---

## [{{CURRENT_DATE}}] setup | {{WIKI_NAME}} 知识库初始化完成
```

---

### 步骤 11：配置 qmd 集合

如果 qmd 已安装，执行：

```bash
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js collection add "{{WIKI_PATH}}/wiki" --name "{{WIKI_NAME}}"
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js collection list
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js update
```

预期输出：
```
✅ 已添加集合 "{{WIKI_NAME}}" -> {{WIKI_PATH}}/wiki
已重建索引（0 个文件，2 个系统文件）
```

---

### 步骤 12：预下载 AI 搜索模型

> 🚫 **此步骤为强制步骤，不可跳过、不可延迟到 `/query` 时再做。**
> 没有完成此步骤的知识库视为**未创建完成**，不允许输出欢迎信息（步骤 13）。
>
> 原因：如果此步骤被跳过，后续 `/query` 只能使用 BM25 关键词搜索，
> 向量语义搜索和 LLM 重排序都无法启用，搜索质量严重下降。

**告知用户**：

```
📥 正在预下载 AI 搜索模型（共约 2GB，只需下载一次）：
   - embeddinggemma-300M    向量嵌入模型（~300MB）
   - qmd-query-expansion    查询扩展模型（~1GB）
   - Qwen3-Reranker-0.6B   结果重排序模型（~600MB）

模型保存到：~/.cache/qmd/models/
下载完成后，/query 将自动使用混合搜索（质量最高）。
```

**执行模型预下载**：

qmd 的 AI 模型在**首次运行 `qmd embed` 时自动下载**（无需单独的 pull 命令）。

```bash
# 触发模型下载 + 对初始 wiki 目录（index.md + log.md）生成向量嵌入
# ⚠️ 首次运行会下载约 1.3GB 模型，时间较长，请耐心等待
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js embed
```

> ⚠️ **注意**：`qmd embed` 运行时**没有进度条输出**，这是 qmd 当前版本的特性。
> 模型下载可能需要 5-30 分钟（取决于网速），期间命令会静默等待，这是**正常现象**，请勿中断。

验证模型是否下载并嵌入成功：

```bash
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js status
```

在 `status` 输出中检查 `Vectors` 一行：
- `Vectors: N embedded`（N > 0）→ ✅ 嵌入成功，向量搜索可用
- `Vectors: 0 embedded` → ⚠️ 嵌入未完成，可能模型还在下载中，稍后重试

**成功标志**（status 输出示例）：

```
Documents
  Total:    2 files indexed
  Vectors:  2 embedded    ← 这里应该 > 0
  Pending:  0 need embedding
```

**如果 embed 因网络问题失败**（仅此情况允许暂缓）：

```
🔴 向量索引建立失败（原因：[具体错误信息]）。
知识库创建【未完成】，搜索功能受限：
  - /ingest：✅ 可用
  - /lint：✅ 可用
  - /query（BM25 关键词搜索）：⚠️ 降级可用（仅关键词匹配，语义搜索不可用）
  - /query（向量语义搜索 + LLM 重排序）：❌ 不可用

⚠️ 请尽快解决网络问题后运行以下命令完成初始化：
  node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js embed
```

> 🚫 **注意**：用户主动说"跳过"时，LLM 应解释跳过的后果（搜索质量严重下降），并建议用户稍后补完。不允许 LLM 自行决定跳过。

---

### 步骤 13：输出欢迎信息

```
╔══════════════════════════════════════════════════════════╗
║   🎉 知识库 "{{WIKI_NAME}}" 初始化完成！                  ║
╚══════════════════════════════════════════════════════════╝

📂 位置：{{WIKI_PATH}}

目录结构：
  raw/articles/   ← 将文章、访谈记录放在这里
  raw/papers/     ← 将论文、报告放在这里
  raw/assets/     ← 将图片等媒体文件放在这里
  raw/data/       ← 将数据文件放在这里
  wiki/           ← LLM 自动管理，无需手动编辑
  Schema.md       ← 知识库规范（可自定义）

🚀 现在开始导入你的第一份资料吧！直接告诉我：
  · "帮我把桌面上的xxx导入知识库"
  · "把 C:\xxx\报告.pdf 导入知识库"
  · 或者自己把文件放进 raw/ 目录后告诉我处理

支持的格式：.md .txt .csv .xlsx .docx .pptx .pdf .png .jpg 等

📎 推荐安装 Obsidian Web Clipper 浏览器插件：
  浏览网页时一键剪藏文章到 raw/articles/，下次对话我会自动检测并提醒导入。
  Chrome：https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf
  Firefox：https://addons.mozilla.org/en-US/firefox/addon/web-clipper-obsidian/

🎯 你还可以做这些事：
  · 查询知识库：直接问我问题，如"性能痛点的根因是什么？"、"女性玩家核心需求是什么？"
  · 健康检查：对我说"对知识库进行健康检查"
  · 用 Obsidian 浏览：打开 {{WIKI_PATH}} 查看完整知识图谱
```

---

## 故障排除

### qmd 编译失败

请重新执行步骤 3（编译 qmd），确保 `pnpm install` 和 TypeScript 编译成功：

```bash
cd <SKILL_PATH>/scripts/qmd
pnpm install --no-frozen-lockfile
npx tsc -p tsconfig.build.json
```

### 目录已存在

如果 `{{WIKI_PATH}}` 已存在，提示用户选择：
1. 继续（跳过已存在的目录，继续创建缺失的）
2. 选择新路径

### Windows 路径问题

Windows 用户注意：
- 使用 PowerShell 而非 CMD
- 路径分隔符使用 `\` 或 `/` 均可
- 桌面路径通常为 `C:\Users\<用户名>\Desktop\{{WIKI_NAME}}`

---

## 13. Schema 演进指南

> Schema.md 不是一成不变的。随着知识库的使用，用户应该与 LLM 协作演进它，使其越来越贴合自己的领域和工作方式。

### 何时演进 Schema

| 信号 | 建议调整 |
|------|---------|
| 发现现有 4 种页面类型不够用 | 新增自定义类型（如 `decisions/`、`experiments/`） |
| Frontmatter 字段不满足 Dataview 查询需求 | 添加新的元数据字段（如 `priority`、`status`） |
| Ingest 流程中某步骤对当前领域不适用 | 在 Schema.md 中标注跳过该步骤 |
| 同一类问题反复出现 | 在 Schema.md 中添加领域特定的处理规则 |
| 知识库超过 100 页 | 考虑细分子目录（如 entities/ 下按类型分组） |

### 演进示例

#### 示例 1：新增自定义页面类型

假设用户在做产品决策记录，需要 `decisions/` 类型：

1. 在 `wiki/` 下创建 `decisions/` 目录
2. 在 Schema.md 中添加：
   ```markdown
   ### decisions/（决策记录）
   记录关键的产品/技术决策及其上下文和影响。
   ```
3. 定义 frontmatter 模板：
   ```yaml
   type: decision
   status: proposed | accepted | deprecated
   impact: high | medium | low
   ```
4. 更新 `index.md` 中添加 `decisions/` 分类

#### 示例 2：添加新的 Frontmatter 字段

为所有页面添加 `confidence` 字段表示结论可信度：

```yaml
confidence: high | medium | low | unverified
```

然后用 Dataview 查询低可信度页面：

````markdown
```dataview
LIST
FROM "wiki"
WHERE confidence = "low" OR confidence = "unverified"
```
````

#### 示例 3：领域特定规则

如果知识库是"游戏用户研究"方向，可在 Schema.md 中添加：

```markdown
## 领域特定规则

### 满意度调研处理
- 满意度分数必须标注样本量和置信区间
- NPS 分数按照行业标准分类：推荐者(9-10)、被动者(7-8)、贬损者(0-6)
- 不同时期的调研结果必须标注调研时间，便于趋势对比

### 用户访谈处理
- 访谈对象必须记录：游戏时长、服务器、付费等级
- 直接引述原文时使用 `>` 引用格式
```

### 演进频率建议

- **每 10 次 ingest 后**：回顾 Schema.md，看是否有需要调整的规范
- **每次 lint 后**：根据发现的模式问题，考虑是否需要新增规则
- **切换研究主题时**：评估现有分类是否仍然适用
