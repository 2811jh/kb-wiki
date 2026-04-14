# qmd 工具完整参考

> qmd 是 kb-wiki 的本地 Markdown 搜索引擎，支持 BM25 全文搜索、向量语义搜索和混合搜索。
> 提供 CLI 命令行工具和 MCP server 两种使用模式。

---

## 安装

```bash
# 安装（需要 Node.js >= 22）
npm install -g @tobilu/qmd

# 验证安装
qmd --version

# 更新到最新版本
npm update -g @tobilu/qmd
```

---

## 三种搜索命令对比

| 命令 | 搜索方式 | 速度 | 质量 | 适用场景 |
|------|---------|------|------|---------|
| `qmd search` | BM25 全文检索 | ⚡ 最快 | 中 | 搜索精确术语、人名、产品名 |
| `qmd vsearch` | 向量语义搜索 | 🔄 中等（需嵌入） | 高 | 搜索概念、问题、模糊描述 |
| `qmd query` | 混合搜索+重排+扩展 | 🔄 中等 | 最高 | 大多数研究问题的推荐选择 |

### search - BM25 全文搜索

```bash
# 基础搜索
qmd search "支付流程"

# 指定集合
qmd search "支付流程" --collection ux-research

# 限制结果数量
qmd search "支付流程" --top 10

# 搜索特定目录
qmd search "用户-A" --collection ux-research --path entities/
```

**何时使用**：搜索已知的精确术语、人名、功能名、引述关键词时使用。

### vsearch - 向量语义搜索

```bash
# 基础语义搜索（需要先运行 qmd embed）
qmd vsearch "用户在付款时遇到的阻碍"

# 指定集合
qmd vsearch "界面设计让用户感到困惑" --collection ux-research

# 调整结果数量
qmd vsearch "用户痛点" --top 5
```

**何时使用**：当查询是描述性的、概念性的，或不确定确切关键词时使用。

### query - 混合搜索（推荐）

```bash
# 标准混合搜索（推荐）
qmd query "支付流程的用户痛点有哪些"

# 带重排序（质量最高）
qmd query "支付流程痛点" --rerank

# 指定集合
qmd query "竞品功能对比" --collection ux-research

# 指定搜索类型
qmd query "支付痛点" --type lex    # 仅词法搜索
qmd query "支付痛点" --type vec    # 仅向量搜索
qmd query "支付痛点" --type hyde   # HYDE 假设文档扩展

# 跨多个集合搜索
qmd query "用户体验" --collections ux-research,product-wiki
```

**何时使用**：绝大多数查询场景的推荐选择，综合精度和语义理解。

---

## 文档获取命令

### get - 获取单个文档

```bash
# 获取完整文档
qmd get wiki/concepts/支付流程痛点.md

# 通过文档 ID 获取
qmd get #12

# 获取指定行范围（从第 50 行开始，读取 100 行）
qmd get wiki/concepts/支付流程痛点.md:50 -l 100

# 仅返回 frontmatter
qmd get wiki/entities/用户-A.md --frontmatter
```

### multi-get - 批量获取文档

```bash
# 逗号分隔多个文件
qmd multi-get "wiki/concepts/支付流程痛点.md,wiki/entities/用户-A.md"

# Glob 模式批量获取
qmd multi-get "wiki/entities/*.md"
qmd multi-get "wiki/sources/用户访谈-*.md"

# 获取某目录下所有文件
qmd multi-get "wiki/synthesis/**"
```

---

## 文件列表命令

### ls - 列出集合中的文件

```bash
# 列出当前集合所有文件
qmd ls

# 列出指定集合
qmd ls --collection ux-research

# 列出特定路径
qmd ls wiki/entities/

# 按修改时间排序
qmd ls --sort modified
```

---

## 集合管理命令

集合（Collection）是 qmd 管理多个 Markdown 目录的方式。每个知识库对应一个集合。

### collection add - 添加集合

```bash
# 添加知识库 wiki/ 目录为集合
qmd collection add /path/to/your-wiki/wiki --name ux-research

# Windows 路径
qmd collection add "C:\Users\name\Desktop\ux-research\wiki" --name ux-research
```

### collection list - 列出所有集合

```bash
qmd collection list

# 输出示例：
# ux-research -> /Users/name/Desktop/ux-research/wiki
# product-wiki -> /Users/name/Documents/product-wiki/wiki
```

### collection remove - 删除集合

```bash
qmd collection remove ux-research
```

### collection rename - 重命名集合

```bash
qmd collection rename ux-research ux-research-2024
```

### collection include / exclude - 过滤文件

```bash
# 只索引 wiki/ 目录（排除 raw/）
qmd collection include ux-research "wiki/**"

# 排除特定文件
qmd collection exclude ux-research "wiki/log.md"
qmd collection exclude ux-research "wiki/index.md"  # 通常不需要被搜索
```

---

## 索引管理命令

### update - 重建索引

```bash
# 重建默认集合的索引
qmd update

# 重建特定集合
qmd update --collection ux-research

# 从远程 pull 并重建（git 集成）
qmd update --pull
```

**何时运行**：每次 `/ingest` 后自动运行，或手动添加文件后运行。

### embed - 生成向量嵌入

```bash
# 为当前集合生成向量嵌入（vsearch 和 query --type vec/hyde 需要）
qmd embed

# 强制重新生成（覆盖现有嵌入）
qmd embed -f

# 使用 AST 感知分块策略（推荐，更好地处理 Markdown 结构）
qmd embed --chunk-strategy auto

# 指定集合
qmd embed --collection ux-research
```

