# kb-wiki 文件格式转换工具

将 Office 文档（Excel、Word、PowerPoint、PDF）自动转换为 Markdown，供 LLM 读取和 ingest。

## 安装依赖

```bash
pip install -r requirements.txt
```

需要 Python >= 3.10。

## 使用方式

所有脚本遵循统一的 CLI 接口：

```bash
python <脚本> <输入文件> <输出.md> [--images-dir <图片目录>]
```

### Excel → Markdown

```bash
python convert_xlsx.py raw/data/Q1.xlsx wiki/.cache/Q1.xlsx.md --images-dir raw/assets
```

支持 `.xlsx`（openpyxl）和 `.xls`（xlrd）。特性：
- 多 Sheet 支持（每个 Sheet 作为独立章节）
- 智能日期格式检测（防止日期显示为数字）
- 自动跳过空 Sheet
- 提取嵌入图片

### Word → Markdown

```bash
python convert_docx.py raw/articles/report.docx wiki/.cache/report.docx.md --images-dir raw/assets
```

仅支持 `.docx`（不支持旧版 `.doc`，建议用 Word 另存为 `.docx`）。特性：
- 保留标题层级（Heading 1-6）
- 有序/无序列表检测
- 表格转 Markdown 表格
- 页眉页脚自动过滤
- 提取内联图片

### PowerPoint → Markdown

```bash
python convert_pptx.py raw/reports/pitch.pptx wiki/.cache/pitch.pptx.md --images-dir raw/assets
```

特性：
- 逐页提取内容（`## Slide N: 标题`）
- 自动识别幻灯片标题
- 提取图片和表格
- 跳过空白幻灯片

### PDF → Markdown

```bash
python convert_pdf.py raw/papers/paper.pdf wiki/.cache/paper.pdf.md --images-dir raw/assets
```

特性：
- 逐页处理
- 双策略表格检测（标准线框表格 + 文本位置推断）
- 标题/列表格式智能识别
- 图片提取（跳过 CMYK 和过小图片）
- 内容按原始位置排序输出

## 输出格式

所有脚本成功时输出 JSON 摘要到 stdout：

```json
{"success": true, "file_type": "xlsx", "sheets": 3, "rows": 150, "images": 2}
```

退出码：`0` 成功，`1` 失败。

## 在 kb-wiki 中的使用

这些脚本由 LLM 在 `/ingest` 流程中自动调用。用户不需要手动运行。

当 LLM 检测到 `raw/` 中的文件是非文本格式时，会自动：
1. 调用对应转换脚本
2. 将转换后的 `.md` 存到 `wiki/.cache/`
3. 读取转换结果，执行标准 ingest 流程

## 致谢

转换逻辑参考了 office-to-md skill 的实现，针对 kb-wiki 场景做了精简适配。
