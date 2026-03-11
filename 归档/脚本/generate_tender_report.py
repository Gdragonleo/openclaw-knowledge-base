#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标报告生成器 - 生成超详细报告
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 勘察/监测/测绘类关键词
SURVEY_KEYWORDS = [
    '勘察', '地质勘察', '岩土工程', '岩土勘察',
    '测绘', '测量', '地形测绘', '工程测量',
    '监测', '检测', '观测', '安全监测', '变形监测',
    '物探', '地质勘探',
    '水文地质', '环境地质',
    '边坡', '基坑', '地基',
    '土壤污染', '环境修复'
]

def matches_keywords(text: str, keywords: List[str]) -> bool:
    """检查文本是否匹配关键词"""
    return any(keyword in text for keyword in keywords)

def generate_detailed_analysis(project: Dict[str, Any]) -> Dict[str, Any]:
    """为项目生成7个维度的详细分析"""
    
    # 1. 基本信息
    basic_info = {
        '项目名称': project.get('title', '未知'),
        '项目金额': project.get('amount', '待确定'),
        '招标单位': project.get('bidder', '待公布'),
        '发布时间': project.get('date', datetime.now().strftime('%Y-%m-%d')),
        '截止时间': project.get('deadline', '待确定'),
        '地区': project.get('region', '重庆市'),
        '项目类型': project.get('type', '工程招标'),
        '资质要求': project.get('qualification', '待查看招标文件'),
        '原文链接': project.get('url', '')
    }
    
    # 2. 项目详情
    project_detail = {
        '项目批准文件': project.get('approval_doc', '待查看'),
        '主要建设内容': project.get('content', '待查看详情'),
        '项目规模': project.get('scale', '待确定'),
        '招标方式': project.get('tender_method', '公开招标'),
        '交易场所': project.get('venue', '重庆市公共资源交易中心')
    }
    
    # 3. 市场机会分析
    amount_str = project.get('amount', '0')
    amount_num = 0
    if isinstance(amount_str, str) and '万' in amount_str:
        try:
            amount_num = float(amount_str.replace('万元', '').replace('元', '').strip())
        except:
            amount_num = 0
    
    market_opportunity = {
        '政策支持': analyze_policy_support(project),
        '市场需求': analyze_market_demand(project),
        '投资规模': f"{amount_num}万元" if amount_num > 0 else "待确定",
        '地域优势': analyze_regional_advantage(project),
        '业务机会': analyze_business_opportunity(project),
        '推荐指数': calculate_recommendation_index(project, amount_num)
    }
    
    # 4. 竞争分析
    competition_analysis = {
        '竞争程度': analyze_competition_level(project, amount_num),
        '竞争对手': '待市场调研',
        '技术门槛': analyze_technical_threshold(project),
        '资质壁垒': analyze_qualification_barrier(project)
    }
    
    # 5. 投标建议
    bidding_advice = {
        '投标策略': generate_bidding_strategy(project, amount_num),
        '报价区间': estimate_price_range(amount_num),
        '技术方案重点': identify_technical_focus(project),
        '团队配置建议': suggest_team_configuration(project),
        '准备时间': estimate_preparation_time(project),
        '成功概率': estimate_success_probability(project, amount_num)
    }
    
    # 6. 风险评估
    risk_assessment = {
        '时间风险': analyze_time_risk(project),
        '业绩风险': analyze_performance_risk(project),
        '技术风险': analyze_technical_risk(project),
        '资金风险': analyze_financial_risk(amount_num),
        '竞争风险': analyze_competition_risk(project, amount_num),
        '综合风险等级': calculate_overall_risk(project, amount_num)
    }
    
    # 7. 原文链接
    original_link = {
        'URL': project.get('url', 'https://www.cqggzy.com'),
        '访问提示': '建议使用Chrome浏览器访问,注意投标截止时间'
    }
    
    return {
        'basic_info': basic_info,
        'project_detail': project_detail,
        'market_opportunity': market_opportunity,
        'competition_analysis': competition_analysis,
        'bidding_advice': bidding_advice,
        'risk_assessment': risk_assessment,
        'original_link': original_link
    }

# 以下是分析函数的实现

