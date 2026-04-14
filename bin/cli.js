#!/usr/bin/env node

/**
 * kb-wiki CLI 入口
 * 这是通过 npx skills add 2811jh/kb-wiki 安装的 skill 包
 * 实际功能由 skills/ 目录下的 Markdown 文档驱动，供 LLM 读取执行
 */

const pkg = require('../package.json');

console.log(`
╔══════════════════════════════════════════════╗
║           kb-wiki skill 安装成功 🎉           ║
╚══════════════════════════════════════════════╝

版本：${pkg.version}
描述：${pkg.description}

📚 这是一个 LLM-driven 知识库管理 skill。
   请在 Claude / 其他 LLM 客户端中运行：

   /setup    ← 首次使用，初始化知识库
   /ingest   ← 导入新资料
   /query    ← 查询知识库
   /lint     ← 健康检查

🔗 文档：https://github.com/2811jh/kb-wiki
`);
