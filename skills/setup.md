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

---

### 步骤 2：安装并编译 qmd 搜索引擎

qmd 的完整源码已内嵌在 skill 的 `scripts/qmd/` 目录中，但首次使用需要安装依赖并编译。

**自动执行以下命令**（LLM 直接执行，无需用户操作）：

```bash
# 2.1 检测 pnpm 是否可用
pnpm --version
# 如果 pnpm 不可用，先安装：
npm install -g pnpm

# 2.2 进入 qmd 目录安装依赖
cd <skill安装路径>/scripts/qmd
pnpm install --no-frozen-lockfile

# 2.3 编译 TypeScript
npx tsc -p tsconfig.build.json

# 2.4 验证编译成功
node dist/cli/qmd.js --version
```

> ⚠️ 注意：`<skill安装路径>` 是 `npx skills add` 安装 skill 到本地的路径。LLM 应自动检测此路径（通常在 `~/.skills/` 或 `.agents/skills/` 下）。

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
node <skill安装路径>/scripts/qmd/dist/cli/qmd.js <命令> [参数]

# 例如：
node <skill安装路径>/scripts/qmd/dist/cli/qmd.js query "用户痛点"
node <skill安装路径>/scripts/qmd/dist/cli/qmd.js update
node <skill安装路径>/scripts/qmd/dist/cli/qmd.js collection list
node <skill安装路径>/scripts/qmd/dist/cli/qmd.js embed
```

> 💡 LLM 应在 setup 完成后记住 qmd 的完整调用路径，后续 ingest/query 时直接使用。

### 步骤 2.5：配置 HuggingFace 镜像（中国大陆用户）

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
也可以用 `qmd pull` 命令预先下载所有模型。
```

---

### 步骤 3：询问知识库名称

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

### 步骤 4：询问知识库位置

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

### 步骤 5：创建目录结构

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
```

---

### 步骤 6：复制并填充 CLAUDE.md 模板

读取 skill 包中的 `templates/CLAUDE.md.template`，将以下占位符替换：

| 占位符 | 替换为 |
|--------|--------|
| `{{WIKI_NAME}}` | 用户输入的知识库名称 |
| `{{WIKI_PATH}}` | 知识库完整路径 |
| `{{CURRENT_DATE}}` | 当前日期（格式：YYYY-MM-DD） |

将结果写入 `{{WIKI_PATH}}/CLAUDE.md`。

---

### 步骤 7：创建 index.md

在 `{{WIKI_PATH}}/wiki/index.md` 写入：

```markdown
# {{WIKI_NAME}} 知识库索引

> 最后更新：{{CURRENT_DATE}}
> 总页面数：0 | sources: 0 | entities: 0 | concepts: 0 | synthesis: 0

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

### 步骤 8：创建 log.md

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

### 步骤 9：配置 qmd 集合

如果 qmd 已安装，执行：

```bash
qmd collection add "{{WIKI_PATH}}/wiki" --name "{{WIKI_NAME}}"
qmd collection list
qmd update
```

预期输出：
```
✅ 已添加集合 "{{WIKI_NAME}}" -> {{WIKI_PATH}}/wiki
已重建索引（0 个文件，2 个系统文件）
```

---

### 步骤 10：输出欢迎信息

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
  CLAUDE.md       ← 知识库规范（可自定义）

🚀 下一步：
  1. 将第一份资料放入 raw/articles/
  2. 运行 /ingest raw/articles/你的文件.md
  3. 用 Obsidian 打开 {{WIKI_PATH}} 实时浏览知识库

💡 推荐：安装 Obsidian（https://obsidian.md）并打开此知识库目录，
   你将能实时看到 LLM 构建的知识图谱。
```

---

## 故障排除

### qmd 安装失败

```bash
# 检查 npm 版本
npm --version

# 清理 npm 缓存后重试
npm cache clean --force
npm install -g @tobilu/qmd
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
