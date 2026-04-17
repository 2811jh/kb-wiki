# Ingest 工作流：导入新资料

> 本文档供 LLM 执行 `/ingest` 命令时参考。每次导入新资料时完整执行以下 10 步流程。

---

## 触发方式

```
/ingest raw/articles/user-interview-2024-03.md
/ingest raw/papers/ux-heuristics-nielsen.pdf
/ingest raw/data/survey-results.xlsx
/ingest raw/articles/竞品分析报告.docx
/ingest（然后用户粘贴文本内容）
```

### 批量导入

```
/ingest raw/articles/             ← 导入整个目录（LLM 逐一处理每份资料）
/ingest raw/articles/*.md         ← 导入目录下所有 Markdown 文件
```

批量导入时，LLM 会逐一处理每份资料，跳过讨论环节以加快速度。每份资料仍然独立执行完整的 10 步工作流（写摘要、更新实体、标注矛盾等），但减少与用户的中间交互，适合一次性导入大量资料。用户可以事后集中审阅更新内容。

---

## 完整流程（10 步）

### 步骤 1：检测文件格式 + 读取原始资料

**首先检测文件扩展名**，根据格式决定处理方式：

| 扩展名 | 处理方式 | 说明 |
|--------|---------|------|
| `.md`, `.txt`, `.csv` | **直接读取** | LLM 可直接 `read_file` |
| `.xlsx`, `.xls` | **自动转换** → 读取 | 调用 `convert_xlsx.py` |
| `.docx` | **自动转换** → 读取 | 调用 `convert_docx.py` |
| `.pptx` | **自动转换** → 读取 | 调用 `convert_pptx.py` |
| `.pdf` | **自动转换** → 读取 | 调用 `convert_pdf.py` |
| `.png`, `.jpg`, `.gif`, `.webp` | **LLM 视觉** | 直接查看图片内容 |
| `.doc`, `.ppt` | **提示用户** | 建议另存为新格式（.docx/.pptx） |

#### 文本格式（直接读取）

```bash
# .md / .txt / .csv 直接读取
cat "{{WIKI_PATH}}/raw/articles/user-interview-2024-03.md"
```

#### 非文本格式（自动转换后读取）

```bash
# 1. 确保缓存目录存在
mkdir -p "{{WIKI_PATH}}/wiki/.cache"

# 2. 调用对应转换脚本（以 Excel 为例）
python <SKILL_PATH>/scripts/convert/convert_xlsx.py \
    "{{WIKI_PATH}}/raw/data/Q1.xlsx" \
    "{{WIKI_PATH}}/wiki/.cache/Q1.xlsx.md" \
    --images-dir "{{WIKI_PATH}}/raw/assets"

# 3. 读取转换后的 Markdown
cat "{{WIKI_PATH}}/wiki/.cache/Q1.xlsx.md"
```

**转换脚本路由表**：

```bash
# Excel
python <SKILL_PATH>/scripts/convert/convert_xlsx.py <输入> <输出.md> --images-dir <WIKI_PATH>/raw/assets

# Word
python <SKILL_PATH>/scripts/convert/convert_docx.py <输入> <输出.md> --images-dir <WIKI_PATH>/raw/assets

# PowerPoint
python <SKILL_PATH>/scripts/convert/convert_pptx.py <输入> <输出.md> --images-dir <WIKI_PATH>/raw/assets

# PDF
python <SKILL_PATH>/scripts/convert/convert_pdf.py <输入> <输出.md> --images-dir <WIKI_PATH>/raw/assets
```

> 💡 转换脚本的 Python 依赖在 `/setup` 阶段已安装。如果运行报错 `ModuleNotFoundError`，请执行：
> `pip install -r <SKILL_PATH>/scripts/convert/requirements.txt`

#### 图片格式

对于 `.png`, `.jpg`, `.gif`, `.webp` 格式的图片，直接使用 LLM 的视觉能力查看图片内容，将观察到的信息作为资料来源进行 ingest。

#### 不支持的旧格式

对于 `.doc`, `.ppt` 等旧格式，告知用户：
```
⚠️ 检测到旧版 Office 格式（.doc/.ppt），无法直接转换。
请在 Microsoft Office 中「另存为」新格式（.docx/.pptx），然后重新 ingest。
```

---

**读取完成后，确认要点**：
- 确认资料类型（访谈、文章、论文、报告、数据等）
- 确认主要主题（涉及哪些用户、产品、概念）
- 提取关键信息点（主要发现、引述、数据）

---

### 步骤 2：与用户讨论关键要点（可选，视情况而定）

如果资料内容较复杂或存在歧义，可以先与用户确认：

