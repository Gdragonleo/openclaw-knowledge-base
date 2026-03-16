#!/usr/bin/env node
/**
 * 简化的招标公告抓取脚本
 * 使用https模块直接抓取网页内容
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置
const TARGET_DATE = '2026-03-10';
const KEYWORDS = ['勘察', '地质', '监测', '检测', '测绘', '测量', '岩土'];
const OUTPUT_DIR = path.join(__dirname, '../outputs');

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
  
  // 简单的正则提取（实际项目中应该使用cheerio等HTML解析器）
  const linkRegex = /<a[^>]*href="([^"]*014001001[^"]*)"[^>]*>([^<]*)<\/a>/g;
  const dateRegex = /(\d{4}-\d{2}-\d{2})/g;
  
  let match;
  while ((match = linkRegex.exec(html)) !== null) {
    const url = match[1];
    const title = match[2].trim();
    
    // 提取日期（假设日期在链接附近）
    const nearbyText = html.substring(Math.max(0, match.index - 200), match.index + 200);
    const dateMatch = nearbyText.match(dateRegex);
    const date = dateMatch ? dateMatch[0] : '';
    
    // 只保留目标日期的项目
    if (date === TARGET_DATE) {
      projects.push({
        title,
        url: url.startsWith('http') ? url : `https://www.cqggzy.com${url}`,
        date
      });
    }
  }
  
  return projects;
}

// 筛选相关项目
function filterByKeywords(projects) {
  return projects.filter(project => 
    KEYWORDS.some(keyword => project.title.includes(keyword))
  );
}

// 主函数
async function main() {
  console.log('🚀 开始抓取招标公告...');
  console.log(`📅 目标日期: ${TARGET_DATE}`);
  
  try {
    // 确保输出目录存在
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    // 抓取招标公告列表页面
    const baseUrl = 'https://www.cqggzy.com/xxhz/014001/bidding.html';
    console.log(`📡 正在访问: ${baseUrl}`);
    
    const html = await httpGet(baseUrl);
    console.log(`✅ 获取页面成功，长度: ${html.length}`);
    
    // 提取项目
    const allProjects = extractProjects(html);
    console.log(`📊 找到 ${allProjects.length} 个项目（${TARGET_DATE}）`);
    
    // 筛选相关项目
    const relevantProjects = filterByKeywords(allProjects);
    console.log(`🎯 筛选出 ${relevantProjects.length} 个相关项目`);
    
    // 保存结果
    const outputFile = path.join(OUTPUT_DIR, `tenders_${TARGET_DATE}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(relevantProjects, null, 2));
    console.log(`💾 结果已保存到: ${outputFile}`);
    
    // 输出项目列表
    relevantProjects.forEach((project, index) => {
      console.log(`\n${index + 1}. ${project.title}`);
      console.log(`   日期: ${project.date}`);
      console.log(`   链接: ${project.url}`);
    });
    
    return relevantProjects;
  } catch (error) {
    console.error('❌ 抓取失败:', error.message);
    throw error;
  }
}

// 执行
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, extractProjects, filterByKeywords };
