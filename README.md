# kb-wiki

[![npm version](https://img.shields.io/npm/v/kb-wiki.svg)](https://www.npmjs.com/package/kb-wiki)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![node](https://img.shields.io/badge/node-%3E%3D22-brightgreen.svg)](https://nodejs.org)
[![skills](https://img.shields.io/badge/skills-agentskills.io-purple.svg)](https://agentskills.io)

**LLM 自动维护的持久化研究知识库 skill —— 你只负责提供资料和提问，LLM 负责构建整个知识库。**

---

## 快速安装

```bash
# 第一步：安装 skills CLI（如未安装）
npm install -g skills

# 第二步：安装 kb-wiki skill
npx skills add 2811jh/kb-wiki

# 第三步：在 Claude 中初始化知识库
/setup
```

---

## 核心理念：llm-wiki 三层架构

kb-wiki 基于 [llm-wiki](https://github.com/2811jh/kb-wiki) 理念构建，将知识库分为三层：

```
your-wiki/
├── CLAUDE.md          ← Schema 层：告诉 LLM 如何工作（可自定义演进）
├── raw/               ← 原始资料层：只读，LLM 从这里读取来源
│   ├── articles/      ← 文章、访谈记录
│   ├── papers/        ← 学术论文
│   ├── assets/        ← 图片等媒体文件
│   └── data/          ← 数据文件
└── wiki/              ← Wiki 层：LLM 完全掌控，自动生成和维护
    ├── entities/      ← 用户、产品、组织等实体页面
    ├── concepts/      ← 用户痛点、行为模式等概念页面
    ├── sources/       ← 每份资料的摘要页面
    ├── synthesis/     ← 综合分析、洞察归档
    ├── index.md       ← 内容目录（每次 ingest 自动更新）
    └── log.md         ← 操作日志（append-only）
```

**类比**：Obsidian = IDE，LLM = 程序员，Wiki = 代码库。你打开 Obsidian 实时浏览，LLM 在后台编辑维护。

---

## 功能一览

| 命令 | 功能 | 说明 |
|------|------|------|
| `/setup` | 初始化知识库 | 创建目录结构、配置 qmd、生成 CLAUDE.md |
| `/ingest <文件或内容>` | 导入新资料 | 自动更新 10-15 个 wiki 页面 |
| `/query <问题>` | 查询知识库 | 混合搜索 + 综合答案 + 可选归档 |
| `/lint` | 健康检查 | 检测矛盾、孤立页面、缺失引用等 7 项 |
| `/status` | 查看状态 | 显示知识库统计和 qmd 索引状态 |

---

## 首次使用：/setup 流程

运行 `/setup` 后，LLM 将引导你完成：

1. ✅ 检测 Node.js 版本（需 >= 22）
2. 📦 安装 qmd 搜索引擎（`npm install -g @tobilu/qmd`）
3. 📝 输入知识库名称（如：`ux-research`）
4. 📂 选择知识库位置（默认桌面，或自定义路径）
5. 🏗️ 自动创建完整目录结构
6. ⚙️ 生成 `CLAUDE.md` Schema 文件
7. 🔗 配置 qmd 集合（`qmd collection add`）
8. 🎉 输出欢迎信息和使用指南

---

## 核心工作流示例

### 导入资料（Ingest）

```
# 将文章放入 raw/articles/，然后告诉 LLM：
/ingest raw/articles/user-interview-2024-03.md

# LLM 会自动：
# ✓ 读取并理解资料
# ✓ 在 wiki/sources/ 创建摘要页面
# ✓ 更新 wiki/entities/ 中相关用户页面
# ✓ 更新 wiki/concepts/ 中相关概念页面
# ✓ 检查并标注与现有内容的矛盾
# ✓ 强化或修订 wiki/synthesis/ 中的综合结论
# ✓ 更新 wiki/index.md
# ✓ 在 wiki/log.md 追加记录
# ✓ 运行 qmd update 重建索引
```

### 查询知识库（Query）

```
/query 我们的用户在支付流程中最大的痛点是什么？

# LLM 会：
# ✓ 用 qmd 搜索相关页面
# ✓ 综合多个来源给出答案（带引用）
# ✓ 询问是否将洞察归档到 synthesis/
```

### 健康检查（Lint）

```
/lint

# LLM 输出报告，包含：
# ✓ 矛盾论断（如：A 说用户不在意价格，B 说价格是首要因素）
# ✓ 孤立页面（没有入站链接的页面）
# ✓ 缺失交叉引用
# ✓ 过时论断
# ✓ 数据空白建议
# ✓ 推荐探索方向
```

> 💡 每导入 5 份资料后，LLM 会自动提醒你运行 `/lint`。

---

## 推荐工具链

| 工具 | 用途 | 安装 |
|------|------|------|
| **Obsidian** | 实时浏览 wiki，图谱视图可视化页面关联结构 | [obsidian.md](https://obsidian.md) |
| **Obsidian Web Clipper** | 浏览器文章一键转 Markdown | Chrome/Firefox 扩展 |
| **qmd** | 本地 Markdown 搜索引擎（BM25 + 向量） | `npm install -g @tobilu/qmd` |
| **Marp** | 将 wiki 页面转为幻灯片 | Obsidian 插件 |
| **Dataview** | Obsidian 中查询 wiki 数据 | Obsidian 插件 |
| **git** | 知识库版本控制 | `git init` 在知识库根目录 |

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