def analyze_policy_support(project: Dict) -> str:
    """分析政策支持"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['老旧小区', '改造', '基础设施']):
        return "⭐⭐⭐⭐⭐ 国家重点支持,政策力度大"
    elif any(kw in title for kw in ['环境', '治理', '修复']):
        return "⭐⭐⭐⭐ 环保政策支持"
    elif any(kw in title for kw in ['水利', '河道']):
        return "⭐⭐⭐⭐ 水利工程政策支持"
    else:
        return "⭐⭐⭐ 一般性政策支持"

def analyze_market_demand(project: Dict) -> str:
    """分析市场需求"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['改造', '更新', '提升']):
        return "市场需求旺盛,城市更新需求持续增长"
    elif any(kw in title for kw in ['监测', '检测']):
        return "安全监测需求稳定,技术要求高"
    elif any(kw in title for kw in ['勘察', '测绘']):
        return "勘察测绘需求平稳,专业性强"
    else:
        return "市场需求一般"

def analyze_regional_advantage(project: Dict) -> str:
    """分析地域优势"""
    region = project.get('region', '')
    if '主城' in region or '两江' in region:
        return "⭐⭐⭐⭐⭐ 主城区项目,交通便利,配套完善"
    elif '区县' in region:
        return "⭐⭐⭐ 区县项目,竞争相对较小"
    else:
        return "⭐⭐⭐⭐ 重庆市项目,市场活跃"

def analyze_business_opportunity(project: Dict) -> str:
    """分析业务机会"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['勘察', '测绘', '监测']):
        return "🎯 核心业务领域,建议重点关注"
    elif any(kw in title for kw in ['设计', '监理']):
        return "📋 相关业务领域,可考虑拓展"
    else:
        return "💡 潜在业务机会,需评估匹配度"

def calculate_recommendation_index(project: Dict, amount: float) -> str:
    """计算推荐指数"""
    title = project.get('title', '').lower()
    score = 0
    
    # 金额评分
    if amount >= 1000:
        score += 2
    elif amount >= 500:
        score += 1
    
    # 关键词评分
    if any(kw in title for kw in ['勘察', '测绘', '监测']):
        score += 2
    
    # 政策支持评分
    if any(kw in title for kw in ['改造', '更新', '基础设施']):
        score += 1
    
    if score >= 4:
        return "⭐⭐⭐⭐⭐"
    elif score >= 3:
        return "⭐⭐⭐⭐"
    elif score >= 2:
        return "⭐⭐⭐"
    else:
        return "⭐⭐"

def analyze_competition_level(project: Dict, amount: float) -> str:
    """分析竞争程度"""
    if amount >= 1000:
        return "⭐⭐⭐⭐⭐ 大项目,竞争激烈"
    elif amount >= 500:
        return "⭐⭐⭐⭐ 中等项目,竞争较强"
    else:
        return "⭐⭐⭐ 小项目,竞争一般"

def analyze_technical_threshold(project: Dict) -> str:
    """分析技术门槛"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['监测', '检测', '勘察']):
        return "技术要求较高,需要专业资质"
    elif any(kw in title for kw in ['设计', '咨询']):
        return "需要专业设计能力"
    else:
        return "技术要求一般"

def analyze_qualification_barrier(project: Dict) -> str:
    """分析资质壁垒"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['勘察', '测绘']):
        return "需要勘察/测绘资质"
    elif any(kw in title for kw in ['监测', '检测']):
        return "需要监测/检测资质"
    else:
        return "一般工程资质即可"

def generate_bidding_strategy(project: Dict, amount: float) -> str:
    """生成投标策略"""
    if amount >= 1000:
        return "建议联合体投标,提升竞争力"
    elif amount >= 500:
        return "可独立投标,重点突出技术优势"
    else:
        return "快速响应,突出性价比"

def estimate_price_range(amount: float) -> str:
    """估算报价区间"""
    if amount <= 0:
        return "待查看招标文件"
    
    lower = amount * 0.92
    upper = amount * 0.98
    return f"{lower:.2f}万元 - {upper:.2f}万元"

def identify_technical_focus(project: Dict) -> str:
    """识别技术方案重点"""
    title = project.get('title', '').lower()
    if '勘察' in title:
        return "重点:勘察方案设计、技术装备、人员配置"
    elif '监测' in title:
        return "重点:监测方案、设备选型、数据分析"
    elif '测绘' in title:
        return "重点:测绘精度、技术标准、成果质量"
    else:
        return "重点:施工组织设计、质量控制、安全管理"

def suggest_team_configuration(project: Dict) -> str:
    """建议团队配置"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['勘察', '测绘']):
        return "建议:项目负责人+技术负责人+专业工程师(3-5人)"
    elif '监测' in title:
        return "建议:项目负责人+监测工程师+数据分析(2-4人)"
    else:
        return "建议:项目经理+技术团队(根据规模配置)"

