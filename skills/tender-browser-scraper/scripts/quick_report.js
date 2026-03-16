#!/usr/bin/env node
/**
 * 快速抓取脚本 - 直接使用browser工具的结果
 */

const fs = require('fs').promises;
const path = require('path');

// 关键词
const KEYWORDS = [
  '建筑', '市政', '园林', '绿化', '钢结构', '装饰', '装修',
  '房建', '道路', '桥梁', '排水', '景观', '幕墙', '内装',
  '勘察', '测绘', '监测', '地质', '岩土', '测量',
  '工程', '施工', '改造', '建设', '设施', '基础设施',
  '住房', '住房', '产业园', '变电站', '能源', '电站',
  '垃圾', '污水处理', '供水', '管网', '水利', '河道',
  '土地', '土壤', '修复', '治理', '环境', '生态'
];

// 从第一页提取的项目数据
const firstPageProjects = [
  {
    "title": "【九龙坡区】 重庆市九龙坡区城市老旧小区供水管网漏损治理及二次供水设施更新改造工程（一期）三标段（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001002/20260306/dfb6f955-c4e5-42fe-ab4e-44d90d888228.html",
    "date": "2026-03-06"
  },
  {
    "title": "【自主招标】 重庆市人民医院两江院区一层病案室加层改造工程项目（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/5d0f5b9a-63c7-4bd6-b9b1-2f767cf39e72.html",
    "date": "2026-03-06"
  },
  {
    "title": "【沙坪坝区】 重庆农药化工（集团）有限公司原址局部(A／B／C／D地块)土壤污染修复管控工程项目监理",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001010/20260306/320e86fe-c0b6-44fe-b29e-20149c23e18e.html",
    "date": "2026-03-06"
  },
  {
    "title": "【九龙坡区】 西城映画项目改造工程",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/f57cb6e1-f820-4b8f-8807-ad5cae2911fd.html",
    "date": "2026-03-06"
  },
  {
    "title": "【巫溪县】 巫溪县2025年度其他国土绿化项目",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001010/20260306/a315535b-e56a-41f7-a41d-281962444f01.html",
    "date": "2026-03-06"
  },
  {
    "title": "【北碚区】 北碚区麻柳河山洪沟治理工程（二期）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001007/20260306/c49e2818-e62f-4c01-bc6b-5d0a22648bab.html",
    "date": "2026-03-06"
  },
  {
    "title": "【两江新区】 产业园配套变电站项目（B7-3-2地块110KV专用变电站）（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/495a2222-ddf7-426a-9b02-f489cae343b2.html",
    "date": "2026-03-06"
  },
  {
    "title": "【两江新区】 协同创新区-五期创新空间、孵化加速器能源站供配电采购及安装项目（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/1a18097f-4fb1-4f64-8960-483397d6e15f.html",
    "date": "2026-03-06"
  },
  {
    "title": "【两江新区】 两江新区水土高新产业园复兴北片区基础设施工程（一期）（一标段—3号路）、两江新区水土高新产业园复兴北片区基础设施工程（一期）（一标段—1-5号路K1+090～K1+180段）等2个工程（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001002/20260306/76cb1ff9-29bb-45c9-8d15-ac5cf54ae65b.html",
    "date": "2026-03-06"
  },
  {
    "title": "【两江新区】 C标准分区路网三期工程（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001002/20260306/fba4ec2b-7665-4063-aed2-241bc2a5afdb.html",
    "date": "2026-03-06"
  },
  {
    "title": "【两江新区】 12英寸功率半导体芯片制造及封装测试生产基地项目（生产调度及研发楼）EPC总承包（第二次）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/32fcbf37-fc50-42b2-ba1b-34fc4c47b4f4.html",
    "date": "2026-03-06"
  },
  {
    "title": "【彭水县】 彭水县靛水街道建筑垃圾消纳场及资源化利用项目（监理）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001002/20260306/1339ce8b-976a-4f85-bbcb-1022cb663579.html",
    "date": "2026-03-06"
  },
  {
    "title": "【石柱县】 石柱县城镇生活垃圾治理项目（二期）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001002/20260306/745b8d03-9b97-4d9c-aca6-6158a1e4f661.html",
    "date": "2026-03-06"
  },
  {
    "title": "【永川区】 重庆永川区云谷大数据产业园F区保障性租赁住房及重庆市永川高新区数字经济融合创新示范产业园项目EPC总承包",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/4ba5b0c2-e5b3-4e57-982b-56d5ef22cadc.html",
    "date": "2026-03-06"
  },
  {
    "title": "【永川区】 重庆永川区云谷大数据产业园F区保障性租赁住房及重庆市永川高新区数字经济融合创新示范产业园项目EPC总承包监理",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/9c8a7ff1-43fa-41c7-8b52-488bd59a307b.html",
    "date": "2026-03-06"
  },
  {
    "title": "【涪陵区】 重庆港龙头作业区二期工程5#、6#多用途泊位后方陆域堆场（一期）第二次",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001010/20260306/21293ee6-78aa-4d59-aa43-6fe6106ad1ae.html",
    "date": "2026-03-06"
  },
  {
    "title": "【合川区】 合川区2026年补家项目区小流域综合治理提质增效项目",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001007/20260306/87951221-bbfa-423b-96ed-a733c73a6ce7.html",
    "date": "2026-03-06"
  },
  {
    "title": "【自主招标】 垫江县牡丹湖智能化农贸市场建设项目EPC铝镁锰屋面瓦采购（第二次）竞争性比选公告",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/99fafebd-38a2-4826-b43b-c801f0409759.html",
    "date": "2026-03-06"
  },
  {
    "title": "【酉阳县】 酉阳县保障性住房（一期）项目—山水云境监理",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001001/20260306/a45029f5-67bb-437d-9dbd-5af28c22de96.html",
    "date": "2026-03-06"
  },
  {
    "title": "【江津区】 江津区四面山镇头道河社区、林海村2026年度市级美丽移民村建设项目（项目编号AA202600271）",
    "url": "https://www.cqggzy.com/xxhz/014001/014001001/014001001007/20260306/6b2c7659-254c-4726-bbf9-dc275b810a94.html",
    "date": "2026-03-06"
  }
];

