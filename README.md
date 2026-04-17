# kb-wiki

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![node](https://img.shields.io/badge/node-%3E%3D22-brightgreen.svg)](https://nodejs.org)

**LLM 自动维护的持久化研究知识库 —— 你只负责提供资料和提问，LLM 负责构建整个 Wiki。**

> 基于 [llm-wiki](https://github.com/2811jh/kb-wiki) 理念 · 搭配 Obsidian 实时浏览 · 支持 Excel / Word / PPT / PDF

---

## 安装

### 方式一：Skills CLI（推荐）

```bash
npx skills add 2811jh/kb-wiki
```

### 方式二：手动安装

```bash
git clone https://github.com/2811jh/kb-wiki.git ~/.agents/skills/kb-wiki
```

### 安装后初始化

在 Claude / CodeMaker 对话中输入：

```
/setup
```

LLM 会自动引导你完成全部配置（环境检测 → 编译搜索引擎 → 创建知识库 → 下载 AI 模型）。

---

## 功能一览

| 命令 | 功能 | 说明 |
|------|------|------|
| `/setup` | 初始化知识库 | 创建目录结构、配置 qmd、生成 Schema.md |
| `/ingest <文件>` | 导入新资料 | 自动更新 10-15 个 wiki 页面 |
| `/query <问题>` | 查询知识库 | 混合搜索 + 综合答案 + 可选归档 |
| `/lint` | 健康检查 | 矛盾、孤立页面、缺失引用等 7 项检查 |
| `/status` | 查看状态 | 知识库统计 + qmd 索引状态 |

> 💡 也可以直接用自然语言，如"帮我导入这份报告"、"用户最大的痛点是什么？"

---

## 三层架构

```
your-wiki/
├── Schema.md        ← 规范层：告诉 LLM 如何工作（可自定义演进）
├── raw/             ← 原始资料层（只读）
│   ├── articles/       文章、访谈记录
│   ├── papers/         学术论文、研究报告
│   ├── assets/         图片等媒体文件
│   └── data/           数据文件（CSV、JSON）
└── wiki/            ← Wiki 层（LLM 完全掌控）
    ├── entities/       实体（用户、产品、组织）
    ├── concepts/       概念（痛点、行为模式）
    ├── sources/        资料摘要（每份资料一个）
    ├── synthesis/      综合分析（跨资料洞察）
    ├── index.md        内容目录
    └── log.md          操作日志（append-only）
```

**类比**：Obsidian = IDE，LLM = 程序员，Wiki = 代码库。

---

## 支持的文件格式

| 格式 | 扩展名 | 处理方式 |
|------|--------|---------|
| Markdown / 文本 | `.md` `.txt` `.csv` | 直接读取 |
| Excel | `.xlsx` `.xls` | 自动转 Markdown（需 Python） |
| Word | `.docx` | 自动转 Markdown（需 Python） |
| PowerPoint | `.pptx` | 自动转 Markdown（需 Python） |
| PDF | `.pdf` | 自动转 Markdown（需 Python） |
| 图片 | `.png` `.jpg` `.gif` `.webp` | LLM 视觉能力直接查看 |

> Python 为可选依赖（仅转换非文本文件时需要），`/setup` 时自动安装。

---

## 工作流

```
用户做的事（很少）              LLM 做的事（很多）
─────────────                 ────────────────
📁 把资料放进 raw/             📝 读取 → 理解 → 写 10-15 个 wiki 页面
❓ 问问题                      🔍 搜索 → 综合 → 生成带引用的答案
👀 在 Obsidian 中浏览          🔧 维护交叉引用、标注矛盾、修订结论
                              📊 定期健康检查 → 发现知识空白
```

### /ingest 示例

```
/ingest raw/articles/user-interview-2024-03.md
```

LLM 会自动：创建摘要页 → 更新实体页 → 更新概念页 → 标注矛盾 → 修订综合结论 → 更新索引 → 重建搜索

### /query 示例

```
/query 我们的用户在支付流程中最大的痛点是什么？
```

LLM 会：qmd 混合搜索 → 综合多来源 → 带引用的答案 → 可选归档到 synthesis/

### /lint 示例

```
/lint
```

输出：矛盾论断 · 孤立页面 · 缺失引用 · 过时内容 · 数据空白 · 建议行动

> 每导入 5 份资料后，LLM 会自动提醒运行 `/lint`。

---

## 与传统 RAG 的区别

| | 传统 RAG | kb-wiki |
|---|---|---|
| 知识形式 | 文档向量索引 | LLM 提炼的结构化 Wiki |
| 矛盾处理 | 原样返回冲突内容 | 标注并综合矛盾 |
| 知识增长 | 线性堆积 | 复利式增长（交叉引用强化） |
| 可读性 | 机器友好 | 人类可直接阅读 |
| 输入格式 | 纯文本/PDF | Markdown, Excel, Word, PPT, PDF, 图片 |

---

## 推荐工具

| 工具 | 用途 | 链接 |
|------|------|------|
| **Obsidian** | 实时浏览 wiki + 图谱视图 | [obsidian.md](https://obsidian.md) |
| **Web Clipper** | 浏览器文章一键剪藏 | [Chrome](https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf) / [Firefox](https://addons.mozilla.org/en-US/firefox/addon/web-clipper-obsidian/) |
| **Marp** | wiki 页面转幻灯片 | [Obsidian 插件](https://obsidian.md/plugins?id=marp-slides) |
| **Dataview** | frontmatter 动态查询 | [Obsidian 插件](https://obsidian.md/plugins?id=dataview) |
| **git** | 知识库版本控制 | [git-scm.com](https://git-scm.com/downloads) |

> qmd 搜索引擎（BM25 + 向量 + LLM 重排序）已内嵌在 skill 中，`/setup` 时自动编译，无需单独安装。

---

## 进阶用法

### Git 版本控制

```bash
cd ~/Desktop/your-wiki
git init && git add . && git commit -m "init: 知识库创建"
```

### qmd MCP 模式

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "kb-wiki": {
      "command": "qmd",
      "args": ["mcp"]
    }
  }
}
```

---

## 为什么有效

维护知识库最繁琐的不是思考——而是**簿记**：更新交叉引用、保持摘要最新、标注矛盾、在数十个页面间维护一致性。

**人类会放弃 wiki，因为维护负担的增长速度快于知识价值的增长速度。**

LLM 改变了这个等式——维护成本趋近于零，知识持续复利增长。

- 🧑 **人类**：策划来源、引导分析、提出正确的问题
- 🤖 **LLM**：其他一切

---

## 许可证

MIT © [2811jh](https://github.com/2811jh)