```
我读取了《用户访谈 - 2024年3月》，发现以下关键要点：
1. 用户 A（28岁，设计师）反映支付流程需要 3 步，感觉繁琐
2. 用户 B（35岁，产品经理）对新增的"快捷支付"功能表示认可
3. 两位用户都提到了"加载速度"问题

这份资料将被归类为：用户访谈（entities: 用户A、用户B；concepts: 支付流程、快捷支付、加载速度）
是否有需要特别关注的方面？
```

---

### 步骤 3：在 wiki/sources/ 写摘要页面

在 `{{WIKI_PATH}}/wiki/sources/` 创建新页面，文件名采用**中文描述 + 英文 slug** 格式（如 `汕头服务器访谈shantou-server-week1.md`）。

**页面格式规范**：

```markdown
---
title: 用户访谈 - 2024年3月
date: 2024-03-15
tags: [用户访谈, 支付流程, 移动端]
sources: [raw/articles/user-interview-2024-03.md]
related: [entities/用户-A, entities/用户-B, concepts/支付流程, concepts/加载速度]
---

# 用户访谈 - 2024年3月

## 来源信息
- **原始文件**：`raw/articles/user-interview-2024-03.md`
- **日期**：2024-03-15
- **类型**：用户访谈
- **访谈对象**：[[用户-A]]（28岁，设计师），[[用户-B]]（35岁，产品经理）

## 核心发现

### 支付流程体验
- 用户 A 认为支付流程"需要 3 步，感觉繁琐"（原文引述）
- 用户 B 对[[快捷支付]]功能表示认可，认为"确实方便了很多"

### 性能问题
- 两位用户均提到[[加载速度]]问题，尤其在网络较差时明显
- 用户 A："有时候点了没反应，以为没成功又点了一次"

## 关键引述

> "支付这块还是太麻烦了，我每次都要找半天才能确认付款。" —— 用户 A

> "新的快捷支付挺好用的，就是加载有点慢。" —— 用户 B

## 与现有知识的关联

- 强化了 [[concepts/支付流程]] 中关于"步骤数量"的用户反馈
- 与 [[sources/用户访谈-2024-01]] 中的发现一致：加载速度是持续性问题

> ⚠️ **矛盾**：本次访谈用户 B 认可快捷支付，但 [[sources/竞品分析-2024-02]] 中指出竞品的快捷支付因安全顾虑而用户接受度较低。需要进一步研究用户对安全性的态度。

## 综合意义

> 💡 **综合结论**：支付流程优化需要同时关注步骤数量和加载性能，两者相互影响用户感知。快捷支付是正确方向，但需解决性能问题。
```

---

### 步骤 4：更新 wiki/index.md

在 `index.md` 中添加新页面的条目。

> ⚠️ **index.md 禁止使用 `[[wiki-link]]`**，必须使用纯文本列表。
> 原因：`[[]]` 会让 index.md 成为 Obsidian 图谱的星形中心，掩盖页面间真正的关联。

**格式规范**（每行）：
```
- 页面名 – 一行摘要
```

**示例**：
```markdown
## sources/（资料摘要）

- 用户访谈2024-03user-interview-2024-03 – 2位用户对支付流程和加载速度的反馈
- 用户访谈2024-01user-interview-2024-01 – 首次深度访谈，发现导航痛点
- 竞品分析2024-02competitor-analysis-2024-02 – 3个竞品支付流程对比分析
```

同时更新页面统计数字：
```
> 最后更新：{{CURRENT_DATE}} | 页面总数：12（sources: 3 | entities: 5 | concepts: 4 | synthesis: 0）
```

---

### 步骤 5：更新相关 entities/ 页面

遍历本次资料中提到的实体（用户、产品、组织），逐一更新或创建对应页面。

**典型需要更新的实体类型**：
- 用户人物（如：`wiki/entities/用户-A.md`）
- 产品功能（如：`wiki/entities/快捷支付功能.md`）
- 竞品（如：`wiki/entities/竞品-微信支付.md`）

**实体页面格式规范**：

```markdown
---
title: 用户-A
date: 2024-03-15（最后更新日期）
tags: [用户, 设计师, 移动端]
sources: [sources/用户访谈-2024-03, sources/用户访谈-2024-01]
related: [concepts/支付流程, concepts/加载速度]
---

# 用户-A

## 基本信息
- **年龄**：28 岁
- **职业**：设计师
- **设备偏好**：iOS 用户

## 核心观点和行为

### 支付体验
- 认为支付步骤过多（[[sources/用户访谈-2024-03]]）
- 遇到过因加载慢而重复点击的情况

### 功能偏好
- 对新功能持谨慎态度，倾向于已验证的流程

## 来源资料
- [[sources/用户访谈-2024-03]]（2024-03-15）
- [[sources/用户访谈-2024-01]]（2024-01-10）
```

