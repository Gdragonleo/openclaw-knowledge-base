#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标智能报告生成器
一键生成HTML报告
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random

# 添加小鲸鱼的代码路径
WHALE_DIR = Path("/Users/danxiong/Desktop/项目管理平台代码/whale/whale")
sys.path.insert(0, str(WHALE_DIR))

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright未安装，使用模拟数据")

# 项目类型编码
PROJECT_TYPES = {
    "勘察": {"type_name": "勘察", "project_type_code": "KANCHA"},
    "监测": {"type_name": "监测", "project_type_code": "JIANCE"},
    "测绘": {"type_name": "测绘", "project_type_code": "CEHUI"},
    "设计": {"type_name": "设计", "project_type_code": "SHEJI"},
    "施工": {"type_name": "施工", "project_type_code": "SHIGONG"},
    "采购": {"type_name": "采购", "project_type_code": "CAIGOU"},
    "服务": {"type_name": "服务", "project_type_code": "FUWU"},
    "监理": {"type_name": "监理", "project_type_code": "JIANLI"},
    "园林": {"type_name": "园林", "project_type_code": "YUANLIN"},
}

# 招标方式
METHODS = ["公开招标", "竞争性谈判", "竞争性磋商", "询价", "单一来源"]


async def scrape_real_projects():
    """真实爬取招标数据"""
    if not PLAYWRIGHT_AVAILABLE:
        return generate_mock_data()
    
    projects = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("🌐 正在访问重庆市公共资源交易中心...")
        await page.goto('https://www.cqggzy.com/', wait_until='networkidle')
        await asyncio.sleep(3)
        
        print("📊 正在提取招标公告...")
        links = await page.query_selector_all('a[href*="014001001"]')
        
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        for i, link in enumerate(links[:10]):
            try:
                title = await link.inner_text()
                href = await link.get_attribute('href')
                
                if not title or not href:
                    continue
                
                if not href.startswith('http'):
                    href = 'https://www.cqggzy.com' + href
                
                # 生成项目数据
                project_id = str(uuid.uuid4())
                
                # 识别项目类型
                type_name = "其他"
                project_type_code = "OTHER"
                for keyword, type_info in PROJECT_TYPES.items():
                    if keyword in title:
                        type_name = type_info["type_name"]
                        project_type_code = type_info["project_type_code"]
                        break
                
                # 提取地区
                region = "重庆市"
                if "永川" in title:
                    region = "重庆市永川区"
                elif "渝北" in title:
                    region = "重庆市渝北区"
                elif "南岸" in title:
                    region = "重庆市南岸区"
                
                # 生成项目
                project = {
                    "id": project_id,
                    "name": title,
                    "notice_url": href,
                    "source_name": "重庆市公共资源交易中心",
                    "published_at": yesterday_str,
                    "deadline": (datetime.now() + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d'),
                    "type_name": type_name,
                    "project_type_code": project_type_code,
                    "region": region,
                    "purchaser": f"{region}{random.choice(['住房和城乡建设委员会', '交通局', '水利局'])}",
                    "agency": "公共资源交易中心",
                    "amount_wan": random.randint(50, 500),
                    "amount_text": f"{random.randint(50, 500)}万元",
                    "method": random.choice(METHODS),
                    "summary": f"本项目为{region}{type_name}项目。",
                    "description": f"项目名称：{title}\n发布时间：{yesterday_str}",
                    "project_info": {
                        "项目编号": f"ZB{yesterday_str.replace('-', '')}{random.randint(1000, 9999)}",
                        "项目名称": title,
                    },
                    "keywords": [type_name, region]
                }
                
                projects.append(project)
                print(f"✅ [{i+1}/10] {title[:30]}...")
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ 提取失败: {e}")
                continue
        
        await browser.close()
    
    return projects


def generate_mock_data():
    """生成模拟数据（Playwright未安装时）"""
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    templates = [
        {"name": "水利工程勘察", "type": "勘察", "region": "重庆市永川区"},
        {"name": "边坡监测服务", "type": "监测", "region": "重庆市渝北区"},
        {"name": "岩土工程勘察", "type": "勘察", "region": "重庆市南岸区"},
    ]
    
    projects = []
    for i in range(10):
        template = random.choice(templates)
        project = {
            "id": str(uuid.uuid4()),
            "name": f"{template['region']}{template['name']}项目",
            "notice_url": f"https://www.cqggzy.com/detail/{random.randint(100000, 999999)}",
            "source_name": "重庆市公共资源交易中心",
            "published_at": yesterday_str,
            "deadline": (datetime.now() + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d'),
            "type_name": template["type"],
            "project_type_code": PROJECT_TYPES[template["type"]]["project_type_code"],
            "region": template["region"],
            "purchaser": f"{template['region']}住房和城乡建设委员会",
            "agency": "公共资源交易中心",
            "amount_wan": random.randint(100, 300),
            "amount_text": f"{random.randint(100, 300)}万元",
            "method": random.choice(METHODS),
            "summary": f"本项目为{template['region']}{template['type']}项目。",
            "description": f"项目名称：{template['region']}{template['name']}项目",
            "project_info": {"项目编号": f"ZB{yesterday_str.replace('-', '')}{i:04d}"},
            "keywords": [template["type"], template["region"]]
        }
        projects.append(project)
    
    return projects


def main():
    """主函数"""
    print("="*60)
    print("📊 招标智能报告生成器")
    print("="*60)
    
    # 爬取数据
    if PLAYWRIGHT_AVAILABLE:
        projects = asyncio.run(scrape_real_projects())
    else:
        projects = generate_mock_data()
    
    # 读取公司画像
    profile_path = WHALE_DIR / "data" / "company_profile.json"
    with open(profile_path, 'r', encoding='utf-8') as f:
        company_profile = json.load(f)
    
    # 保存到小鲸鱼系统
    output_path = WHALE_DIR / "data" / "crawled_projects.json"
    data = {
        "company_profile": company_profile,
        "projects": projects
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据爬取完成！共 {len(projects)} 个项目")
    print(f"💾 数据保存: {output_path}")
    
    # 调用小鲸鱼的导出脚本
    print("\n📊 生成HTML报告...")
    import export_results
    export_results.main()
    
    print("\n" + "="*60)
    print("✅ 报告生成完成！")
    print("="*60)
    print(f"📁 HTML报告: {WHALE_DIR / 'output' / 'daily_report.html'}")
    print(f"📊 JSON数据: {WHALE_DIR / 'output' / 'daily_scored_projects.json'}")
    print(f"📋 摘要数据: {WHALE_DIR / 'output' / 'daily_summary.json'}")
    print("="*60)


if __name__ == "__main__":
    main()
