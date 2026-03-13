# 招标监控Skill - 配置指南

## 📋 配置文件说明

本skill采用JSON配置文件，简单易用。

---

## 1️⃣ 网站配置 (sites.json)

```json
{
  "sites": [
    {
      "id": "cqggzy",
      "name": "重庆市公共资源交易中心",
      "url": "https://www.cqggzy.com",
      "enabled": true,
      "priority": 1,
      "selectors": {
        "announcementLink": "a[href*='014001001']",
        "listContainer": ".list-container",
        "itemTitle": "a",
        "itemDate": ".date"
      },
      "pagination": {
        "enabled": true,
        "maxPages": 10
      }
    }
  ]
}
```

**字段说明**：
- `id`: 网站唯一标识
- `name`: 网站名称
- `url`: 网站地址
- `enabled`: 是否启用
- `priority`: 优先级（1-5，1最高）
- `selectors`: HTML选择器配置
- `pagination`: 分页配置

---

## 2️⃣ 关键词配置 (keywords.json)

```json
{
  "primary": [
    "勘察", "地质勘察", "岩土工程",
    "测绘", "测量", "地形测绘",
    "监测", "检测", "安全监测"
  ],
  "secondary": [
    "水文地质", "环境地质",
    "边坡", "基坑", "地基"
  ],
  "blacklist": [
    "设计", "咨询", "监理"
  ],
  "synonyms": {
    "勘察": ["勘察", "地质勘察", "岩土勘察"],
    "监测": ["监测", "检测", "观测"]
  }
}
```

**字段说明**：
- `primary`: 主要关键词（必须匹配）
- `secondary`: 次要关键词（加分项）
- `blacklist`: 黑名单关键词（排除）
- `synonyms`: 同义词映射

---

## 3️⃣ 公司配置 (company.json)

```json
{
  "basic": {
    "name": "XX工程勘察有限公司",
    "qualifications": [
      "工程勘察甲级",
      "测绘乙级",
      "岩土工程甲级"
    ]
  },
  "business": {
    "core": ["地质勘察", "边坡监测", "基坑监测"],
    "expand": ["测绘", "沉降观测"],
    "exclude": ["设计", "咨询"]
  },
  "regions": {
    "core": ["重庆", "四川"],
    "expand": ["湖北", "贵州", "云南"],
    "exclude": ["西藏", "新疆"]
  },
  "budget": {
    "min": 500,
    "max": 2000,
    "unit": "万元",
    "ideal": [500, 1500]
  },
  "team": {
    "seniorEngineers": 5,
    "juniorEngineers": 10,
    "advantages": ["边坡监测", "深基坑", "隧道监测"]
  },
  "funds": {
    "maxBidBond": 50,
    "maxPerformanceBond": 200,
    "maxConcurrent": 5
  },
  "strategy": {
    "stage": "expansion",
    "yearlyGoal": {
      "projects": 10,
      "amount": 10000
    }
  }
}
```

**字段说明**：
- `basic`: 公司基本信息
- `business`: 业务范围偏好
- `regions`: 地区偏好
- `budget`: 金额偏好
- `team`: 团队能力
- `funds`: 资金实力
- `strategy`: 战略目标

---

## 4️⃣ 运行设置 (settings.json)

```json
{
  "execution": {
    "time": "0 9 * * *",
    "timezone": "Asia/Shanghai",
    "mode": "daily"
  },
  "output": {
    "reportType": "detailed",
    "format": "markdown",
    "saveTo": "./output/",
    "uploadToFeishu": true,
    "feishuConfig": {
      "folderToken": "xxx",
      "chatId": "oc_xxx"
    }
  },
  "notification": {
    "channels": ["feishu", "email"],
    "priority": {
      "urgent": {
        "condition": "amount >= 1000 && matchScore >= 90",
        "channels": ["feishu", "sms"]
      },
      "important": {
        "condition": "amount >= 500 || matchScore >= 70",
        "channels": ["feishu"]
      }
    }
  },
  "advanced": {
    "parallel": true,
    "maxConcurrent": 3,
    "timeout": 300,
    "retry": 3,
    "delay": [3, 8]
  }
}
```

**字段说明**：
- `execution`: 执行配置
- `output`: 输出配置
- `notification`: 通知配置
- `advanced`: 高级配置

---

## 5️⃣ 竞争对手配置 (competitors.json)（可选）

```json
{
  "competitors": [
    {
      "name": "XX勘察设计院",
      "qualifications": ["工程勘察甲级", "设计甲级"],
      "advantages": ["大型项目", "政府项目"],
      "regions": ["重庆", "四川"],
      "avoid": true
    },
    {
      "name": "XX监测公司",
      "qualifications": ["监测甲级"],
      "advantages": ["价格优势"],
      "regions": ["重庆"],
      "avoid": false
    }
  ]
}
```

**用途**：
- 识别竞争激烈的项目
- 避开实力差距大的竞争
- 发现竞争空白区

---

## 🎯 配置示例

### 示例1：勘察公司
```json
{
  "keywords": {
    "primary": ["勘察", "地质", "岩土"]
  },
  "business": {
    "core": ["地质勘察", "岩土工程"]
  },
  "budget": {
    "ideal": [300, 1000]
  }
}
```

### 示例2：监测公司
```json
{
  "keywords": {
    "primary": ["监测", "检测", "观测"]
  },
  "business": {
    "core": ["边坡监测", "基坑监测", "隧道监测"]
  },
  "budget": {
    "ideal": [200, 800]
  }
}
```

### 示例3：测绘公司
```json
{
  "keywords": {
    "primary": ["测绘", "测量", "地形"]
  },
  "business": {
    "core": ["地形测绘", "工程测量"]
  },
  "budget": {
    "ideal": [100, 500]
  }
}
```

---

## 💡 配置技巧

### 1. 关键词优化
- 使用同义词提高覆盖率
- 黑名单过滤不相关项目
- 主次关键词结合使用

### 2. 地区策略
- 核心地区：优先级最高
- 拓展地区：适度关注
- 排除地区：直接过滤

### 3. 金额策略
- 设定理想区间
- 标注风险金额
- 区分项目规模

### 4. 通知策略
- 紧急项目：多渠道通知
- 重要项目：飞书群通知
- 普通项目：仅保存报告

---

## 🔍 调试配置

### 测试配置是否正确
```bash
# 测试单个网站
openclaw skill run tender-monitor --test --site cqggzy

# 测试关键词匹配
openclaw skill run tender-monitor --test --keyword "勘察"

# 测试通知
openclaw skill run tender-monitor --test --notify
```

### 查看配置
```bash
# 查看当前配置
openclaw skill config tender-monitor show

# 编辑配置
openclaw skill config tender-monitor edit sites.json
```

---

## 📚 进阶配置

### 1. 自定义筛选规则
在 `rules.json` 中定义复杂规则：
```json
{
  "rules": [
    {
      "name": "黄金项目",
      "conditions": {
        "amount": {">=": 1000, "<=": 2000},
        "region": {"in": ["重庆", "四川"]},
        "keywords": {"contains": "勘察"},
        "deadline": {">=": 7}
      },
      "priority": 5
    }
  ]
}
```

### 2. 自定义报告模板
在 `templates/` 中创建自定义模板，支持变量：
- `{{date}}` - 日期
- `{{total}}` - 总项目数
- `{{projects}}` - 项目列表
- `{{statistics}}` - 统计数据

---

**更新时间**：2026-03-12
**维护者**：小八爪 🐙