// 筛选关键词匹配的项目
function matchesKeywords(text) {
  return KEYWORDS.some(keyword => text.includes(keyword));
}

const relevantProjects = firstPageProjects.filter(p => matchesKeywords(p.title));

console.log(`第一页共${firstPageProjects.length}个项目，筛选出${relevantProjects.length}个相关项目`);

// 生成初步报告
async function generatePreliminaryReport() {
  const date = new Date().toISOString().split('T')[0];
  const filepath = '/Users/danxiong/.openclaw/workspace/知识库/招标监控/原始清单/重庆公共资源_近3个月_初步清单.md';
  
  let content = `# 重庆市公共资源交易中心招标公告初步清单\n\n`;
  content += `**报告生成时间**: ${new Date().toLocaleString('zh-CN')}\n`;
  content += `**数据来源**: 第一页（共20个项目）\n`;
  content += `**筛选项目**: ${relevantProjects.length}个相关项目\n\n`;
  content += `---\n\n`;
  content += `## 📋 相关项目列表（第一页）\n\n`;
  
  relevantProjects.forEach((project, index) => {
    content += `### ${index + 1}. ${project.title}\n\n`;
    content += `**发布时间**: ${project.date}\n\n`;
    content += `**原文链接**: [查看详情](${project.url})\n\n`;
    content += `---\n\n`;
  });
  
  content += `\n## 📌 说明\n\n`;
  content += `- 这是初步报告，仅包含第一页的${relevantProjects.length}个相关项目\n`;
  content += `- 完整报告正在后台生成中，将包含近3个月的所有相关项目\n`;
  content += `- 完整报告将包含项目金额、招标单位、联系方式等详细信息\n`;
  
  await fs.writeFile(filepath, content, 'utf-8');
  console.log(`✅ 初步报告已生成: ${filepath}`);
  console.log(`📊 共 ${relevantProjects.length} 个相关项目`);
}

generatePreliminaryReport().catch(console.error);
