# Obsidian 集成指南

> 本文档帮助用户充分利用 Obsidian 浏览和管理 kb-wiki 知识库。

---

## 1. 基础配置

### 打开知识库

用 Obsidian 打开知识库**根目录**（包含 `Schema.md`、`raw/`、`wiki/` 的那个文件夹），而不是只打开 `wiki/` 子目录。这样可以在需要时直接浏览 raw/ 中的原始资料。

### 推荐设置

在 Obsidian 设置中调整以下选项：

| 设置项 | 路径 | 推荐值 | 原因 |
|--------|------|--------|------|
| 附件文件夹 | 设置 → 文件与链接 → 附件文件夹路径 | `raw/assets` | 图片统一存放 |
| 新建文件位置 | 设置 → 文件与链接 → 新建笔记存放位置 | 当前文件夹 | 避免文件散落根目录 |
| Wiki 链接 | 设置 → 文件与链接 → 使用 Wiki 链接 | ✅ 开启 | 支持 `[[]]` 语法 |

---

## 2. Obsidian Web Clipper

**用途**：在浏览器中看到有价值的文章时，一键剪藏为 Markdown 文件，直接保存到知识库的 `raw/articles/` 目录。

### 2.1 安装

| 浏览器 | 安装链接 |
|--------|---------|
| Chrome / Edge | [Chrome Web Store](https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf) |
| Firefox | [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/web-clipper-obsidian/) |
| Safari | Obsidian 桌面端内置，需在 设置 → 通用 → Web Clipper 中开启 |

安装后在浏览器工具栏会出现 Obsidian 图标。

### 2.2 连接到知识库

1. 打开 Obsidian，确保已打开知识库根目录（包含 `Schema.md` 的那个文件夹）
2. 点击浏览器中的 Web Clipper 图标
3. 首次使用会提示连接 Vault → 选择你的知识库
4. 连接成功后，图标会变为实心

### 2.3 配置剪藏模板（关键步骤）

在 Web Clipper 设置中创建一个 **kb-wiki 专用模板**，确保剪藏的文章自带结构化元数据：

**设置路径**：点击 Web Clipper 图标 → 右下角齿轮 ⚙️ → Templates → New template

**模板名称**：`kb-wiki`

**保存路径（Folder）**：

```
raw/articles
```

**文件名（File name）**：

```
{{title}}
```

**模板内容（Template）**：

````
---
title: "{{title}}"
date: {{date}}
source_url: "{{url}}"
author: "{{author|default:未知}}"
domain: "{{domain}}"
tags: [待分类]
clipped: true
---

# {{title}}

> 🔗 来源：[{{domain}}]({{url}})
> 📅 剪藏时间：{{date}}

{{content}}
````

> 💡 **`clipped: true` 标记很重要**：LLM 在 ingest 时会识别此标记，自动将文章作为"网络文章"类型处理，并在 sources/ 摘要页中记录原始 URL。

### 2.4 日常使用流程

```
① 浏览器中看到有价值的文章
      ↓
② 点击 Web Clipper 图标 → 选择 "kb-wiki" 模板 → 保存
      ↓
③ 文件自动保存到 raw/articles/文章标题.md
      ↓
④ 下次打开 LLM 对话时，LLM 会自动检测到新文件并提醒：
   "📎 发现 raw/articles/ 中有 2 篇新资料尚未导入，要我处理吗？"
      ↓
⑤ 确认后 LLM 自动批量 ingest → 知识库更新完成
```

> 你也可以随时主动说："帮我处理刚剪藏的文章"或 `/ingest raw/articles/文章标题.md`

### 2.5 图片本地化（推荐）

剪藏的文章中，图片默认是远程 URL。为防止链接失效，建议剪藏后立即本地化：

1. 在 Obsidian 设置 → 快捷键中，搜索 "Download"
2. 找到 **"Download attachments for current file"**，绑定快捷键（推荐 `Ctrl+Shift+D`）
3. 打开刚剪藏的文件，按快捷键 → 所有图片自动下载到 `raw/assets/`

> ⚠️ 如果不做图片本地化，原始 URL 可能在几个月后失效，导致图片丢失。

### 2.6 常见问题

**Q：剪藏后文件保存在哪了？**
A：如果模板配置正确，文件在 `知识库根目录/raw/articles/` 下。如果找不到，检查 Web Clipper 模板的 Folder 设置。

**Q：剪藏的内容格式很乱怎么办？**
A：Web Clipper 对部分网站的解析可能不完美。可以选择"简化文章"模式（Clipper 界面中的选项），或剪藏后在 Obsidian 中手动整理再 ingest。LLM 能处理格式不完美的 Markdown。

