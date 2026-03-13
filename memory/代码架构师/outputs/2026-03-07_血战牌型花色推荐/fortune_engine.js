/**
 * 麻将算命微信小程序 - 算法核心层
 * 实现血战到底牌型 & 花色命盘推荐功能
 * 根据生辰八字、星座、查询日期计算推荐牌型和花色
 */

// 牌型枚举
const PATTERN_TYPES = {
  PING_HU: '平胡',
  DUI_DUI_HU: '对对胡',
  QING_YI_SE: '清一色',
  HUN_YI_SE: '混一色',
  QI_DUI: '七对',
  QING_DUI: '清对',
  JIANG_DUI: '将对',
  MEN_QING: '门清',
  GANG_SHANG_HUA: '杠上花',
  GANG_SHANG_PAO: '杠上炮',
  QIANG_GANG_HU: '抢杠胡',
  HAI_DI_LAO_YUE: '海底捞月',
  XUE_ZHAN_DAO_DI: '血战到底'
};

// 花色枚举
const SUIT_TYPES = {
  WAN: '万',
  TONG: '筒',
  TIAO: '条'
};

// 五行枚举
const FIVE_ELEMENTS = {
  METAL: '金',
  WOOD: '木',
  WATER: '水',
  FIRE: '火',
  EARTH: '土'
};

// 牌型特征矩阵（根据算法文档定义）
const PATTERN_FEATURES = {
  [PATTERN_TYPES.PING_HU]: { aggressiveness: 0.3, complexity: 0.2, luck_factor: 0.5, risk_tolerance: 0.8, patience: 0.6 },
  [PATTERN_TYPES.DUI_DUI_HU]: { aggressiveness: 0.7, complexity: 0.5, luck_factor: 0.4, risk_tolerance: 0.6, patience: 0.4 },
  [PATTERN_TYPES.QING_YI_SE]: { aggressiveness: 0.8, complexity: 0.8, luck_factor: 0.7, risk_tolerance: 0.3, patience: 0.9 },
  [PATTERN_TYPES.HUN_YI_SE]: { aggressiveness: 0.6, complexity: 0.6, luck_factor: 0.5, risk_tolerance: 0.5, patience: 0.7 },
  [PATTERN_TYPES.QI_DUI]: { aggressiveness: 0.6, complexity: 0.7, luck_factor: 0.8, risk_tolerance: 0.5, patience: 0.8 },
  [PATTERN_TYPES.QING_DUI]: { aggressiveness: 0.9, complexity: 0.9, luck_factor: 0.6, risk_tolerance: 0.2, patience: 0.9 },
  [PATTERN_TYPES.JIANG_DUI]: { aggressiveness: 0.8, complexity: 0.8, luck_factor: 0.5, risk_tolerance: 0.3, patience: 0.8 },
  [PATTERN_TYPES.MEN_QING]: { aggressiveness: 0.4, complexity: 0.4, luck_factor: 0.6, risk_tolerance: 0.7, patience: 0.7 },
  [PATTERN_TYPES.GANG_SHANG_HUA]: { aggressiveness: 0.5, complexity: 0.3, luck_factor: 0.9, risk_tolerance: 0.6, patience: 0.5 },
  [PATTERN_TYPES.GANG_SHANG_PAO]: { aggressiveness: 0.6, complexity: 0.4, luck_factor: 0.8, risk_tolerance: 0.4, patience: 0.4 },
  [PATTERN_TYPES.QIANG_GANG_HU]: { aggressiveness: 0.7, complexity: 0.5, luck_factor: 0.7, risk_tolerance: 0.5, patience: 0.6 },
  [PATTERN_TYPES.HAI_DI_LAO_YUE]: { aggressiveness: 0.5, complexity: 0.3, luck_factor: 0.9, risk_tolerance: 0.7, patience: 0.8 },
  [PATTERN_TYPES.XUE_ZHAN_DAO_DI]: { aggressiveness: 0.9, complexity: 0.7, luck_factor: 0.6, risk_tolerance: 0.2, patience: 0.9 }
};

