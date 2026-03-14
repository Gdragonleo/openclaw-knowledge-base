#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麻将运势 - 易经算法
基于易经64卦推演每日麻将运势

作者：小八爪 🐙
创建时间：2026-03-14
"""

from datetime import datetime, date
import json
import hashlib


class MahjongFortune:
    """麻将运势推演算法"""
    
    # 64卦象数据（简化版，实际应从配置文件读取）
    HEXAGRAMS = {
        1: {"name": "乾卦", "nature": "天", "fortune": 95, "desc": "大吉大利，所向披靡"},
        2: {"name": "坤卦", "nature": "地", "fortune": 90, "desc": "厚德载物，稳中求胜"},
        # ... 这里应该有64个卦象，为了示例只列出前几个
        3: {"name": "屯卦", "nature": "水雷", "fortune": 60, "desc": "初生之难，谨慎行事"},
        4: {"name": "蒙卦", "nature": "山水", "fortune": 55, "desc": "启蒙之象，学习为主"},
        5: {"name": "需卦", "nature": "水天", "fortune": 70, "desc": "等待时机，不宜急躁"},
        # 省略其他58个卦象...
        11: {"name": "泰卦", "nature": "地天", "fortune": 92, "desc": "天地交泰，万事亨通"},
        12: {"name": "否卦", "nature": "天地", "fortune": 40, "desc": "天地不交，诸事不宜"},
        33: {"name": "遁卦", "nature": "天山", "fortune": 45, "desc": "退避三舍，以退为进"},
        34: {"name": "大壮", "nature": "雷天", "fortune": 75, "desc": "刚健有力，勇往直前"},
        63: {"name": "既济", "nature": "水火", "fortune": 85, "desc": "功德圆满，功成身退"},
        64: {"name": "未济", "nature": "火水", "fortune": 65, "desc": "事业未成，继续努力"},
    }
    
    # 八卦方位数据
    BAGUA_DIRECTIONS = {
        "乾": {"direction": "西北", "element": "金", "score_base": 70},
        "坤": {"direction": "西南", "element": "土", "score_base": 65},
        "震": {"direction": "东", "element": "木", "score_base": 75},
        "巽": {"direction": "东南", "element": "木", "score_base": 80},
        "坎": {"direction": "北", "element": "水", "score_base": 60},
        "离": {"direction": "南", "element": "火", "score_base": 70},
        "艮": {"direction": "东北", "element": "土", "score_base": 68},
        "兑": {"direction": "西", "element": "金", "score_base": 72},
    }
    
    def __init__(self, target_date=None, birthday=None):
        """
        初始化
        
        Args:
            target_date: 目标日期（默认今天）
            birthday: 用户生日（可选，用于个性化）
        """
        self.date = target_date if target_date else date.today()
        self.birthday = birthday
        self.hexagram = self._calculate_hexagram()
    
    def _calculate_hexagram(self):
        """
        计算今日卦象（基于日期）
        
        Returns:
            int: 卦象编号（1-64）
        """
        # 方法1：基于日期数字求和
        date_str = self.date.strftime("%Y%m%d")
        date_num = int(date_str)
        
        # 如果有生日，加入计算
        if self.birthday:
            try:
                birth_str = self.birthday.strftime("%Y%m%d")
                date_num += int(birth_str)
            except:
                pass
        
        # 使用哈希增加随机性
        hash_value = int(hashlib.md5(str(date_num).encode()).hexdigest(), 16)
        hexagram_num = (hash_value % 64) + 1  # 1-64
        
        return hexagram_num
    
    def _get_fortune_by_hexagram(self, hexagram_num):
        """
        根据卦象获取运势
        
        Args:
            hexagram_num: 卦象编号
            
        Returns:
            dict: 卦象信息
        """
        return self.HEXAGRAMS.get(hexagram_num, {
            "name": f"第{hexagram_num}卦",
            "nature": "未知",
            "fortune": 60,
            "desc": "运势平稳"
        })
    
    def calculate_fengshui(self):
        """
        计算今日风水方位
        
        Returns:
            dict: 风水方位信息
        """
        # 基于卦象计算各方位运势
        hexagram_info = self._get_fortune_by_hexagram(self.hexagram)
        base_fortune = hexagram_info["fortune"]
        
        directions = {}
        for gua_name, gua_info in self.BAGUA_DIRECTIONS.items():
            # 基础分数 + 日期影响
            date_influence = (self.date.day * 7 + self.date.month * 3) % 20 - 10
            score = gua_info["score_base"] + date_influence
            
            # 卦象加成
            if gua_name in hexagram_info["nature"]:
                score += 15
            
            # 限制在0-100
            score = max(0, min(100, score))
            
            directions[gua_info["direction"]] = {
                "gua": gua_name,
                "element": gua_info["element"],
                "score": score,
                "level": "最佳" if score >= 75 else ("次选" if score >= 60 else "忌讳")
            }
        
        # 找出最佳和最差方位
        sorted_dirs = sorted(directions.items(), key=lambda x: x[1]["score"], reverse=True)
        best_direction = sorted_dirs[0][0]
        worst_direction = sorted_dirs[-1][0]
        
        return {
            "best_direction": best_direction,
            "worst_direction": worst_direction,
            "all_directions": directions,
            "placement_tips": [
                "靠墙摆放，背后有靠山",
                "灯光明亮，阳气充足",
                "避免对门，防止气流直冲",
                f"今日最佳座位：{best_direction}方"
            ]
        }
    
    def calculate_hourly_fortune(self):
        """
        计算时辰运势（6个时段）
        
        Returns:
            list: 时辰运势列表
        """
        # 中国传统时辰（简化为6个时段）
        time_slots = [
            {"name": "早晨", "range": "05:00-09:00", "gua": "震"},
            {"name": "上午", "range": "09:00-11:00", "gua": "巽"},
            {"name": "中午", "range": "11:00-13:00", "gua": "离"},
            {"name": "下午", "range": "13:00-17:00", "gua": "坤"},
            {"name": "傍晚", "range": "17:00-19:00", "gua": "兑"},
            {"name": "晚上", "range": "19:00-23:00", "gua": "乾"},
        ]
        
        hourly = []
        for slot in time_slots:
            # 基于时辰卦象和日期卦象计算运势
            date_influence = (self.date.day + hash(slot["name"])) % 30 - 15
            base_score = self.BAGUA_DIRECTIONS.get(slot["gua"], {}).get("score_base", 60)
            score = base_score + date_influence
            score = max(30, min(100, score))
            
            hourly.append({
                "name": slot["name"],
                "time_range": slot["range"],
                "gua": slot["gua"],
                "score": score,
                "level": "黄金时段" if score >= 80 else ("适宜" if score >= 60 else "避坑"),
                "advice": self._get_time_advice(score)
            })
        
        return hourly
    
    def _get_time_advice(self, score):
        """根据分数获取时段建议"""
        if score >= 80:
            return "运势最佳，适合做大牌，勇往直前！"
        elif score >= 70:
            return "运势不错，可以积极进攻，但保持冷静"
        elif score >= 60:
            return "运势平稳，稳扎稳打，不宜冒险"
        elif score >= 50:
            return "运势一般，保守为上，小赌怡情"
        else:
            return "运势较弱，建议休息，避免损失"
    
    def get_strategy_advice(self):
        """
        获取策略建议
        
        Returns:
            dict: 策略建议
        """
        hexagram_info = self._get_fortune_by_hexagram(self.hexagram)
        fortune = hexagram_info["fortune"]
        
        if fortune >= 80:
            return {
                "overall": "运势极佳",
                "playing_style": "进攻型",
                "bet_strategy": "可以适当加注，做大牌",
                "risk_level": "中等",
                "psychological": "信心满满，但不要骄傲",
                "when_to_stop": "运势下降时及时收手"
            }
        elif fortune >= 70:
            return {
                "overall": "运势不错",
                "playing_style": "稳健型",
                "bet_strategy": "中等注码，稳步推进",
                "risk_level": "中低",
                "psychological": "保持冷静，不骄不躁",
                "when_to_stop": "赢到目标金额就收手"
            }
        elif fortune >= 60:
            return {
                "overall": "运势平稳",
                "playing_style": "保守型",
                "bet_strategy": "小注怡情，不贪大牌",
                "risk_level": "低",
                "psychological": "心态平和，输赢看淡",
                "when_to_stop": "小输即止，不要追回"
            }
        else:
            return {
                "overall": "运势较弱",
                "playing_style": "观望型",
                "bet_strategy": "不建议打，实在要打就最小注",
                "risk_level": "高",
                "psychological": "调整心态，转移注意力",
                "when_to_stop": "最好不打，去了也早点回来"
            }
    
    def get_warnings(self):
        """
        获取注意事项
        
        Returns:
            list: 注意事项列表
        """
        hexagram_info = self._get_fortune_by_hexagram(self.hexagram)
        fortune = hexagram_info["fortune"]
        
        warnings = []
        
        # 通用警告
        warnings.append("麻将娱乐为主，切勿赌博")
        warnings.append("保持良好心态，输赢乃兵家常事")
        
        # 根据卦象添加特定警告
        if fortune >= 80:
            warnings.append("运势虽好，但不要贪心")
            warnings.append("赢了要见好就收")
        elif fortune >= 70:
            warnings.append("稳中求胜，不要冒险")
            warnings.append("注意观察对手，灵活应变")
        elif fortune >= 60:
            warnings.append("运势平平，不宜久战")
            warnings.append("小赌怡情，大赌伤身")
        else:
            warnings.append("今日运势不佳，建议休息")
            warnings.append("实在要打，要做好输的准备")
            warnings.append("不要追回，及时止损")
        
        # 风水警告
        fengshui = self.calculate_fengshui()
        warnings.append(f"避开{fengshui['worst_direction']}方座位")
        
        return warnings
    
    def get_full_fortune(self):
        """
        获取完整运势
        
        Returns:
            dict: 完整运势信息
        """
        hexagram_info = self._get_fortune_by_hexagram(self.hexagram)
        
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "birthday": self.birthday.strftime("%Y-%m-%d") if self.birthday else None,
            "hexagram": {
                "number": self.hexagram,
                "name": hexagram_info["name"],
                "nature": hexagram_info["nature"],
                "fortune_score": hexagram_info["fortune"],
                "description": hexagram_info["desc"]
            },
            "overall_fortune": {
                "score": hexagram_info["fortune"],
                "level": self._get_fortune_level(hexagram_info["fortune"]),
                "summary": hexagram_info["desc"]
            },
            "fengshui": self.calculate_fengshui(),
            "hourly_fortune": self.calculate_hourly_fortune(),
            "strategy": self.get_strategy_advice(),
            "warnings": self.get_warnings(),
            "share_card": {
                "title": f"今日麻将运势 {hexagram_info['name']}",
                "score": hexagram_info["fortune"],
                "tagline": hexagram_info["desc"],
                "lucky_direction": self.calculate_fengshui()["best_direction"]
            }
        }
    
    def _get_fortune_level(self, score):
        """根据分数获取运势等级"""
        if score >= 90:
            return "大吉"
        elif score >= 80:
            return "吉"
        elif score >= 70:
            return "中吉"
        elif score >= 60:
            return "平"
        elif score >= 50:
            return "小凶"
        else:
            return "凶"


def main():
    """测试函数"""
    # 测试1：今天运势
    fortune_today = MahjongFortune()
    result = fortune_today.get_full_fortune()
    
    print("=" * 50)
    print("麻将运势测试 - 今天")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试2：带生日的运势
    print("\n" + "=" * 50)
    print("麻将运势测试 - 带生日")
    print("=" * 50)
    fortune_with_birthday = MahjongFortune(
        target_date=date(2026, 3, 15),
        birthday=date(1990, 1, 1)
    )
    result2 = fortune_with_birthday.get_full_fortune()
    print(json.dumps(result2, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
