#!/usr/bin/env node
/**
 * 招标网站自动化爬取工具
 * 使用Playwright模拟真实浏览器行为，支持反爬绕过
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth');
const fs = require('fs').promises;
const path = require('path');

// 使用stealth插件
chromium.use(stealth());

// 配置
const CONFIG = {
  site: process.argv.includes('--site') ? process.argv[process.argv.indexOf('--site') + 1] : 'cqggzy',
  output: process.argv.includes('--output') ? process.argv[process.argv.indexOf('--output') + 1] : './output/tenders',
  max: process.argv.includes('--max') ? parseInt(process.argv[process.argv.indexOf('--max') + 1]) : 500,
  useScrapling: process.argv.includes('--use-scrapling'),
  minInterval: process.argv.includes('--min-interval') ? parseInt(process.argv[process.argv.indexOf('--min-interval') + 1]) : 3,
  maxInterval: process.argv.includes('--max-interval') ? parseInt(process.argv[process.argv.indexOf('--max-interval') + 1]) : 8,
  days: process.argv.includes('--days') ? parseInt(process.argv[process.argv.indexOf('--days') + 1]) : 90, // 默认近3个月
  notify: process.argv.includes('--notify'),
};

// 关键词白名单
const KEYWORDS = [
  '建筑工程', '市政工程', '园林绿化', '钢结构', '装饰装修',
  '房建', '道路', '桥梁', '给排水', '景观', '幕墙', '内装',
  '勘察', '测绘', '监测', '地质', '岩土', '测量'
];

// 网站配置
const SITES = {
  cqggzy: {
    name: '重庆市公共资源交易中心',
    url: 'https://www.cqggzy.com',
    selectors: {
      announcementLink: 'a[href*="014001001"]', // 招标公告链接
      listContainer: '.tender-list, .list-container, ul.list',
      itemTitle: 'a, .title, .tender-title',
      itemDate: '.date, .time, span',
      itemAmount: '.amount, .money',
      detailPage: {
        title: 'h1, .title',
        content: '.content, .detail-content, .tender-detail',
        amount: '.amount, .money',
        deadline: '.deadline, .date',
        contact: '.contact, .phone',
      }
    }
  }
};

// 工具函数
function randomDelay(min, max) {
  return new Promise(resolve => 
    setTimeout(resolve, (Math.random() * (max - min) + min) * 1000)
  );
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function matchesKeywords(text) {
  return KEYWORDS.some(keyword => text.includes(keyword));
}

function formatDate(date) {
  return date.toISOString().split('T')[0];
}

// 主函数
async function main() {
  console.log('🚀 招标网站爬虫启动');
  console.log(`📋 目标网站: ${SITES[CONFIG.site].name}`);
  console.log(`📁 输出目录: ${CONFIG.output}`);
  console.log(`📊 最大项目数: ${CONFIG.max}`);
  console.log(`⏱️  间隔: ${CONFIG.minInterval}-${CONFIG.maxInterval}秒`);
  
  const site = SITES[CONFIG.site];
  const projects = [];
  
  let browser;
  try {
    // 启动浏览器
    console.log('\n🌐 启动浏览器...');
    browser = await chromium.launch({
      headless: false, // 使用有头模式，更像真人
      args: [
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
      ]
    });
    
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
      locale: 'zh-CN',
    });
    
    const page = await context.newPage();
    
    // 访问首页
    console.log(`\n📍 访问首页: ${site.url}`);
    await page.goto(site.url, { waitUntil: 'networkidle', timeout: 60000 });
    
    // 截图
    await page.screenshot({ path: path.join(CONFIG.output, 'logs', 'homepage.png'), fullPage: true });
    console.log('📸 首页截图已保存');
    
    // 等待页面加载
    await randomDelay(CONFIG.minInterval, CONFIG.maxInterval);
    
    // 点击"招标公告"
    console.log('\n🔍 寻找"招标公告"链接...');
    const announcementLink = await page.$(site.selectors.announcementLink);
    
    if (announcementLink) {
      await announcementLink.click();
      console.log('✅ 已进入招标公告页面');
      await page.waitForLoadState('networkidle');
      await randomDelay(CONFIG.minInterval, CONFIG.maxInterval);
    } else {
      console.log('⚠️  未找到招标公告链接，尝试直接访问列表页');
      await page.goto(`${site.url}/xxhz/014001/014001001/transaction_detail.html`, {
        waitUntil: 'networkidle'
      });
    }
    
    // 提取项目列表
    console.log('\n📋 提取项目列表...');
    
    // 先尝试多种选择器
    const listSelectors = [
      'ul.list li',
      '.tender-list li',
      '.list-container li',
      'table tbody tr',
      '.item-list .item',
      'a[href*="014001001"]' // 直接找所有招标公告链接
    ];
    
    let listItems = [];
    for (const selector of listSelectors) {
      try {
        const items = await page.$$(selector);
        if (items.length > 0) {
          console.log(`✅ 使用选择器 "${selector}" 找到 ${items.length} 个元素`);
          
          // 提取信息
          listItems = await page.$$eval(selector, (els) => {
            return els.map(el => {
              // 尝试多种方式提取标题
              const titleEl = el.querySelector('a[title], a[href*="014001001"], .title, td a, a');
              const title = titleEl?.textContent?.trim() || titleEl?.getAttribute('title') || '';
              
              // 尝试多种方式提取链接
              const linkEl = el.querySelector('a[href*="014001001"], a[href*="/xxhz/"]');
              const link = linkEl?.href || '';
              
              // 尝试提取日期
              const dateText = el.textContent || '';
              const dateMatch = dateText.match(/\d{4}-\d{2}-\d{2}/);
              const date = dateMatch ? dateMatch[0] : '';
              
              // 尝试提取金额
              const amountText = el.textContent || '';
              const amountMatch = amountText.match(/(\d+\.?\d*)\s*(万元|元|万)/);
              const amount = amountMatch ? amountMatch[0] : '';
              
              return {
                title: title,
                link: link,
                date: date,
                amount: amount,
              };
            }).filter(item => item.title && item.link);
          });
          
          if (listItems.length > 0) break;
        }
      } catch (error) {
        continue;
      }
    }
    
    console.log(`✅ 找到 ${listItems.length} 个项目`);
    
    // 过滤相关项目
    const relevantProjects = listItems.filter(item => matchesKeywords(item.title));
    console.log(`🎯 筛选出 ${relevantProjects.length} 个相关项目`);
    
    // 逐个访问详情页
    const toVisit = relevantProjects.slice(0, CONFIG.max);
    
    for (let i = 0; i < toVisit.length; i++) {
      const item = toVisit[i];
      console.log(`\n[${i + 1}/${toVisit.length}] 访问: ${item.title}`);
      
      try {
        await page.goto(item.link, { waitUntil: 'networkidle', timeout: 30000 });
        await randomDelay(CONFIG.minInterval, CONFIG.maxInterval);
        
        // 提取详情
        const detail = await page.evaluate(() => {
          const getText = (sel) => document.querySelector(sel)?.textContent?.trim() || '';
          const getAttr = (sel, attr) => document.querySelector(sel)?.getAttribute(attr) || '';
          
          // 尝试多种选择器
          const title = getText('.article-title, h1.title, .tender-title, h1, h2') || 
                        getAttr('meta[name="title"]', 'content') || 
                        document.title;
          
          const content = getText('.epoint-article-content, .content, .detail-content, .main-content, article');
          
          // 提取金额
          const amountText = content || getText('body');
          const amountMatch = amountText.match(/(\d+\.?\d*)\s*(万元|元|万)/);
          const amount = amountMatch ? amountMatch[0] : '';
          
          // 提取日期
          const dateMatch = content.match(/(\d{4}-\d{2}-\d{2})/g);
          const date = dateMatch && dateMatch.length > 0 ? dateMatch[0] : '';
          
          // 提取联系方式
          const contactMatch = content.match(/联系电话[：:]\s*([\d\-]+)/);
          const contact = contactMatch ? contactMatch[1] : '';
          
          // 提取招标人
          const bidderMatch = content.match(/招标人[：:]\s*([^\n]+)/);
          const bidder = bidderMatch ? bidderMatch[1].trim() : '';
          
          // 提取截止时间
          const deadlineMatch = content.match(/截止时间[：:]\s*([^\n]+)/);
          const deadline = deadlineMatch ? deadlineMatch[1].trim() : '';
          
          return {
            title: title,
            content: content.substring(0, 1000), // 限制长度
            amount: amount,
            date: date,
            contact: contact,
            bidder: bidder,
            deadline: deadline,
          };
        });
        
        projects.push({
          ...item,
          ...detail,
          url: item.link,
        });
        
        console.log(`✅ 提取成功: ${detail.title || item.title}`);
        
      } catch (error) {
        console.error(`❌ 访问失败: ${error.message}`);
      }
    }
    
  } catch (error) {
    console.error('❌ 爬取失败:', error);
    
    if (!CONFIG.useScrapling) {
      console.log('\n💡 建议使用 --use-scrapling 参数重试');
    }
    
  } finally {
    if (browser) {
      await browser.close();
    }
  }
  
  // 生成报告
  if (projects.length > 0) {
    console.log(`\n📊 生成报告...`);
    await generateReport(projects, site.name);
  }
  
  console.log('\n✅ 爬取完成');
}

// 生成报告
async function generateReport(projects, siteName) {
  const reportDate = formatDate(new Date());
  const filename = `${reportDate}_${CONFIG.site}.md`;
  const filepath = path.join(CONFIG.output, filename);
  
  // 统计信息
  const totalAmount = projects.reduce((sum, p) => {
    const amount = parseFloat(p.amount?.match(/(\d+\.?\d*)/)?.[1] || 0);
    return sum + amount;
  }, 0);
  
  const categories = {};
  projects.forEach(p => {
    const type = p.title?.includes('道路') ? '道路工程' :
                 p.title?.includes('桥梁') ? '桥梁工程' :
                 p.title?.includes('建筑') ? '建筑工程' :
                 p.title?.includes('市政') ? '市政工程' :
                 p.title?.includes('勘察') ? '勘察测绘' :
                 p.title?.includes('监测') ? '工程监测' :
                 '其他';
    categories[type] = (categories[type] || 0) + 1;
  });
  
  let content = `# ${siteName}招标公告汇总报告\n\n`;
  content += `**报告生成时间**: ${new Date().toLocaleString('zh-CN')}\n`;
  content += `**数据时间范围**: 近${CONFIG.days}天\n`;
  content += `**项目总数**: ${projects.length}个\n`;
  content += `**预估总金额**: ${totalAmount.toFixed(2)}万元\n\n`;
  
  content += `## 📊 统计信息\n\n`;
  content += `### 按类型分布\n\n`;
  Object.entries(categories).forEach(([type, count]) => {
    content += `- **${type}**: ${count}个\n`;
  });
  
  content += `\n---\n\n`;
  content += `## 📋 项目列表\n\n`;
  
  projects.forEach((project, index) => {
    content += `## ${index + 1}. ${project.title || '未知项目'}\n\n`;
    if (project.bidder) content += `**招标单位**: ${project.bidder}\n\n`;
    if (project.amount) content += `**项目金额**: ${project.amount}\n\n`;
    if (project.deadline) content += `**截止时间**: ${project.deadline}\n\n`;
    if (project.date) content += `**发布时间**: ${project.date}\n\n`;
    if (project.contact) content += `**联系方式**: ${project.contact}\n\n`;
    if (project.content) content += `**项目详情**:\n\`\`\`\n${project.content}\n\`\`\`\n\n`;
    if (project.url) content += `**原文链接**: [查看详情](${project.url})\n\n`;
    content += `---\n\n`;
  });
  
  // 确保目录存在
  await fs.mkdir(CONFIG.output, { recursive: true });
  await fs.mkdir(path.join(CONFIG.output, 'logs'), { recursive: true });
  
  // 写入文件
  await fs.writeFile(filepath, content, 'utf-8');
  console.log(`✅ 报告已生成: ${filepath}`);
}

// 执行
main().catch(console.error);