// 星座特征映射
const ZODIAC_FEATURES = {
  // 火象星座
  '白羊座': { aggressiveness: 0.2, complexity: 0.0, luck_factor: 0.0, risk_tolerance: 0.2, patience: -0.1 },
  '狮子座': { aggressiveness: 0.3, complexity: -0.1, luck_factor: 0.1, risk_tolerance: 0.3, patience: -0.2 },
  '射手座': { aggressiveness: 0.2, complexity: 0.1, luck_factor: 0.2, risk_tolerance: 0.2, patience: -0.1 },
  // 土象星座
  '金牛座': { aggressiveness: -0.1, complexity: 0.0, luck_factor: -0.1, risk_tolerance: 0.1, patience: 0.3 },
  '处女座': { aggressiveness: -0.1, complexity: 0.2, luck_factor: -0.2, risk_tolerance: 0.0, patience: 0.4 },
  '摩羯座': { aggressiveness: 0.0, complexity: 0.1, luck_factor: -0.1, risk_tolerance: 0.1, patience: 0.3 },
  // 风象星座
  '双子座': { aggressiveness: 0.1, complexity: 0.3, luck_factor: 0.1, risk_tolerance: 0.1, patience: -0.1 },
  '天秤座': { aggressiveness: 0.0, complexity: 0.2, luck_factor: 0.1, risk_tolerance: 0.0, patience: 0.0 },
  '水瓶座': { aggressiveness: 0.1, complexity: 0.3, luck_factor: 0.2, risk_tolerance: 0.1, patience: -0.1 },
  // 水象星座
  '巨蟹座': { aggressiveness: -0.1, complexity: 0.0, luck_factor: 0.3, risk_tolerance: -0.1, patience: 0.2 },
  '天蝎座': { aggressiveness: 0.1, complexity: 0.1, luck_factor: 0.2, risk_tolerance: 0.1, patience: 0.1 },
  '双鱼座': { aggressiveness: -0.2, complexity: 0.0, luck_factor: 0.4, risk_tolerance: -0.1, patience: 0.3 }
};

// 五行与花色映射
const ELEMENT_SUIT_MAPPING = {
  [FIVE_ELEMENTS.METAL]: SUIT_TYPES.TONG,   // 金 → 筒
  [FIVE_ELEMENTS.WOOD]: SUIT_TYPES.TIAO,    // 木 → 条
  [FIVE_ELEMENTS.WATER]: SUIT_TYPES.WAN,    // 水 → 万
  [FIVE_ELEMENTS.FIRE]: null,               // 火 → 无直接对应
  [FIVE_ELEMENTS.EARTH]: null               // 土 → 无直接对应
};

/**
 * 计算五行强度
 * @param {string|number} year - 生辰八字字符串（格式：YYYY-MM-DD HH:mm）或年份
 * @param {number} month - 月份（可选）
 * @param {number} day - 日期（可选）
 * @param {number} hour - 时辰（可选）
 * @returns {Object} 五行强度对象 {metal, wood, water, fire, earth}
 */
function calculateFiveElements(year, month, day, hour) {
  // 简化实现：根据生辰日期计算五行强度
  // 实际应用中应使用专业的八字计算库
  
  // 兼容两种调用方式：
  // 1. calculateFiveElements(2025, 3, 7, 14) - 4个参数
  // 2. calculateFiveElements('2025-03-07 14:00') - 1个日期字符串
  let date;
  if (typeof year === 'string') {
    // 日期字符串格式
    date = new Date(year);
  } else {
    // 4个独立参数格式
    date = new Date(year, month - 1, day, hour);
  }
  
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const h = date.getHours();
  
  // 简化算法：基于年月日时计算五行
  const elements = {
    metal: 0,
    wood: 0,
    water: 0,
    fire: 0,
    earth: 0
  };
  
  // 年份五行（简化）
  const yearLastDigit = y % 10;
  if ([0, 1].includes(yearLastDigit)) elements.metal += 0.3;
  if ([2, 3].includes(yearLastDigit)) elements.water += 0.3;
  if ([4, 5].includes(yearLastDigit)) elements.wood += 0.3;
  if ([6, 7].includes(yearLastDigit)) elements.fire += 0.3;
  if ([8, 9].includes(yearLastDigit)) elements.earth += 0.3;
  
  // 月份五行（简化）
  if ([3, 4].includes(m)) elements.wood += 0.2; // 春季
  if ([5, 6, 7].includes(m)) elements.fire += 0.2; // 夏季
  if ([8, 9].includes(m)) elements.metal += 0.2; // 秋季
  if ([10, 11, 12, 1, 2].includes(m)) elements.water += 0.2; // 冬季
  
  // 日期五行（简化）
  const dayMod = d % 5;
  if (dayMod === 0) elements.metal += 0.2;
  if (dayMod === 1) elements.wood += 0.2;
  if (dayMod === 2) elements.water += 0.2;
  if (dayMod === 3) elements.fire += 0.2;
  if (dayMod === 4) elements.earth += 0.2;
  
  // 时辰五行（简化）
  if (h >= 3 && h < 9) elements.wood += 0.2; // 寅卯辰辰
  if (h >= 9 && h < 15) elements.fire += 0.2; // 巳午未辰
  if (h >= 15 && h < 21) elements.metal += 0.2; // 申酉戌辰
  if (h >= 21 || h < 3) elements.water += 0.2; // 亥子丑辰
  
  // 归一化
  const total = Object.values(elements).reduce((sum, val) => sum + val, 0);
  if (total > 0) {
    Object.keys(elements).forEach(key => {
      elements[key] = elements[key] / total;
    });
  }
  
  return elements;
}

