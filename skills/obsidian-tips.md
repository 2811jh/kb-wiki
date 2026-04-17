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

**用途**：将网页文章一键转换为 Markdown，快速收入 `raw/articles/`。

### 安装

1. 在浏览器扩展商店搜索 "Obsidian Web Clipper" 并安装
2. 配置 Vault 路径指向知识库根目录

### 使用工作流

1. 在浏览器中打开要保存的文章
2. 点击 Web Clipper 图标
3. 选择保存路径为 `raw/articles/`
4. 点击保存
5. 回到 LLM 对话，执行 `/ingest raw/articles/刚保存的文件.md`

### 图片本地化

剪藏文章后，图片默认是远程 URL。为防止链接失效：

1. 在 Obsidian 设置 → 快捷键中，搜索 "Download"
2. 找到 "Download attachments for current file"，绑定快捷键（推荐 `Ctrl+Shift+D`）
3. 打开刚剪藏的文件，按快捷键，所有图片自动下载到 `raw/assets/`

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