**Q：我一天剪藏了很多篇，怎么批量导入？**
A：下次打开 LLM 对话时会自动检测并提醒批量导入。也可以主动说"把 raw/articles/ 里的新文章都导入"。

**Q：剪藏的文章需要我自己分类吗？**
A：不需要！LLM 在 ingest 时会自动分析内容，创建对应的 entities/、concepts/ 页面，并归类到合适的主题下。你只需要剪藏，分类由 LLM 完成。

**Q：能剪藏需要登录才能看的文章吗？**
A：可以。Web Clipper 剪藏的是你当前浏览器中**已渲染**的页面内容，所以只要你能看到，就能剪藏。

> 💡 LLM 无法在一次 read_file 中读取内嵌图片。工作流是：LLM 先读文本内容，再单独查看 raw/assets/ 中的图片获取额外上下文。

---

## 3. 图谱视图（Graph View）

**用途**：可视化知识库的整体结构，发现关联和孤立页面。

### 打开方式

- 快捷键：`Ctrl+G`（全局图谱）
- 或：命令面板 → "Graph view: Open graph view"

### 阅读技巧

| 图谱特征 | 含义 | 行动建议 |
|---------|------|---------|
| 大节点（多连线） | 核心概念/实体，被多个页面引用 | 这些是知识库的枢纽，确保内容全面 |
| 孤立节点（无连线） | 缺少交叉引用的页面 | 执行 `/lint` 检查，补充关联 |
| 紧密连接的子簇 | 某个主题领域的知识聚合 | 考虑在 synthesis/ 中创建该主题的综合分析 |
| 两个子簇之间的桥接节点 | 连接不同领域的关键概念 | 重点关注，可能是跨域洞察的来源 |

### 过滤设置

- **推荐过滤**：隐藏 `raw/` 路径，只显示 `wiki/` 页面
- **颜色分组**：按文件夹着色（entities=蓝色, concepts=绿色, sources=灰色, synthesis=橙色）

> ⚠️ `index.md` 使用纯文本（非 `[[wiki-link]]`），因此不会在图谱中产生干扰性的星形连线。

---

## 4. Dataview 插件

**用途**：对页面 frontmatter 运行动态查询，生成自动更新的表格和列表。

### 安装

1. Obsidian 设置 → 第三方插件 → 浏览
2. 搜索 "Dataview" → 安装 → 启用

### 常用查询示例

#### 列出所有 sources/ 页面，按日期排序

````markdown
```dataview
TABLE title, date, tags
FROM "wiki/sources"
SORT date DESC
```
````

#### 列出所有包含"矛盾"标签的页面

````markdown
```dataview
LIST
FROM "wiki"
WHERE contains(tags, "矛盾")
```
````

#### 统计每个分类的页面数

````markdown
```dataview
TABLE length(rows) AS "页面数"
FROM "wiki"
GROUP BY split(file.folder, "/")[1] AS "分类"
```
````

#### 找出缺少 related 字段的页面（可能是孤立页面）

````markdown
```dataview
LIST
FROM "wiki"
WHERE !related OR length(related) = 0
```
````

> 💡 Dataview 查询可以放在 `wiki/synthesis/` 中作为动态仪表盘，实时反映知识库状态。

---

## 5. Marp 幻灯片

**用途**：将 Markdown 内容直接转换为演示幻灯片。

### 安装

1. Obsidian 插件商店搜索 "Marp Slides" → 安装 → 启用
2. 或使用独立工具：`npm install -g @marp-team/marp-cli`

### 使用方式

在 `/query` 时选择 "形式 C：Marp 幻灯片格式"，LLM 会生成带 `marp: true` 头部的 Markdown。在 Obsidian 中用 Marp 插件预览即可。

---

## 6. Git 版本管理

**用途**：知识库就是一个 Markdown 文件组成的 Git 仓库，天然支持版本历史。

### 推荐工作流

```bash
cd {{WIKI_PATH}}
git init
git add -A
git commit -m "initial: 知识库创建"
```

**后续每次 ingest 后**：

```bash
git add -A
git commit -m "ingest: 资料标题"
```

### Obsidian Git 插件

安装 "Obsidian Git" 插件可实现自动定时提交，无需手动操作。

| 设置 | 推荐值 |
|------|--------|
| 自动提交间隔 | 30 分钟 |
| 自动拉取 | 关闭（单人使用时） |
| 提交信息模板 | `auto: {{date}}` |