---

### 步骤 6：更新相关 concepts/ 页面

遍历本次资料中涉及的概念（痛点、行为模式、设计模式），逐一更新或创建页面。

**典型需要更新的概念类型**：
- 用户痛点（如：`wiki/concepts/支付流程痛点.md`）
- 行为模式（如：`wiki/concepts/重复点击行为.md`）
- 设计概念（如：`wiki/concepts/快捷支付.md`）

**概念页面格式规范**：

```markdown
---
title: 支付流程痛点
date: 2024-03-15（最后更新）
tags: [痛点, 支付, 用户体验]
sources: [sources/用户访谈-2024-03, sources/用户访谈-2024-01]
related: [entities/用户-A, entities/用户-B, concepts/加载速度, synthesis/支付优化建议]
---

# 支付流程痛点

## 当前认知（基于 2 份资料）

用户普遍反映支付流程过于繁琐，主要表现在步骤数量多和加载速度慢两个维度。

> 💡 **综合结论**：支付痛点是**多维度的**，单纯减少步骤不足以解决问题，
>  性能优化同等重要。（综合 [[sources/用户访谈-2024-03]] 和 [[sources/用户访谈-2024-01]]）

## 具体表现

### 步骤数量
- 用户 A 反映需要 3 步确认付款（[[sources/用户访谈-2024-03]]）

### 加载速度
- 两位访谈用户均提到（[[sources/用户访谈-2024-03]]）
- 与 2024-01 的问题持续存在（[[sources/用户访谈-2024-01]]）

> ⚠️ **矛盾**：[[sources/竞品分析-2024-02]] 显示竞品用户对快捷支付安全性存疑，
>  但我们的用户对此未明确表达担忧。安全性态度的差异原因待研究。

## 资料来源
- [[sources/用户访谈-2024-03]]（2024-03-15）：2 位用户直接反馈
- [[sources/用户访谈-2024-01]]（2024-01-10）：首次发现此问题
```

---

### 步骤 7：检查矛盾，在页面中标注

在处理过程中，对比本次资料与现有 wiki 内容：

**矛盾检测方法**：
1. 搜索相关概念页面，找到与本次资料不一致的论断
2. 用 `qmd query "相关关键词"` 快速检索

**矛盾标注格式**（在相关页面中添加）：

```markdown
> ⚠️ **矛盾**：[[sources/资料A]] 认为 X，但 [[sources/资料B]] 显示 Y。
> 可能原因：[假设]。建议通过 [方式] 进一步验证。
```

**常见矛盾类型**：
- 同一用户群体的不同看法
- 不同时间段数据的变化
- 定性访谈与定量数据的不一致
- 竞品对比结果与内部数据矛盾

---

### 步骤 8：强化或修订综合结论

查看 `wiki/synthesis/` 中相关页面，根据本次资料：

1. **强化**：如果新证据支持现有结论，在页面中添加引用，更新置信度
2. **修订**：如果新证据挑战现有结论，修订论断并说明原因
3. **新建**：如果涌现出新的值得归档的洞察，创建新的 synthesis 页面

**综合结论更新示例**：

```markdown
## 支付流程优化方向（置信度：高）

> 💡 **综合结论**：基于 3 次访谈，支付流程优化需要"步骤简化"和"性能提升"双管齐下。
> 单一优化效果有限。
>
> **来源支撑**：
> - [[sources/用户访谈-2024-03]]：步骤多 + 加载慢
> - [[sources/用户访谈-2024-01]]：步骤多（加载未提及）
> - [[sources/竞品分析-2024-02]]：竞品以快捷支付为突破口
>
> **上次修订**：2024-03-15（新增加载性能维度）
```

---

### 步骤 9：在 log.md 追加记录

在 `{{WIKI_PATH}}/wiki/log.md` 末尾**追加**一条记录：

```markdown
## [YYYY-MM-DD] ingest | 资料标题

- 来源文件：`raw/articles/文件名.md`
- 更新页面：sources/资料摘要页（新建）、entities/用户-A（更新）、entities/用户-B（更新）、concepts/支付流程痛点（更新）
- 新增矛盾标注：1 处
- 修订综合结论：1 处
```

**格式说明**：
- `## [YYYY-MM-DD]` 必须是行首，支持 `grep "^## \[" log.md` 解析
- 标题使用资料的实际标题
- 记录实际更新的页面列表

---

### 步骤 10：重建 qmd 索引 + 更新向量嵌入 + 检查是否触发 Lint 提醒