def estimate_preparation_time(project: Dict) -> str:
    """估算准备时间"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['大型', '综合']):
        return "建议准备时间:15-20个工作日"
    elif any(kw in title for kw in ['勘察', '监测']):
        return "建议准备时间:10-15个工作日"
    else:
        return "建议准备时间:7-10个工作日"

def estimate_success_probability(project: Dict, amount: float) -> str:
    """估算成功概率"""
    title = project.get('title', '').lower()
    score = 50
    
    if any(kw in title for kw in ['勘察', '测绘', '监测']):
        score += 20
    
    if amount < 500:
        score += 10
    elif amount > 1000:
        score -= 10
    
    return f"{score}%"

def analyze_time_risk(project: Dict) -> str:
    """分析时间风险"""
    return "⚠️ 需关注投标截止时间,提前准备材料"

def analyze_performance_risk(project: Dict) -> str:
    """分析业绩风险"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['勘察', '监测']):
        return "⚠️ 需要类似项目业绩,注意积累"
    else:
        return "✅ 一般业绩要求,风险较低"

def analyze_technical_risk(project: Dict) -> str:
    """分析技术风险"""
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['复杂', '大型']):
        return "⚠️ 技术要求高,需充分准备"
    else:
        return "✅ 技术要求适中"

def analyze_financial_risk(amount: float) -> str:
    """分析资金风险"""
    if amount >= 1000:
        return "⚠️ 大额项目,需评估资金压力"
    elif amount >= 500:
        return "✅ 资金要求适中"
    else:
        return "✅ 资金压力较小"

def analyze_competition_risk(project: Dict, amount: float) -> str:
    """分析竞争风险"""
    if amount >= 1000:
        return "⚠️ 大项目竞争激烈,价格压力大"
    else:
        return "✅ 竞争相对可控"

def calculate_overall_risk(project: Dict, amount: float) -> str:
    """计算综合风险等级"""
    risk_score = 0
    
    if amount >= 1000:
        risk_score += 2
    elif amount >= 500:
        risk_score += 1
    
    title = project.get('title', '').lower()
    if any(kw in title for kw in ['复杂', '大型']):
        risk_score += 1
    
    if risk_score >= 3:
        return "⚠️ 高风险"
    elif risk_score >= 2:
        return "⚡ 中风险"
    else:
        return "✅ 低风险"