/**
 * 计算向量余弦相似度
 * @param {Array} vec1 - 向量1
 * @param {Array} vec2 - 向量2
 * @returns {number} 相似度分数
 */
function cosineSimilarity(vec1, vec2) {
  if (vec1.length !== vec2.length) return 0;
  
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;
  
  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i];
    norm1 += vec1[i] * vec1[i];
    norm2 += vec2[i] * vec2[i];
  }
  
  if (norm1 === 0 || norm2 === 0) return 0;
  
  return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
}

/**
 * 推荐牌型
 * @param {Object} fiveElements - 五行强度对象
 * @param {string} zodiacSign - 星座
 * @param {string} queryDate - 查询日期
 * @returns {Object} 推荐结果 {pattern, score, alternatives}
 */
function recommendPattern(fiveElements, zodiacSign, queryDate) {
  // 计算日期因子（使结果随日期变化）
  const date = new Date(queryDate);
  const dayOfMonth = date.getDate();
  const hourOfDay = date.getHours();
  const dateHash = dayOfMonth * 100 + hourOfDay;
  const dateFactor = (dateHash % 100) / 100; // 0-1 之间的随机因子

  // 计算用户特征向量
  const userFeatures = {
    aggressiveness: 0.5, // 基础值
    complexity: 0.5,
    luck_factor: 0.5,
    risk_tolerance: 0.5,
    patience: 0.5
  };

  // 五行特征影响
  userFeatures.aggressiveness += fiveElements.metal * 0.3 + fiveElements.fire * 0.4;
  userFeatures.complexity += fiveElements.wood * 0.2;
  userFeatures.luck_factor += fiveElements.water * 0.3;
  userFeatures.risk_tolerance += fiveElements.wood * 0.1 + fiveElements.fire * 0.3;
  userFeatures.patience += fiveElements.earth * 0.3 + fiveElements.water * 0.2 - fiveElements.metal * 0.2;

  // 日期因子微调（每日运势波动）
  userFeatures.aggressiveness += (dateFactor - 0.5) * 0.1;
  userFeatures.luck_factor += Math.sin(dateHash * 0.1) * 0.15;
  
  // 星座特征影响
  const zodiacFeature = ZODIAC_FEATURES[zodiacSign] || {};
  Object.keys(zodiacFeature).forEach(key => {
    if (userFeatures[key] !== undefined) {
      userFeatures[key] += zodiacFeature[key];
    }
  });
  
  // 归一化到[0,1]
  Object.keys(userFeatures).forEach(key => {
    userFeatures[key] = Math.max(0, Math.min(1, userFeatures[key]));
  });
  
  // 转换为向量
  const userVector = [
    userFeatures.aggressiveness,
    userFeatures.complexity,
    userFeatures.luck_factor,
    userFeatures.risk_tolerance,
    userFeatures.patience
  ];
  
  // 计算与每个牌型的相似度
  const patternScores = [];
  
  Object.keys(PATTERN_FEATURES).forEach(pattern => {
    const patternVector = [
      PATTERN_FEATURES[pattern].aggressiveness,
      PATTERN_FEATURES[pattern].complexity,
      PATTERN_FEATURES[pattern].luck_factor,
      PATTERN_FEATURES[pattern].risk_tolerance,
      PATTERN_FEATURES[pattern].patience
    ];
    
    const similarity = cosineSimilarity(userVector, patternVector);
    const score = Math.round(similarity * 100);
    
    patternScores.push({
      pattern,
      score
    });
  });
  
  // 按分数降序排序
  patternScores.sort((a, b) => b.score - a.score);
  
  // 返回推荐结果
  return {
    pattern: patternScores[0].pattern,
    score: patternScores[0].score,
    alternatives: patternScores.slice(1, 4).map(item => ({
      pattern: item.pattern,
      score: item.score
    }))
  };
}

