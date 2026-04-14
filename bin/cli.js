#!/usr/bin/env node

/**
 * kb-wiki CLI 入口
 * 这是通过 npx skills add 2811jh/kb-wiki 安装的 skill 包
 * 实际功能由 skills/ 目录下的 Markdown 文档驱动，供 LLM 读取执行
 * qmd 搜索引擎作为 npm 依赖已自动内嵌
 */

const { execSync } = require('child_process');
const pkg = require('../package.json');

// 检测 qmd 是否可用
let qmdVersion = '未检测到';
try {
  qmdVersion = execSync('npx qmd --version 2>&1', { encoding: 'utf8', timeout: 10000 }).trim();
} catch (e) {
  try {
    // 尝试直接从依赖目录调用
    const qmdBin = require.resolve('@tobilu/qmd/bin/qmd');
    qmdVersion = '已内嵌（通过 npm 依赖）';
  } catch (e2) {
    qmdVersion = '⚠️ 未找到，请运行 npm install 重新安装';
  }
}

console.log(`
╔══════════════════════════════════════════════╗
║           kb-wiki skill 安装成功 🎉           ║
╚══════════════════════════════════════════════╝

版本：${pkg.version}
qmd：${qmdVersion}

📚 这是一个 LLM 驱动的持久化知识库管理 skill。
   qmd 搜索引擎已作为依赖内嵌，无需单独安装。

   请在 Claude / 其他 LLM 客户端中运行：

   /setup    ← 首次使用，初始化知识库（检测环境 + 创建目录 + 配置 qmd）
   /ingest   ← 导入新资料（自动更新 10-15 个 wiki 页面）
   /query    ← 查询知识库（混合搜索 + 综合答案）
   /lint     ← 健康检查（矛盾、孤立页面、缺失引用等 7 项检查）
   /status   ← 查看知识库统计

🔗 文档：https://github.com/2811jh/kb-wiki
`);