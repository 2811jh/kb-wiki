#!/usr/bin/env node

/**
 * 跨平台 build 脚本（替代 qmd 原始 build 中的 shell 命令）
 * 解决 Windows 上 printf/cat/mv/chmod 不可用的问题
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const qmdDir = path.join(__dirname, '..', 'scripts', 'qmd');
const distCli = path.join(qmdDir, 'dist', 'cli', 'qmd.js');

console.log('📦 kb-wiki: 正在编译内嵌的 qmd 搜索引擎...\n');

// 步骤 1：检测并安装 pnpm（如果没有）
try {
  execSync('pnpm --version', { stdio: 'ignore' });
  console.log('✅ pnpm 已就绪');
} catch {
  console.log('📥 正在安装 pnpm...');
  try {
    execSync('npm install -g pnpm', { stdio: 'inherit' });
    console.log('✅ pnpm 安装成功');
  } catch (e) {
    console.error('⚠️ pnpm 安装失败，尝试使用 npm 继续...');
  }
}

// 步骤 2：安装依赖
console.log('\n📥 正在安装 qmd 依赖（含 native 模块编译）...');
try {
  // 优先用 pnpm，失败则回退到 npm
  try {
    execSync('pnpm install --no-frozen-lockfile', { cwd: qmdDir, stdio: 'inherit' });
  } catch {
    console.log('⚠️ pnpm install 失败，回退到 npm install...');
    execSync('npm install', { cwd: qmdDir, stdio: 'inherit' });
  }
  console.log('✅ 依赖安装成功');
} catch (e) {
  console.error('❌ 依赖安装失败。可能原因：');
  console.error('   - 缺少 C++ 编译工具（Windows: Visual Studio Build Tools, macOS: xcode-select --install）');
  console.error('   - Node.js 版本 < 22');
  console.error('   qmd 搜索功能暂时不可用，但不影响 kb-wiki 的基本功能。');
  process.exit(0); // 不阻断整体安装
}

// 步骤 3：编译 TypeScript
console.log('\n🔨 正在编译 TypeScript...');
try {
  execSync('npx tsc -p tsconfig.build.json', { cwd: qmdDir, stdio: 'inherit' });
  console.log('✅ TypeScript 编译成功');
} catch (e) {
  console.error('❌ TypeScript 编译失败。');
  process.exit(0);
}

// 步骤 4：给 dist/cli/qmd.js 添加 shebang（跨平台方式）
try {
  if (fs.existsSync(distCli)) {
    const content = fs.readFileSync(distCli, 'utf8');
    if (!content.startsWith('#!/usr/bin/env node')) {
      fs.writeFileSync(distCli, '#!/usr/bin/env node\n' + content, 'utf8');
    }
    // Unix 系统加可执行权限
    if (process.platform !== 'win32') {
      fs.chmodSync(distCli, 0o755);
    }
    console.log('✅ CLI 入口配置完成');
  }
} catch (e) {
  console.warn('⚠️ CLI 入口配置跳过（不影响功能）');
}

console.log('\n🎉 qmd 搜索引擎编译完成！');
console.log('   首次使用完整搜索功能时，会自动下载 AI 模型（约 2GB）。');
console.log('   中国大陆用户建议设置环境变量：');
console.log('   HF_ENDPOINT=https://hf-mirror.com\n');
