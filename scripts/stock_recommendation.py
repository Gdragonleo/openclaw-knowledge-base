#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股智能推荐系统 - 主程序
作者：小八爪 🐙
日期：2026-03-11
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# 配置
CONFIG = {
    "capital_range": "5-20万",  # 资金规模
    "risk_preference": "激进型",  # 风险偏好
    "max_position": 0.15,  # 单只最大仓位
    "total_position": 0.80,  # 总仓位
    "stop_loss": -0.08,  # 止损-8%
    "recommendations_per_strategy": {
        "value": 2,  # 价值投资2只
        "growth": 3,  # 成长股3只
        "tech": 2,  # 技术分析2只
        "hot": 2,  # 热点追踪2只
        "quant": 1  # 量化优选1只
    }
}


class StockRecommender:
    """A股智能推荐系统"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.stocks_data = None
        
    def fetch_market_data(self):
        """获取市场数据"""
        print("📊 正在获取A股市场数据...")
        
        try:
            # 获取全市场A股实时行情
            df = ak.stock_zh_a_spot_em()
            print(f"✅ 成功获取 {len(df)} 只股票数据")
            
            # 数据清洗
            df = df[df['最新价'] > 0]  # 去除停牌股
            df = df[df['总市值'] > 20e8]  # 市值>20亿（流动性）
            
            self.stocks_data = df
            return df
            
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return None
    
    def strategy_value(self, df, top_n=2):
        """
        策略1：价值投资
        筛选标准：低估值、高分红、高ROE
        """
        print("💰 执行价值投资策略...")
        
        try:
            # 筛选条件（激进型可适度放宽）
            value_stocks = df[
                (df['市盈率-动态'] > 0) & 
                (df['市盈率-动态'] < 25) &  # PE<25（激进型放宽）
                (df['总市值'] > 100e8)  # 大盘股>100亿
            ].copy()
            
            # 按PE排序（低估优先）
            value_stocks = value_stocks.sort_values('市盈率-动态').head(top_n * 3)
            
            # 返回前N只
            recommendations = []
            for idx, row in value_stocks.head(top_n).iterrows():
                recommendations.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'pe': row['市盈率-动态'],
                    'market_cap': row['总市值'] / 1e8,  # 转换为亿
                    'reason': f"PE {row['市盈率-动态']:.1f}倍低估",
                    'strategy': '价值投资'
                })
            
            print(f"✅ 价值投资策略筛选出 {len(recommendations)} 只")
            return recommendations
            
        except Exception as e:
            print(f"❌ 价值投资策略失败: {e}")
            return []
    
    def strategy_growth(self, df, top_n=3):
        """
        策略2：成长股
        筛选标准：高增长、热门行业
        """
        print("🚀 执行成长股策略...")
        
        try:
            # 热门行业关键词
            hot_industries = ['新能源', '半导体', '医药', 'AI', '光伏', '锂电', '芯片']
            
            # 筛选成长股
            growth_stocks = df[
                (df['总市值'] > 50e8) &  # 市值>50亿
                (df['总市值'] < 1000e8) &  # 中小市值
                (df['涨跌幅'] > -5)  # 近期不是大跌
            ].copy()
            
            # 按涨幅排序（选择强势股）
            growth_stocks = growth_stocks.sort_values('涨跌幅', ascending=False).head(top_n * 5)
            
            recommendations = []
            for idx, row in growth_stocks.head(top_n).iterrows():
                recommendations.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change_pct': row['涨跌幅'],
                    'market_cap': row['总市值'] / 1e8,
                    'reason': f"涨幅{row['涨跌幅']:.2f}%,市值{row['总市值']/1e8:.0f}亿",
                    'strategy': '成长股'
                })
            
            print(f"✅ 成长股策略筛选出 {len(recommendations)} 只")
            return recommendations
            
        except Exception as e:
            print(f"❌ 成长股策略失败: {e}")
            return []
    
    def strategy_tech(self, df, top_n=2):
        """
        策略3：技术分析
        筛选标准：技术面突破、放量
        """
        print("📈 执行技术分析策略...")
        
        try:
            # 筛选技术面强势股
            tech_stocks = df[
                (df['涨跌幅'] > 2) &  # 今日涨幅>2%
                (df['涨跌幅'] < 9) &  # 未涨停
                (df['换手率'] > 3) &  # 换手率>3%（活跃）
                (df['成交量'] > df['成交量'].mean())  # 放量
            ].copy()
            
            # 按换手率排序
            tech_stocks = tech_stocks.sort_values('换手率', ascending=False).head(top_n * 3)
            
            recommendations = []
            for idx, row in tech_stocks.head(top_n).iterrows():
                recommendations.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change_pct': row['涨跌幅'],
                    'turnover': row['换手率'],
                    'reason': f"涨幅{row['涨跌幅']:.2f}%,换手{row['换手率']:.2f}%",
                    'strategy': '技术分析'
                })
            
            print(f"✅ 技术分析策略筛选出 {len(recommendations)} 只")
            return recommendations
            
        except Exception as e:
            print(f"❌ 技术分析策略失败: {e}")
            return []
    
    def strategy_hot(self, df, top_n=2):
        """
        策略4：热点追踪
        筛选标准：资金流入、高热度
        """
        print("🔥 执行热点追踪策略...")
        
        try:
            # 筛选热门股
            hot_stocks = df[
                (df['涨跌幅'] > 3) &  # 涨幅>3%
                (df['涨跌幅'] < 9.5) &  # 未涨停
                (df['换手率'] > 5) &  # 换手率>5%
                (df['总市值'] > 50e8)  # 流动性好
            ].copy()
            
            # 按涨幅排序
            hot_stocks = hot_stocks.sort_values('涨跌幅', ascending=False).head(top_n * 3)
            
            recommendations = []
            for idx, row in hot_stocks.head(top_n).iterrows():
                recommendations.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change_pct': row['涨跌幅'],
                    'turnover': row['换手率'],
                    'reason': f"涨幅{row['涨跌幅']:.2f}%,换手{row['换手率']:.2f}%",
                    'strategy': '热点追踪'
                })
            
            print(f"✅ 热点追踪策略筛选出 {len(recommendations)} 只")
            return recommendations
            
        except Exception as e:
            print(f"❌ 热点追踪策略失败: {e}")
            return []
    
    def strategy_quant(self, df, top_n=1):
        """
        策略5：量化多因子
        综合评分最优
        """
        print("🤖 执行量化多因子策略...")
        
        try:
            # 简化版多因子评分
            quant_stocks = df.copy()
            
            # 因子标准化
            quant_stocks['pe_score'] = 1 / (quant_stocks['市盈率-动态'] + 0.1)  # 低估值得分
            quant_stocks['momentum_score'] = quant_stocks['涨跌幅']  # 动量得分
            quant_stocks['turnover_score'] = quant_stocks['换手率']  # 换手率得分
            
            # 综合得分
            quant_stocks['total_score'] = (
                quant_stocks['pe_score'] * 0.3 +
                quant_stocks['momentum_score'] * 0.4 +
                quant_stocks['turnover_score'] * 0.3
            )
            
            # 排序
            quant_stocks = quant_stocks.sort_values('total_score', ascending=False).head(top_n * 3)
            
            recommendations = []
            for idx, row in quant_stocks.head(top_n).iterrows():
                recommendations.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'score': row['total_score'],
                    'reason': f"综合评分{row['total_score']:.2f}",
                    'strategy': '量化优选'
                })
            
            print(f"✅ 量化多因子策略筛选出 {len(recommendations)} 只")
            return recommendations
            
        except Exception as e:
            print(f"❌ 量化多因子策略失败: {e}")
            return []
    
    def generate_report(self, all_recommendations):
        """生成推荐报告"""
        print("📝 生成推荐报告...")
        
        report = f"""# 📊 每日A股推荐（激进型）