/**
 * 推荐花色
 * @param {Object} fiveElements - 五行强度对象
 * @param {string} queryDate - 查询日期
 * @returns {Object} 推荐结果 {suit, score, breakdown}
 */
function recommendSuit(fiveElements, queryDate) {
  // 计算日期因子
  const date = new Date(queryDate);
  const dayOfMonth = date.getDate();
  const hourOfDay = date.getHours();
  const dateHash = dayOfMonth * 100 + hourOfDay;

  // 基础得分
  const suitScores = {
    [SUIT_TYPES.WAN]: fiveElements.water * 100,
    [SUIT_TYPES.TONG]: fiveElements.metal * 100,
    [SUIT_TYPES.TIAO]: fiveElements.wood * 100
  };

  // 添加日期随机波动（每日运势微调）
  suitScores[SUIT_TYPES.WAN] += Math.sin(dateHash * 0.13) * 5;
  suitScores[SUIT_TYPES.TONG] += Math.sin(dateHash * 0.17 + 1) * 5;
  suitScores[SUIT_TYPES.TIAO] += Math.sin(dateHash * 0.21 + 2) * 5;
  
  // 查询日期季节修正（复用已声明的 date 变量）
  const month = date.getMonth() + 1;
  
  // 春季（木旺）→ 条花色加分
  if (month >= 3 && month <= 5) {
    suitScores[SUIT_TYPES.TIAO] += 15;
  }
  // 夏季（火旺）→ 筒花色间接加分（火生土，土生金）
  else if (month >= 6 && month <= 8) {
    suitScores[SUIT_TYPES.TONG] += 10;
  }
  // 秋季（金旺）→ 筒花色加分
  else if (month >= 9 && month <= 11) {
    suitScores[SUIT_TYPES.TONG] += 15;
  }
  // 冬季（水旺）→ 万花色加分
  else {
    suitScores[SUIT_TYPES.WAN] += 15;
  }
  
  // 归一化到0-100分
  const maxScore = Math.max(...Object.values(suitScores));
  const minScore = Math.min(...Object.values(suitScores));
  
  Object.keys(suitScores).forEach(suit => {
    if (maxScore > minScore) {
      suitScores[suit] = Math.round(((suitScores[suit] - minScore) / (maxScore - minScore)) * 100);
    } else {
      suitScores[suit] = 33; // 平均分配
    }
  });
  
  // 找出最高分花色
  let recommendedSuit = SUIT_TYPES.WAN;
  let highestScore = 0;
  
  Object.keys(suitScores).forEach(suit => {
    if (suitScores[suit] > highestScore) {
      highestScore = suitScores[suit];
      recommendedSuit = suit;
    }
  });
  
  return {
    suit: recommendedSuit,
    score: highestScore,
    breakdown: suitScores
  };
}

/**
 * 获取运势推荐（主函数）
 * @param {string} birthDatetime - 生辰八字
 * @param {string} zodiacSign - 星座
 * @param {string} queryDate - 查询日期
 * @returns {Object} 完整推荐结果
 */