**何时运行**：首次设置时运行一次，之后每次大量 ingest 后运行以更新语义索引。

### status - 查看索引状态

```bash
qmd status

# 输出示例：
# 集合：ux-research
# 路径：/Users/name/Desktop/ux-research/wiki
# 文件数：45
# 最后更新：2024-03-20 14:30:00
# 向量索引：已生成（2024-03-19）
# BM25 索引：已生成（2024-03-20）
```

### cleanup - 清理缓存

```bash
# 清理过时的索引缓存
qmd cleanup
```

---

## 上下文管理命令

上下文（Context）允许将常用文档预加载到 LLM 上下文中。

```bash
# 添加上下文文档
qmd context add wiki/index.md

# 列出当前上下文
qmd context list

# 删除上下文
qmd context rm wiki/index.md
```

**kb-wiki 推荐配置**：将 `index.md` 加入上下文，每次对话开始时自动可见。

```bash
qmd context add "{{WIKI_PATH}}/wiki/index.md"
```

---

## MCP Server 使用

qmd 可以作为 MCP (Model Context Protocol) server 运行，直接集成到 Claude Desktop 等支持 MCP 的客户端。

### 启动 MCP Server（Stdio 模式）

```bash
# 启动 stdio MCP server（Claude Desktop 默认使用此模式）
qmd mcp
```

### Claude Desktop 配置

在 Claude Desktop 配置文件中添加（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

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

Windows 配置文件位置：`%APPDATA%\Claude\claude_desktop_config.json`

### HTTP 模式 MCP Server

适合需要持久运行的场景（如多个客户端共享）：

```bash
# 前台运行 HTTP 模式（默认端口 8080）
qmd mcp --http

# 指定端口
qmd mcp --http --port 9090

# 后台 daemon 模式运行
qmd mcp --http --daemon

# 停止 daemon
qmd mcp stop
```

HTTP 模式端点：`http://localhost:8080/mcp`

---

## MCP Server 的 4 个工具

当 qmd 以 MCP server 模式运行时，提供以下 4 个工具：

### 1. query - 主搜索工具

```json
{
  "tool": "query",
  "params": {
    "q": "支付流程用户痛点",
    "type": "hybrid",      // lex | vec | hyde
    "rerank": true,        // 是否重排序
    "top": 5,              // 返回结果数
    "collections": ["ux-research"]  // 指定集合
  }
}
```

**三种搜索类型**：

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `lex` | BM25 词法搜索 | 精确关键词，速度优先 |
| `vec` | 向量语义搜索 | 语义相似，概念搜索 |
| `hyde` | 假设文档扩展 | 探索性问题，质量优先 |

默认使用混合搜索（lex + vec）。

### 2. get - 文档检索工具

```json
{
  "tool": "get",
  "params": {
    "path": "wiki/concepts/支付流程痛点.md",
    // 或使用 docid:
    "docid": 12,
    // 可选：行范围
    "offset": 50,
    "limit": 100
  }
}
```

### 3. multi_get - 批量文档检索工具

```json
{
  "tool": "multi_get",
  "params": {
    "pattern": "wiki/entities/*.md"
    // 或逗号分隔:
    // "paths": "wiki/concepts/A.md,wiki/concepts/B.md"
  }
}
```

### 4. status - 索引状态工具

```json
{
  "tool": "status",
  "params": {
    "collection": "ux-research"  // 可选，不填则返回所有集合
  }
}
```

---

## kb-wiki 场景下的集合管理最佳实践

### 推荐配置：单知识库单集合

```bash
# 初始设置（在 /setup 时执行）
qmd collection add "~/Desktop/ux-research/wiki" --name ux-research

# 排除不需要搜索的系统文件（可选）
qmd collection exclude ux-research "wiki/.obsidian/**"

# 建立初始索引
qmd update --collection ux-research

# 建立向量索引（可选，用于语义搜索）
qmd embed --collection ux-research --chunk-strategy auto
```

### 多知识库管理

```bash
# 添加多个知识库
qmd collection add "~/Desktop/ux-research/wiki" --name ux-research
qmd collection add "~/Desktop/product-wiki/wiki" --name product-wiki

# 列出所有集合
qmd collection list

# 跨知识库搜索
qmd query "用户体验" --collections ux-research,product-wiki
```

### 定期维护

```bash
# 每次 ingest 后（自动执行）
qmd update --collection ux-research

# 每周重建向量索引
qmd embed -f --collection ux-research

# 清理缓存（可选，每月一次）
qmd cleanup
```

---

## 常见问题

### vsearch 结果为空

原因：尚未生成向量嵌入。

```bash
qmd embed --collection ux-research
```

### 搜索结果不准确

尝试：

1. 使用 `--rerank` 提升精度：`qmd query "关键词" --rerank`
2. 切换搜索类型：`qmd query "关键词" --type vec`
3. 重建索引：`qmd update -f --collection ux-research`

### MCP server 连接失败

1. 确认 qmd 已安装：`qmd --version`
2. 确认 Claude Desktop 配置文件路径正确
3. 重启 Claude Desktop

### Windows 路径问题

在 Windows 上使用引号包裹路径，并使用正斜杠或双反斜杠：

```bash
qmd collection add "C:/Users/name/Desktop/ux-research/wiki" --name ux-research
# 或
qmd collection add "C:\\Users\\name\\Desktop\\ux-research\\wiki" --name ux-research
```
