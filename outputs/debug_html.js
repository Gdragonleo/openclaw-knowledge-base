#!/usr/bin/env node
/**
 * 调试脚本：检查HTML结构
 */

const https = require('https');
const fs = require('fs');

function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function main() {
  const url = 'https://www.cqggzy.com/xxhz/014001/bidding.html';
  console.log(`📡 正在访问: ${url}`);
  
  const html = await httpGet(url);
  
  // 查找包含"2026-03-10"的内容
  const lines = html.split('\n');
  const matches = [];
  
  lines.forEach((line, index) => {
    if (line.includes('2026-03-10') || line.includes('014001001')) {
      matches.push({
        lineNum: index + 1,
        content: line.substring(0, 500)
      });
    }
  });
  
  console.log(`\n找到 ${matches.length} 行匹配内容：\n`);
  matches.slice(0, 20).forEach(match => {
    console.log(`第${match.lineNum}行: ${match.content}\n`);
  });
  
  // 保存HTML到文件
  const outputFile = '/Users/danxiong/.openclaw/workspace/outputs/bidding_page.html';
  fs.writeFileSync(outputFile, html);
  console.log(`\n💾 HTML已保存到: ${outputFile}`);
}

main().catch(console.error);