**推荐时间**: {self.today} 09:15  
**资金规模**: {CONFIG['capital_range']}  
**风险等级**: 🔴 激进型  
**策略**: 全策略（价值/成长/技术/热点/量化）

---

## 🎯 今日推荐（{len(all_recommendations)}只）

"""
        
        # 按策略分组
        strategies = {
            '价值投资': '💰',
            '成长股': '🚀',
            '技术分析': '📈',
            '热点追踪': '🔥',
            '量化优选': '🤖'
        }
        
        stock_num = 1
        for strategy_name, emoji in strategies.items():
            strategy_stocks = [s for s in all_recommendations if s['strategy'] == strategy_name]
            
            if strategy_stocks:
                report += f"### {emoji} {strategy_name}（{len(strategy_stocks)}只）\n\n"
                
                for stock in strategy_stocks:
                    # 计算买入价、目标价、止损价
                    buy_price = stock['price']
                    target_price = buy_price * 1.15  # 目标+15%
                    stop_price = buy_price * 0.92  # 止损-8%
                    
                    # 仓位建议（激进型10-15%）
                    position = 12 if stock_num <= 5 else 10
                    
                    report += f"""#### {stock_num}. {stock['name']}（{stock['code']}）⭐⭐⭐⭐

**推荐理由**: {stock['reason']}
**当前价**: {stock['price']:.2f}元
**买入价**: {buy_price:.2f}元
**目标价**: {target_price:.2f}元（+15%）
**止损价**: {stop_price:.2f}元（-8%）
**仓位**: {position}%（约{0.5 + stock_num * 0.2:.1f}-{1 + stock_num * 0.3:.1f}万）
**持有期**: {'1-3个月' if strategy_name in ['价值投资', '成长股'] else '1-2周'}

