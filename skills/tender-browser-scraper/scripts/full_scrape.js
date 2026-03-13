// 重庆公共资源交易中心 - 完整数据抓取
const fs = require('fs').promises;

// 关键词
const KEYWORDS = [
  '建筑', '市政', '园林', '绿化', '钢结构', '装饰', '装修',
  '房建', '道路', '桥梁', '排水', '景观', '幕墙', '内装',
  '勘察', '测绘', '监测', '地质', '岩土', '测量',
  '工程', '施工', '改造', '建设', '设施', '基础设施',
  '住房', '产业园', '变电站', '能源', '电站',
  '垃圾', '污水处理', '供水', '管网', '水利', '河道',
  '土地', '土壤', '修复', '治理', '环境', '生态'
];

function matchesKeywords(text) {
  return KEYWORDS.some(keyword => text.includes(keyword));
}

// 存储所有项目
let allProjects = [];

console.log('开始完整抓取...');
console.log('预计需要15-20分钟，请耐心等待...');
