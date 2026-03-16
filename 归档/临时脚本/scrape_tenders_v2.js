#!/usr/bin/env node
/**
 * 招标公告抓取脚本 - 修正版
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置
const TARGET_DATE = '2026-03-10';
const KEYWORDS = ['勘察', '地质', '监测', '检测', '测绘', '测量', '岩土', '水文', '环境', '土壤', '地下水'];
const OUTPUT_DIR = path.join(__dirname);

// HTTP GET请求
function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

// 从HTML中提取项目信息
function extractProjects(html) {
  const projects = [];
  
  // 匹配招标公告链接
  const linkRegex = /<a\s+href="(\/xxhz\/014001\/014001001\/[^"]+)"[^>]*title="([^"]+)"[^>]*>/g;
  
  // 查找所有链接
  let match;
  const seenUrls = new Set();
  
  while ((match = linkRegex.exec(html)) !== null) {
    const url = match[1];
    const title = match[2];
    
    // 去重
    if (seenUrls.has(url)) continue;
    seenUrls.add(url);
    
    // 提取日期（在链接后的下一行或同一行）
    const endIndex = match.index + match[0].length;
    const nearbyText = html.substring(match.index, endIndex + 500);
    const dateMatch = nearbyText.match(/\[(\d{4}-\d{2}-\d{2})\]/);
    const date = dateMatch ? dateMatch[1] : '';
    
    // 只保留目标日期的项目
    if (date === TARGET_DATE) {
      projects.push({
        title,
        url: `https://www.cqggzy.com${url}`,
        date,
        keywords: []
      });
    }
  }
  
  return projects;
}

// 筛选相关项目
function filterByKeywords(projects) {
  return projects.map(project => {
    const matchedKeywords = KEYWORDS.filter(keyword => 
      project.title.includes(keyword)
    );
    return {
      ...project,
      keywords: matchedKeywords
    };
  }).filter(project => project.keywords.length > 0);
}

// 主函数
async function main() {
  console.log('🚀 开始抓取招标公告...');
  console.log(`📅 目标日期: ${TARGET_DATE}`);
  console.log(`🔍 筛选关键词: ${KEYWORDS.join(', ')}\n`);
  
  try {
    // 确保输出目录存在
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    // 抓取招标公告列表页面
    const baseUrl = 'https://www.cqggzy.com/xxhz/014001/bidding.html';
    console.log(`📡 正在访问: ${baseUrl}`);
    
    const html = await httpGet(baseUrl);
    console.log(`✅ 获取页面成功，长度: ${html.length}\n`);
    
    // 提取项目
    const allProjects = extractProjects(html);
    console.log(`📊 找到 ${allProjects.length} 个项目（${TARGET_DATE}）\n`);
    
    // 筛选相关项目
    const relevantProjects = filterByKeywords(allProjects);
    console.log(`🎯 筛选出 ${relevantProjects.length} 个相关项目：\n`);
    
    // 输出项目列表
    relevantProjects.forEach((project, index) => {
      console.log(`${index + 1}. ${project.title}`);
      console.log(`   日期: ${project.date}`);
      console.log(`   关键词: ${project.keywords.join(', ')}`);
      console.log(`   链接: ${project.url}\n`);
    });
    
    // 保存结果
    const outputFile = path.join(OUTPUT_DIR, `tenders_${TARGET_DATE}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(relevantProjects, null, 2), 'utf-8');
    console.log(`\n💾 结果已保存到: ${outputFile}`);
    
    return relevantProjects;
  } catch (error) {
    console.error('❌ 抓取失败:', error.message);
    console.error(error.stack);
    throw error;
  }
}

// 执行
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, extractProjects, filterByKeywords };