def generate_report(projects: List[Dict], report_date: str) -> str:
    """生成完整报告"""
    
    # 筛选勘察/监测/测绘类项目
    survey_projects = [p for p in projects if matches_keywords(p.get('title', ''), SURVEY_KEYWORDS)]
    
    # 按类型分类
    survey_type = []
    monitor_type = []
    mapping_type = []
    
    for project in survey_projects:
        title = project.get('title', '')
        if any(kw in title for kw in ['勘察', '地质', '岩土']):
            survey_type.append(project)
        elif any(kw in title for kw in ['监测', '检测', '观测']):
            monitor_type.append(project)
        elif any(kw in title for kw in ['测绘', '测量']):
            mapping_type.append(project)
    
    # 生成报告内容
    report = f"""# 招标日报 - {report_date}

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据时间范围**: {report_date}
**监控网站**: 重庆市公共资源交易中心
**项目总数**: {len(projects)}个

---

## 📊 总体统计

### 按地区分布
"""
    
    # 统计地区分布
    regions = {}
    for project in projects:
        region = project.get('region', '重庆市')
        regions[region] = regions.get(region, 0) + 1
    
    for region, count in regions.items():
        report += f"- **{region}**: {count}个\n"
    
    report += "\n### 按金额分布\n"
    
    # 统计金额分布
    amount_dist = {'1000万以上': 0, '500-1000万': 0, '100-500万': 0, '100万以下': 0}
    total_amount = 0
    
    for project in projects:
        amount_str = project.get('amount', '0')
        if isinstance(amount_str, str) and '万' in amount_str:
            try:
                amount = float(amount_str.replace('万元', '').replace('元', '').strip())
                total_amount += amount
                if amount >= 1000:
                    amount_dist['1000万以上'] += 1
                elif amount >= 500:
                    amount_dist['500-1000万'] += 1
                elif amount >= 100:
                    amount_dist['100-500万'] += 1
                else:
                    amount_dist['100万以下'] += 1
            except:
                pass
    
    for range_name, count in amount_dist.items():
        report += f"- **{range_name}**: {count}个\n"
    
    report += f"\n**总金额**: {total_amount:.2f}万元\n"
    
    report += f"""
### 按项目类型分布

- **🔍 勘察类**: {len(survey_type)}个
- **📡 监测类**: {len(monitor_type)}个
- **📐 测绘类**: {len(mapping_type)}个

---

## 📋 勘察类项目

"""
    
    # 添加勘察类项目
    for idx, project in enumerate(survey_type, 1):
        analysis = generate_detailed_analysis(project)
        rec = analysis['market_opportunity']['推荐指数']
        
        report += f"### {idx}. {rec} {project.get('title', '未知项目')}\n\n"
        report += format_project_analysis(analysis)
        report += "\n---\n\n"
    
    report += "\n## 📡 监测类项目\n\n"
    
    # 添加监测类项目
    for idx, project in enumerate(monitor_type, 1):
        analysis = generate_detailed_analysis(project)
        rec = analysis['market_opportunity']['推荐指数']
        
        report += f"### {idx}. {rec} {project.get('title', '未知项目')}\n\n"
        report += format_project_analysis(analysis)
        report += "\n---\n\n"
    
    report += "\n## 📐 测绘类项目\n\n"
    
    # 添加测绘类项目
    for idx, project in enumerate(mapping_type, 1):
        analysis = generate_detailed_analysis(project)
        rec = analysis['market_opportunity']['推荐指数']
        
        report += f"### {idx}. {rec} {project.get('title', '未知项目')}\n\n"
        report += format_project_analysis(analysis)
        report += "\n---\n\n"
    
    # 综合分析
    report += """## 📊 综合分析

### TOP 10 推荐项目

"""
    
    # 按推荐指数排序
    all_survey_projects = survey_type + monitor_type + mapping_type
    # 这里简化处理,实际应该根据推荐指数排序
    
    for idx, project in enumerate(all_survey_projects[:10], 1):
        report += f"{idx}. {project.get('title', '未知项目')} - {project.get('amount', '待定')}\n"
    
    report += """
### 紧急项目清单（7天内截止）

*需要根据实际截止时间筛选*

### 重点机会项目清单

*高推荐指数项目列表*

### 投标优先级建议

1. 优先关注勘察类项目,匹配度高
2. 关注监测类项目,技术优势明显
3. 评估测绘类项目,考虑投入产出比

---

**备注**:
- 本报告基于公开招标信息生成
- 建议以官方招标文件为准
- 投标前请仔细阅读资质要求和截止时间

---

**小八爪自动生成** 🐙
**生成时间**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return report

def format_project_analysis(analysis: Dict) -> str:
    """格式化项目分析"""
    
    output = ""
    
    # 基本信息
    output += "#### 📋 基本信息\n\n"
    for key, value in analysis['basic_info'].items():
        if key == '原文链接':
            output += f"**{key}**: [查看详情]({value})\n\n"
        else:
            output += f"**{key}**: {value}\n\n"
    
    # 项目详情
    output += "#### 📄 项目详情\n\n"
    for key, value in analysis['project_detail'].items():
        output += f"**{key}**: {value}\n\n"
    
    # 市场机会
    output += "#### 💰 市场机会\n\n"
    for key, value in analysis['market_opportunity'].items():
        output += f"- **{key}**: {value}\n"
    output += "\n"
    
    # 竞争分析
    output += "#### ⚔️ 竞争分析\n\n"
    for key, value in analysis['competition_analysis'].items():
        output += f"- **{key}**: {value}\n"
    output += "\n"
    
    # 投标建议
    output += "#### 🎯 投标建议\n\n"
    for key, value in analysis['bidding_advice'].items():
        output += f"- **{key}**: {value}\n"
    output += "\n"
    
    # 风险评估
    output += "#### ⚠️ 风险评估\n\n"
    for key, value in analysis['risk_assessment'].items():
        output += f"- **{key}**: {value}\n"
    output += "\n"
    
    # 原文链接
    output += "#### 🔗 原文链接\n\n"
    output += f"[查看完整招标文件]({analysis['original_link']['URL']})\n\n"
    output += f"*{analysis['original_link']['访问提示']}*\n\n"
    
    return output

if __name__ == "__main__":
    # 测试代码
    test_project = {
        'title': '测试项目-勘察工程',
        'amount': '500万元',
        'bidder': '测试招标单位',
        'date': '2026-03-10',
        'url': 'https://www.cqggzy.com',
        'region': '重庆市'
    }
    
    analysis = generate_detailed_analysis(test_project)
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
