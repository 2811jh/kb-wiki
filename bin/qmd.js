#!/usr/bin/env node

/**
 * qmd 跨平台包装脚本
 * 让 LLM 和用户可以直接调用 qmd，无需拼完整路径
 * 
 * 用法：node <skill路径>/bin/qmd.js <命令> [参数]
 * 全局安装后：qmd <命令> [参数]
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const qmdEntry = path.join(__dirname, '..', 'scripts', 'qmd', 'dist', 'cli', 'qmd.js');

// 检查 qmd 是否已编译
if (!fs.existsSync(qmdEntry)) {
  console.error('❌ qmd 尚未编译。请运行：');
  console.error('   node ' + path.join(__dirname, 'postinstall.js'));
  process.exit(1);
}

// 透传所有参数给 qmd
const args = [qmdEntry, ...process.argv.slice(2)];
const child = spawn(process.execPath, args, {
  stdio: 'inherit',
  cwd: process.cwd(),
  env: process.env
});

child.on('close', (code) => {
  process.exit(code || 0);
});