function getFortuneRecommendation(birthDatetime, zodiacSign, queryDate) {
  // 输入验证
  if (!birthDatetime || !zodiacSign || !queryDate) {
    return {
      error: '缺少必要参数',
      recommendation: getDefaultRecommendation()
    };
  }
  
  try {
    // 计算五行强度
    const fiveElements = calculateFiveElements(birthDatetime);
    
    // 推荐牌型
    const patternResult = recommendPattern(fiveElements, zodiacSign, queryDate);
    
    // 推荐花色
    const suitResult = recommendSuit(fiveElements, queryDate);
    
    // 生成运势描述
    const fortuneDescription = generateFortuneDescription(
      patternResult.pattern,
      patternResult.score,
      suitResult.suit,
      suitResult.score,
      fiveElements
    );
    
    return {
      success: true,
      birthDatetime,
      zodiacSign,
      queryDate,
      fiveElements,
      pattern: patternResult.pattern,
      patternScore: patternResult.score,
      alternativePatterns: patternResult.alternatives,
      suit: suitResult.suit,
      suitScore: suitResult.score,
      suitBreakdown: suitResult.breakdown,
      fortuneDescription,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('运势计算错误:', error);
    return {
      error: '运势计算失败',
      recommendation: getDefaultRecommendation()
    };
  }
}

/**
 * 生成默认推荐（用于错误处理）
 * @returns {Object} 默认推荐结果
 */
function getDefaultRecommendation() {
  return {
    pattern: PATTERN_TYPES.PING_HU,
    patternScore: 60,
    suit: SUIT_TYPES.WAN,
    suitScore: 50,
    fortuneDescription: '系统暂时无法计算您的专属运势，建议尝试平胡玩法，保持平和心态。'
  };
}

/**
 * 生成运势描述
 * @param {string} pattern - 推荐牌型
 * @param {number} patternScore - 牌型评分
 * @param {string} suit - 推荐花色
 * @param {number} suitScore - 花色评分
 * @param {Object} fiveElements - 五行强度
 * @returns {string} 运势描述文本
 */
function generateFortuneDescription(pattern, patternScore, suit, suitScore, fiveElements) {
  const patternDescriptions = {
    [PATTERN_TYPES.PING_HU]: '平胡是最基础的胡牌方式，适合稳扎稳打的风格。',
    [PATTERN_TYPES.DUI_DUI_HU]: '对对胡需要较强的进攻性，适合主动出击的玩家。',
    [PATTERN_TYPES.QING_YI_SE]: '清一色难度较高但收益大，需要耐心和专注。',
    [PATTERN_TYPES.HUN_YI_SE]: '混一色平衡了难度和收益，是稳健的选择。',
    [PATTERN_TYPES.QI_DUI]: '七对需要一定的运气成分，适合喜欢冒险的玩家。',
    [PATTERN_TYPES.QING_DUI]: '清对是高手向的牌型，需要精湛的技术。',
    [PATTERN_TYPES.JIANG_DUI]: '将对难度极高，适合追求极限的玩家。',
    [PATTERN_TYPES.MEN_QING]: '门清考验防守能力，适合谨慎的玩家。',
    [PATTERN_TYPES.GANG_SHANG_HUA]: '杠上花需要把握时机，运气成分较大。',
    [PATTERN_TYPES.GANG_SHANG_PAO]: '杠上炮风险较高，需要谨慎决策。',
    [PATTERN_TYPES.QIANG_GANG_HU]: '抢杠胡需要敏锐的观察力。',
    [PATTERN_TYPES.HAI_DI_LAO_YUE]: '海底捞月考验耐心和坚持。',
    [PATTERN_TYPES.XUE_ZHAN_DAO_DI]: '血战到底适合持久战的玩家。'
  };
  
  const suitDescriptions = {
    [SUIT_TYPES.WAN]: '万花色象征流动和变化，',
    [SUIT_TYPES.TONG]: '筒花色象征稳定和积累，',
    [SUIT_TYPES.TIAO]: '条花色象征成长和发展，'
  };
  
  // 根据评分生成评价
  let patternEvaluation = '';
  if (patternScore >= 80) {
    patternEvaluation = '与您的性格高度匹配';
  } else if (patternScore >= 60) {
    patternEvaluation = '比较适合您的风格';
  } else {
    patternEvaluation = '可以作为尝试选择';
  }
  
  let suitEvaluation = '';
  if (suitScore >= 80) {
    suitEvaluation = '缘分极深';
  } else if (suitScore >= 60) {
    suitEvaluation = '缘分不错';
  } else {
    suitEvaluation = '缘分一般';
  }
  
  // 五行分析
  const dominantElement = Object.keys(fiveElements).reduce((a, b) => 
    fiveElements[a] > fiveElements[b] ? a : b
  );
  
  const elementNames = {
    metal: '金',
    wood: '木',
    water: '水',
    fire: '火',
    earth: '土'
  };
  
  return `根据您的生辰八字分析，${patternDescriptions[pattern] || ''}
  
推荐您尝试${pattern}，${patternEvaluation}（匹配度${patternScore}%）。

花色方面，${suitDescriptions[suit] || ''}与您${suitEvaluation}（缘分值${suitScore}%）。

您的五行中${elementNames[dominantElement]}元素较强，这影响了您的打牌风格。建议保持平和心态，享受游戏过程。`;
}

// 导出模块
module.exports = {
  PATTERN_TYPES,
  SUIT_TYPES,
  FIVE_ELEMENTS,
  calculateFiveElements,
  recommendPattern,
  recommendSuit,
  getFortuneRecommendation,
  getDefaultRecommendation,
  generateFortuneDescription
};