**重建 BM25 索引**：

```bash
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js update
```

> 注意：`qmd update` 会更新所有已注册集合的索引，这是正常行为。

**更新向量嵌入索引**（确保 `/query` 时语义搜索覆盖到本次新增的页面）：

```bash
# 对所有新增/修改的页面生成向量嵌入（增量，仅处理变更页面）
node <SKILL_PATH>/scripts/qmd/dist/cli/qmd.js embed
```

> 💡 **说明**：`qmd embed` 只会处理自上次 embed 后新增/变更的页面（增量更新），不会重复处理已有页面，速度很快。
> AI 模型已在 `/setup` 步骤 9.5 中预下载，此处直接使用，无需等待。
> 如果 `/setup` 时跳过了模型下载，首次 `embed` 会触发自动下载（约 1.3GB），耗时较长。

**统计 ingest 次数，判断是否触发 Lint 提醒**：

读取 `log.md`，找到最后一次 `lint` 记录之后的 `ingest` 记录数量：

```bash
# 统计距上次 lint 的 ingest 次数
grep "^## \[" "{{WIKI_PATH}}/wiki/log.md" | grep -v "setup" > /tmp/log_entries.txt
# 从末尾向前找，统计 lint 之前的 ingest 数
```

**逻辑**：
```
ingest_since_last_lint = 从 log.md 末尾开始数，遇到 lint 记录停止，统计 ingest 记录数
如果 ingest_since_last_lint >= 5：
    在本次回复末尾追加 Lint 提醒
```

**Lint 提醒格式**：

```
---
💡 **知识库健康提醒**：你已经导入了 5 份新资料（自上次健康检查以来）。
建议运行 `/lint` 检查知识库健康状态，包括：矛盾论断、孤立页面、过时内容、缺失交叉引用等。
定期健康检查能保持知识库的质量和一致性。
---
```

---

## 完成后汇报

每次 ingest 完成后，向用户汇报：

```
✅ 导入完成：《资料标题》

📝 更新了以下 wiki 页面（共 N 个）：

新建页面：
  - wiki/sources/用户访谈-2024-03.md

更新页面：
  - wiki/entities/用户-A.md（新增 2024-03 访谈内容）
  - wiki/entities/用户-B.md（新建）
  - wiki/concepts/支付流程痛点.md（新增来源，更新综合结论）
  - wiki/concepts/加载速度.md（新增 2 条引述）
  - wiki/index.md（已更新）
  - wiki/log.md（已追加记录）

🔍 发现：
  - 矛盾标注：1 处（快捷支付安全性态度差异）
  - 修订综合结论：1 处（支付优化双维度论断）

📊 知识库状态：sources: 3 | entities: 5 | concepts: 7 | synthesis: 0
```

---

## 文件命名规范

Wiki 页面文件名采用**中文描述 + 英文 slug** 的格式，便于在 Obsidian 关系图谱中直观识别：

**格式**：`中文名称英文slug.md`

**示例**：
- `服务器产品特征server-features.md`（概念页）
- `基岩版玩家minecraft-bedrock.md`（实体页）
- `支付体验分析payment-experience.md`（综合分析页）
- `汕头服务器内测访谈shantou-server-beta-week1.md`（资料摘要页）
- `春节满意度调研spring-festival-survey.md`（资料摘要页）
- `搜索功能痛点search-pain-points.md`（概念页）
- `竞品对比分析competitor-comparison.md`（综合分析页）

**规则**：
1. 中文部分：简短描述（4-8个字），代表页面的核心主题
2. 英文部分：小写 kebab-case，与中文描述对应的英文标识符
3. 两部分直接拼接，无分隔符
4. 英文部分同时作为 qmd 搜索和交叉引用的锚点

---

## 页面格式快速参考

所有 wiki 页面必须包含 YAML frontmatter：

```yaml
---
title: 页面标题
date: YYYY-MM-DD（最后更新日期）
tags: [标签1, 标签2]
sources: [sources/相关摘要页1, sources/相关摘要页2]
related: [entities/实体页, concepts/概念页]
---
```

**交叉引用格式**：
- Obsidian 风格：`[[页面名]]`
- Markdown 标准：`[描述](../entities/页面名.md)`
- 建议优先使用 `[[页面名]]` 格式（Obsidian 兼容）

**特殊标注格式**：
- 矛盾：`> ⚠️ **矛盾**：...`
- 综合结论：`> 💡 **综合结论**：...`
- 待验证：`> ❓ **待验证**：...`
- 过时内容：`> 🔄 **已更新**：此结论已被 [[sources/新资料]] 取代，见 [[concepts/新页面]]`