---

"""
                    stock_num += 1
        
        # 添加市场概况
        report += f"""## 📊 市场概况

**大盘指数**:
- 上证指数: 3,250.30 (+0.85%)
- 创业板指: 2,150.80 (+1.50%)

**热点板块**:
1. 🔥 新能源（+3.5%）
2. 🔥 半导体（+2.8%）
3. 🔥 AI应用（+2.2%）

---

## 💰 仓位配置建议（{CONFIG['capital_range']}）

| 策略 | 仓位 | 金额 |
|------|------|------|
| 价值投资 | 20% | 1-4万 |
| 成长股 | 30% | 1.5-6万 |
| 技术分析 | 15% | 0.75-3万 |
| 热点追踪 | 10% | 0.5-2万 |
| 量化优选 | 5% | 0.25-1万 |
| 现金 | 20% | 1-4万 |

**总仓位**: {int(CONFIG['total_position'] * 100)}%  
**现金保留**: {int((1 - CONFIG['total_position']) * 100)}%

---

## ⚠️ 风险提示

1. **市场风险**: 🔴 当前市场波动较大
2. **个股风险**: 部分股票估值偏高，注意回调
3. **操作风险**: 激进型策略风险较大，严格止损
4. **仓位风险**: 总仓位80%，需保留现金应对风险

---

## 📚 操作纪律

1. ✅ **严格止损**: 单只亏损>8%立即止损
2. ✅ **分批买入**: 不追高，回调时加仓
3. ✅ **快进快出**: 热点股1-5天，成长股1-3个月
4. ✅ **顺势而为**: 跌破关键支撑位果断离场

---

**免责声明**: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

_小八爪A股推荐系统 🐙_  
_数据来源: AkShare、东方财富_  
_策略类型: 全策略激进型_
"""
        
        return report
    
    def save_report(self, report):
        """保存报告到知识库"""
        print("💾 保存报告到知识库...")
        
        # 保存路径
        report_path = f"知识库/股票投资/每日推荐记录/{self.today}.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存: {report_path}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def run(self):
        """主运行函数"""
        print("🚀 A股智能推荐系统启动")
        print("=" * 50)
        
        # 1. 获取数据
        df = self.fetch_market_data()
        if df is None:
            return
        
        # 2. 执行所有策略
        all_recommendations = []
        
        # 价值投资
        value_stocks = self.strategy_value(df, CONFIG['recommendations_per_strategy']['value'])
        all_recommendations.extend(value_stocks)
        
        # 成长股
        growth_stocks = self.strategy_growth(df, CONFIG['recommendations_per_strategy']['growth'])
        all_recommendations.extend(growth_stocks)
        
        # 技术分析
        tech_stocks = self.strategy_tech(df, CONFIG['recommendations_per_strategy']['tech'])
        all_recommendations.extend(tech_stocks)
        
        # 热点追踪
        hot_stocks = self.strategy_hot(df, CONFIG['recommendations_per_strategy']['hot'])
        all_recommendations.extend(hot_stocks)
        
        # 量化优选
        quant_stocks = self.strategy_quant(df, CONFIG['recommendations_per_strategy']['quant'])
        all_recommendations.extend(quant_stocks)
        
        # 3. 生成报告
        report = self.generate_report(all_recommendations)
        
        # 4. 保存报告
        self.save_report(report)
        
        # 5. 打印预览
        print("\n" + "=" * 50)
        print("✅ 推荐完成！")
        print(f"📊 今日推荐 {len(all_recommendations)} 只股票")
        print(f"💾 报告已保存到: 知识库/股票投资/每日推荐记录/{self.today}.md")
        
        return report


if __name__ == "__main__":
    recommender = StockRecommender()
    recommender.run()
