#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能招标系统 - 项目筛选算法
基于历史数据分析项目推荐指数

作者：小八爪 🐙
创建时间：2026-03-14
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class TenderRecommendation:
    """招标项目推荐算法"""
    
    # 刘氏集团招标策略配置（从知识库/招标策略配置.json读取）
    STRATEGY = {
        "主要业务类型": ["YT", "SJ", "监测", "勘察设计", "检测"],
        "成功类型": {
            "YT": {"成功率": 36.1, "权重": 1.5},  # 岩土类，成功率最高
            "SJ": {"成功率": 14.0, "权重": 1.2},  # 设计类
            "监测": {"成功率": 11.8, "权重": 1.1},
            "勘察设计": {"成功率": 0.0, "权重": 0.8},
            "检测": {"成功率": 0.0, "权重": 0.7}
        },
        "地域范围": ["重庆市", "四川省"],
        "平均合同金额": 1199613,  # 119万元
        "金额范围": [100000, 20000000],  # 10万-2000万
        "重点领域": ["水利"],  # 小刘特别想进入的领域
        "长期合作客户": []  # 需要从数据库提取
    }
    
    def __init__(self, strategy_config=None):
        """
        初始化
        
        Args:
            strategy_config: 策略配置（可选）
        """
        if strategy_config:
            self.STRATEGY.update(strategy_config)
    
    def calculate_recommendation_score(self, project: Dict) -> int:
        """
        计算项目推荐指数（0-100分）
        
        Args:
            project: 项目信息
                {
                    "name": "项目名称",
                    "type": "YT/SJ/...",
                    "region": "重庆/四川/...",
                    "amount": 500000,
                    "customer": "客户名称",
                    "deadline": "2026-03-20"
                }
        
        Returns:
            int: 推荐指数（0-100）
        """
        score = 0
        
        # 1. 业务类型匹配度（40分）
        score += self._score_business_type(project.get("type", ""))
        
        # 2. 地域优势（20分）
        score += self._score_region(project.get("region", ""))
        
        # 3. 金额范围匹配（20分）
        score += self._score_amount(project.get("amount", 0))
        
        # 4. 客户关系（20分）
        score += self._score_customer(project.get("customer", ""))
        
        # 5. 特殊需求加分（水利领域）
        if self._is_priority_field(project):
            score += 20
        
        # 6. 时间紧迫性（可选）
        if project.get("deadline"):
            score += self._score_deadline(project.get("deadline"))
        
        # 限制在0-100
        score = max(0, min(100, score))
        
        return score
    
    def _score_business_type(self, project_type: str) -> int:
        """
        业务类型评分（40分）
        
        Args:
            project_type: 项目类型
            
        Returns:
            int: 分数（0-40）
        """
        if not project_type:
            return 20  # 未知类型，给中等分
        
        # 从策略配置中查找
        type_info = self.STRATEGY["成功类型"].get(project_type, {})
        success_rate = type_info.get("成功率", 0)
        weight = type_info.get("权重", 0.5)
        
        # YT类型（岩土）成功率最高
        if project_type == "YT":
            return 40
        # SJ类型（设计）成功率较高
        elif project_type == "SJ":
            return 35
        # 监测类型
        elif project_type == "监测":
            return 30
        # 其他已知类型
        elif project_type in self.STRATEGY["主要业务类型"]:
            return 25
        # 未知类型
        else:
            return 15
    
    def _score_region(self, region: str) -> int:
        """
        地域评分（20分）
        
        Args:
            region: 地区
            
        Returns:
            int: 分数（0-20）
        """
        if not region:
            return 10  # 未知地区，给中等分
        
        # 重庆本地
        if "重庆" in region or "渝" in region:
            return 20
        # 四川
        elif "四川" in region or "川" in region:
            return 18
        # 西南地区
        elif any(p in region for p in ["云南", "贵州", "西藏"]):
            return 15
        # 其他地区
        else:
            return 10
    
    def _score_amount(self, amount: int) -> int:
        """
        金额评分（20分）
        
        Args:
            amount: 金额（元）
            
        Returns:
            int: 分数（0-20）
        """
        if not amount or amount <= 0:
            return 10  # 未知金额，给中等分
        
        # 最优金额范围：100-200万（历史平均119万）
        if 100000 <= amount <= 2000000:
            return 20
        # 可接受范围：50-500万
        elif 500000 <= amount <= 5000000:
            return 18
        # 较大项目：500-1000万
        elif 5000000 <= amount <= 10000000:
            return 15
        # 超大项目：1000万以上
        elif amount > 10000000:
            return 12
        # 小项目：50万以下
        else:
            return 10
    
    def _score_customer(self, customer: str) -> int:
        """
        客户评分（20分）
        
        Args:
            customer: 客户名称
            
        Returns:
            int: 分数（0-20）
        """
        if not customer:
            return 10  # 未知客户，给中等分
        
        # 长期合作客户（需要从数据库提取）
        if customer in self.STRATEGY.get("长期合作客户", []):
            return 20
        # 政府项目
        elif any(k in customer for k in ["政府", "局", "委", "办"]):
            return 18
        # 国企项目
        elif any(k in customer for k in ["集团", "公司", "企业"]):
            return 15
        # 其他
        else:
            return 12
    
    def _is_priority_field(self, project: Dict) -> bool:
        """
        判断是否为重点领域（水利）
        
        Args:
            project: 项目信息
            
        Returns:
            bool: 是否为重点领域
        """
        project_type = project.get("type", "")
        project_name = project.get("name", "")
        
        # 水利类型
        if "水利" in project_type or "水" in project_type:
            return True
        
        # 项目名称包含水利关键词
        water_keywords = ["水库", "水利", "灌溉", "防汛", "河道", "堤坝"]
        if any(k in project_name for k in water_keywords):
            return True
        
        return False
    
    def _score_deadline(self, deadline: str) -> int:
        """
        时间紧迫性评分（额外加分0-10分）
        
        Args:
            deadline: 截止日期
            
        Returns:
            int: 分数（0-10）
        """
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            days_left = (deadline_date - datetime.now()).days
            
            # 3天内截止，紧急
            if days_left <= 3:
                return 10
            # 7天内截止
            elif days_left <= 7:
                return 5
            else:
                return 0
        except:
            return 0
    
    def predict_win_probability(self, project: Dict) -> Dict:
        """
        预测中标概率
        
        Args:
            project: 项目信息
            
        Returns:
            dict: 中标概率信息
        """
        recommendation_score = self.calculate_recommendation_score(project)
        
        # 基于推荐分数估算中标概率
        # 推荐分数 80+ -> 概率 60-80%
        # 推荐分数 60-79 -> 概率 40-60%
        # 推荐分数 40-59 -> 概率 20-40%
        # 推荐分数 <40 -> 概率 <20%
        
        if recommendation_score >= 80:
            prob_range = [60, 80]
            confidence = "高"
        elif recommendation_score >= 60:
            prob_range = [40, 60]
            confidence = "中"
        elif recommendation_score >= 40:
            prob_range = [20, 40]
            confidence = "低"
        else:
            prob_range = [5, 20]
            confidence = "很低"
        
        return {
            "probability_range": prob_range,
            "confidence": confidence,
            "recommendation_score": recommendation_score,
            "analysis": self._generate_analysis(project, recommendation_score)
        }
    
    def _generate_analysis(self, project: Dict, score: int) -> str:
        """
        生成分析说明
        
        Args:
            project: 项目信息
            score: 推荐分数
            
        Returns:
            str: 分析说明
        """
        analysis = []
        
        # 业务类型分析
        if project.get("type") == "YT":
            analysis.append("✅ 岩土类项目，历史成功率36.1%，优势明显")
        elif project.get("type") == "SJ":
            analysis.append("✅ 设计类项目，历史成功率14.0%，有一定经验")
        else:
            analysis.append("⚠️ 项目类型经验较少")
        
        # 金额分析
        amount = project.get("amount", 0)
        if 100000 <= amount <= 2000000:
            analysis.append("✅ 金额在最优范围内（100-200万）")
        else:
            analysis.append("⚠️ 金额偏大或偏小，需谨慎评估")
        
        # 地域分析
        if "重庆" in project.get("region", ""):
            analysis.append("✅ 重庆本地项目，地域优势明显")
        
        # 水利领域加分
        if self._is_priority_field(project):
            analysis.append("🎯 水利领域项目，符合重点发展方向")
        
        return "\n".join(analysis)
    
    def suggest_price(self, project: Dict) -> Dict:
        """
        报价建议
        
        Args:
            project: 项目信息
            
        Returns:
            dict: 报价建议
        """
        amount = project.get("amount", 0)
        recommendation_score = self.calculate_recommendation_score(project)
        
        # 基于推荐分数调整报价策略
        if recommendation_score >= 80:
            # 高优势项目，可以报价稍高
            price_multiplier = 1.0
            strategy = "稳健报价，保持合理利润"
        elif recommendation_score >= 60:
            # 中等优势，需要竞争
            price_multiplier = 0.95
            strategy = "适当降价，提高竞争力"
        else:
            # 低优势，激进降价
            price_multiplier = 0.9
            strategy = "低价策略，争取机会"
        
        suggested_price = amount * price_multiplier if amount > 0 else 0
        
        return {
            "suggested_price": suggested_price,
            "price_range": [
                suggested_price * 0.95,
                suggested_price * 1.05
            ],
            "strategy": strategy,
            "margin_estimate": "20-30%" if recommendation_score >= 60 else "10-20%"
        }
    
    def recommend_projects(self, projects: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        批量推荐项目
        
        Args:
            projects: 项目列表
            top_n: 返回前N个
            
        Returns:
            list: 推荐项目列表
        """
        scored_projects = []
        
        for project in projects:
            score = self.calculate_recommendation_score(project)
            project_with_score = project.copy()
            project_with_score["recommendation_score"] = score
            project_with_score["win_probability"] = self.predict_win_probability(project)
            project_with_score["price_suggestion"] = self.suggest_price(project)
            scored_projects.append(project_with_score)
        
        # 按推荐分数排序
        scored_projects.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return scored_projects[:top_n]


def main():
    """测试函数"""
    # 测试项目数据
    test_projects = [
        {
            "name": "九龙坡老旧小区改造项目",
            "type": "YT",
            "region": "重庆市九龙坡区",
            "amount": 800000,
            "customer": "九龙坡区政府",
            "deadline": "2026-03-20"
        },
        {
            "name": "沙坪坝土壤修复项目",
            "type": "YT",
            "region": "重庆市沙坪坝区",
            "amount": 650000,
            "customer": "沙坪坝环保局",
            "deadline": "2026-03-25"
        },
        {
            "name": "永川区水利工程勘察",
            "type": "YT",
            "region": "重庆市永川区",
            "amount": 1200000,
            "customer": "永川区水利局",
            "deadline": "2026-03-18"
        }
    ]
    
    # 创建推荐器
    recommender = TenderRecommendation()
    
    print("=" * 60)
    print("智能招标系统 - 项目推荐测试")
    print("=" * 60)
    
    # 测试单个项目
    print("\n【单个项目分析】")
    for project in test_projects:
        print(f"\n项目：{project['name']}")
        print("-" * 50)
        
        # 推荐分数
        score = recommender.calculate_recommendation_score(project)
        print(f"推荐指数：{score}/100")
        
        # 中标概率
        prob = recommender.predict_win_probability(project)
        print(f"中标概率：{prob['probability_range'][0]}-{prob['probability_range'][1]}%")
        print(f"置信度：{prob['confidence']}")
        print(f"分析：\n{prob['analysis']}")
        
        # 报价建议
        price = recommender.suggest_price(project)
        print(f"\n报价建议：")
        print(f"  建议价格：{price['suggested_price']:,.0f}元")
        print(f"  价格区间：{price['price_range'][0]:,.0f}-{price['price_range'][1]:,.0f}元")
        print(f"  策略：{price['strategy']}")
    
    # 批量推荐
    print("\n" + "=" * 60)
    print("【批量推荐结果】")
    print("=" * 60)
    
    recommended = recommender.recommend_projects(test_projects, top_n=3)
    
    for i, project in enumerate(recommended, 1):
        print(f"\n{i}. {project['name']}")
        print(f"   推荐指数：{project['recommendation_score']}/100")
        print(f"   中标概率：{project['win_probability']['probability_range'][0]}-{project['win_probability']['probability_range'][1]}%")


if __name__ == "__main__":
    main()
