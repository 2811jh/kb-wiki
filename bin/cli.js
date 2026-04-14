#!/usr/bin/env node

/**
 * kb-wiki CLI 入口
 * qmd 搜索引擎完整内嵌在 scripts/qmd/ 目录中
 */

const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');
const pkg = require('../package.json');

// qmd 路径
const qmdDir = path.join(__dirname, '..', 'scripts', 'qmd');
const qmdBin = path.join(qmdDir, 'bin', 'qmd');
const qmdNodeModules = path.join(qmdDir, 'node_modules');

// 检测 qmd 状态
let qmdStatus = '';
const qmdInstalled = fs.existsSync(qmdNodeModules);
const qmdBuilt = fs.existsSync(path.join(qmdDir, 'dist'));

if (qmdInstalled && qmdBuilt) {
  qmdStatus = '✅ 已就绪（内嵌在 scripts/qmd/）';
} else if (qmdInstalled && !qmdBuilt) {
  qmdStatus = '⚠️ 依赖已安装但未编译，请运行: cd scripts/qmd && npm run build';
} else {
  qmdStatus = '⚠️ 首次使用需初始化，请在 LLM 中运行 /setup';
}

console.log(`
╔══════════════════════════════════════════════╗
║           kb-wiki skill 安装成功 🎉           ║
╚══════════════════════════════════════════════╝

版本：${pkg.version}
qmd：${qmdStatus}
qmd 路径：${qmdDir}

📚 这是一个 LLM 驱动的持久化知识库管理 skill。
   qmd 搜索引擎已完整内嵌在 scripts/qmd/ 目录中。

   请在 Claude / 其他 LLM 客户端中运行：

   /setup    ← 首次使用（自动安装 qmd 依赖 + 创建知识库）
   /ingest   ← 导入新资料（自动更新 10-15 个 wiki 页面）
   /query    ← 查询知识库（混合搜索 + 综合答案）
   /lint     ← 健康检查（矛盾、孤立页面、缺失引用等）
   /status   ← 查看知识库统计

🔗 文档：https://github.com/2811jh/kb-wiki
`);