// pages/result/result.js
const app = getApp();

Page({
  data: {
    // 从全局数据获取运势结果
    userInfo: {},
    recommendedPattern: '',
    patternScore: 0,
    patternIcon: '🀄',
    patternDescription: '',
    winningProbability: 50,
    difficultyStars: [],
    difficultyLevel: '',
    patternTips: '',
    alternativePatterns: [],
    recommendedSuit: '',
    suitScore: { value: 0 },
    suitBreakdown: {},
    suitAnalysis: [],
    fiveElements: {},
    indicatorAngle: 0,
    fortunePeriod: '今日有效',
    overallFortune: '',
    calculationTime: '',
    recommendations: [],
    // 方位相关
    luckyDirection: '',
    luckyDirectionIcon: '',
    luckyDirectionDesc: '',
    allDirections: [],
    // 食物推荐
    foodRecommendation: {},
  },

  onLoad: function(options) {
    const result = app.globalData.fortuneResult;
    if (result) {
      // 生成测算时间显示
      const now = new Date();
      const calculationTime = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      // 从 patternResult 和 suitResult 读取数据
      const patternResult = result.patternResult || {};
      const suitResult = result.suitResult || {};

      // 计算获胜概率 (30-95之间)
      const winningProbability = Math.min(95, Math.max(30, patternResult.score || 50));

      // 根据牌型难度生成星星数组
      const difficultyStars = this.getDifficultyStars(patternResult.pattern);
      const difficultyLevel = this.getDifficultyLevel(patternResult.pattern);

      // 从 breakdown 获取各花色分数，兼容不同 key 格式
      const breakdown = suitResult.breakdown || {};
      const wanScore = breakdown['万'] || breakdown['wan'] || breakdown['WAN'] || 0;
      const tongScore = breakdown['筒'] || breakdown['tong'] || breakdown['TONG'] || 0;
      const tiaoScore = breakdown['条'] || breakdown['tiao'] || breakdown['TIAO'] || 0;
      
      // 找出最高分的花色作为推荐
      const scores = [
        { suit: '万', score: wanScore },
        { suit: '筒', score: tongScore },
        { suit: '条', score: tiaoScore }
      ];
      scores.sort((a, b) => b.score - a.score);
      const highestSuit = scores[0].suit;

      // 问题4修复：生成总体运势文本
      let overallFortuneText = '今日运势上佳，牌运亨通，宜积极进攻';
      if (typeof result.fortuneDescription === 'string' && result.fortuneDescription) {
        overallFortuneText = result.fortuneDescription;
      } else if (typeof result.fortuneText === 'string' && result.fortuneText) {
        overallFortuneText = result.fortuneText;
      } else if (result.fortuneText && typeof result.fortuneText === 'object') {
        overallFortuneText = result.fortuneText.description || result.fortuneText.recommendation || result.fortuneText.text || '今日运势上佳，牌运亨通，宜积极进攻';
      } else if (result.fortuneText) {
        overallFortuneText = String(result.fortuneText);
      }

      // 获取五行信息
      const fiveElements = result.fiveElements || this.calculateFiveElements(result);
      
      // 计算今日吉方
      const directionData = this.calculateLuckyDirection(fiveElements);
      
      // 计算食物推荐
      const foodRecommendation = this.calculateFoodRecommendation(fiveElements);

      this.setData({
        userInfo: result,
        recommendedPattern: patternResult.pattern || '',
        patternScore: patternResult.score || 0,
        patternDescription: result.fortuneText || '根据您的生辰八字为您推荐最佳牌型',
        winningProbability: winningProbability,
        difficultyStars: difficultyStars,
        difficultyLevel: difficultyLevel,
        patternTips: '保持心态平和享受游戏过程',
        alternativePatterns: patternResult.alternatives || [],
        recommendedSuit: highestSuit,  // 改为使用最高分的花色
        suitScore: {
          wan: { value: wanScore, active: highestSuit === '万' },
          tong: { value: tongScore, active: highestSuit === '筒' },
          tiao: { value: tiaoScore, active: highestSuit === '条' },
          value: scores[0].score
        },
        suitBreakdown: suitResult.breakdown || {},
        suitAnalysis: [],
        fiveElements: fiveElements,
        fortunePeriod: '今日有效',
        overallFortune: overallFortuneText,
        calculationTime: calculationTime,
        recommendations: ['建议保持当前手牌', '注意对手牌型'],
        // 指针指向最高分的花色
        indicatorAngle: this.getSuitAngle(highestSuit),
        // 方位数据
        luckyDirection: directionData.luckyDirection,
        luckyDirectionIcon: directionData.luckyDirectionIcon,
        luckyDirectionDesc: directionData.luckyDirectionDesc,
        allDirections: directionData.allDirections,
        // 食物推荐
        foodRecommendation: foodRecommendation,
      });
    }
  },

  // 根据用户信息计算五行
  calculateFiveElements: function(userInfo) {
    // 从生辰八字获取年柱，然后计算五行
    // 这里使用简化的算法：基于生日和时辰
    const year = userInfo.year || new Date().getFullYear();
    const month = userInfo.month || 1;
    const day = userInfo.day || 1;
    const hour = userInfo.hour || 0;
    
    // 天干地支对应五行 (简化版)
    const heavenlyStems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
    const earthlyBranches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
    const elementMap = {
      '甲': '木', '乙': '木',
      '丙': '火', '丁': '火',
      '戊': '土', '己': '土',
      '庚': '金', '辛': '金',
      '壬': '水', '癸': '水'
    };
    const branchElementMap = {
      '寅': '木', '卯': '木',
      '巳': '火', '午': '火',
      '申': '金', '酉': '金',
      '子': '水', '亥': '水',
      '辰': '土', '戌': '土', '丑': '土', '未': '土'
    };
    
    // 简化计算：基于年月日时生成天干地支
    const stemIndex = (year - 4) % 10;
    const branchIndex = (year - 4) % 12;
    const monthBranch = (month * 2) % 12;
    const dayBranch = (day * 2) % 12;
    const hourBranch = (hour * 2) % 12;
    
    const yearElement = elementMap[heavenlyStems[stemIndex]] || '木';
    const monthElement = branchElementMap[earthlyBranches[monthBranch]] || '木';
    const dayElement = branchElementMap[earthlyBranches[dayBranch]] || '火';
    const hourElement = branchElementMap[earthlyBranches[hourBranch]] || '水';
    
    // 统计五行数量，确定喜用神
    const elements = { 木: 0, 火: 0, 土: 0, 金: 0, 水: 0 };
    elements[yearElement]++;
    elements[monthElement]++;
    elements[dayElement]++;
    elements[hourElement]++;
    
    // 找出最弱的五行作为喜用神
    const minElement = Object.keys(elements).reduce((a, b) => 
      elements[a] < elements[b] ? a : b
    );
    
    return {
      yearElement,
      monthElement,
      dayElement,
      hourElement,
      preferredElement: minElement,
      elementCount: elements
    };
  },

  // 计算今日吉方
  calculateLuckyDirection: function(fiveElements) {
    const directionMap = {
      '东': { icon: '🧭', desc: '木生方位,利东方', isLucky: false },
      '南': { icon: '🔥', desc: '火旺南方,利南方', isLucky: false },
      '西': { icon: '⚪', desc: '金旺西方,利西方', isLucky: false },
      '北': { icon: '💧', desc: '水旺北方,利北方', isLucky: false },
      '东南': { icon: '🌲', desc: '木之方位', isLucky: false },
      '东北': { icon: '🏔️', desc: '土之方位', isLucky: false },
      '西南': { icon: '🏜️', desc: '土之方位', isLucky: false },
      '西北': { icon: '❄️', desc: '金之方位', isLucky: false }
    };
    
    // 根据喜用神确定吉方
    const preferredElement = fiveElements.preferredElement || '木';
    let luckyDirections = [];
    
    switch(preferredElement) {
      case '木':
        luckyDirections = ['东', '东南', '北'];
        break;
      case '火':
        luckyDirections = ['南', '东南', '东'];
        break;
      case '土':
        luckyDirections = ['东北', '西南', '南'];
        break;
      case '金':
        luckyDirections = ['西', '西北', '西南'];
        break;
      case '水':
        luckyDirections = ['北', '西北', '西'];
        break;
      default:
        luckyDirections = ['东', '南', '西', '北'];
    }
    
    // 生成所有方位
    const allDirections = [
      { name: '东', icon: '🧭', isLucky: luckyDirections.includes('东') },
      { name: '南', icon: '🔥', isLucky: luckyDirections.includes('南') },
      { name: '西', icon: '⚪', isLucky: luckyDirections.includes('西') },
      { name: '北', icon: '💧', isLucky: luckyDirections.includes('北') },
      { name: '东南', icon: '🌲', isLucky: luckyDirections.includes('东南') },
      { name: '东北', icon: '🏔️', isLucky: luckyDirections.includes('东北') },
      { name: '西南', icon: '🏜️', isLucky: luckyDirections.includes('西南') },
      { name: '西北', icon: '❄️', isLucky: luckyDirections.includes('西北') }
    ];
    
    const mainDirection = luckyDirections[0];
    
    return {
      luckyDirection: mainDirection + '方',
      luckyDirectionIcon: directionMap[mainDirection].icon,
      luckyDirectionDesc: directionMap[mainDirection].desc,
      allDirections: allDirections
    };
  },

  // 计算食物推荐
  calculateFoodRecommendation: function(fiveElements) {
    const preferredElement = fiveElements.preferredElement || '木';
    
    const foodMap = {
      '木': {
        name: '绿色蔬菜类',
        icon: '🥬',
        description: '今日宜食绿色蔬菜，如菠菜、黄瓜，有助运势',
        advice: '木属性食物有助于提升生机活力，保持身心舒畅，牌运亨通',
        items: [
          { name: '菠菜', icon: '🥬' },
          { name: '黄瓜', icon: '🥒' },
          { name: '西兰花', icon: '🥦' },
          { name: '青椒', icon: '🫑' },
          { name: '绿茶', icon: '🍵' }
        ]
      },
      '火': {
        name: '红色辛辣类',
        icon: '🌶️',
        description: '今日宜食红色食物和辛辣美味，激发热情',
        advice: '火属性食物能激发热情和活力，助力牌桌好运',
        items: [
          { name: '辣椒', icon: '🌶️' },
          { name: '胡萝卜', icon: '🥕' },
          { name: '番茄', icon: '🍅' },
          { name: '石榴', icon: '🍎' },
          { name: '红酒', icon: '🍷' }
        ]
      },
      '土': {
        name: '黄色主食类',
        icon: '🍚',
        description: '今日宜食黄色食物和谷物主食，稳定运势',
        advice: '土属性食物能稳定气场，带来踏实感，利于持久战',
        items: [
          { name: '米饭', icon: '🍚' },
          { name: '面包', icon: '🍞' },
          { name: '玉米', icon: '🌽' },
          { name: '南瓜', icon: '🎃' },
          { name: '土豆', icon: '🥔' }
        ]
      },
      '金': {
        name: '白色金属类',
        icon: '🥛',
        description: '今日宜食白色食物和奶制品，清爽开运',
        advice: '金属性食物能带来清新之气，头脑清晰，判断准确',
        items: [
          { name: '牛奶', icon: '🥛' },
          { name: '豆腐', icon: '🧈' },
          { name: '银耳', icon: '🍄' },
          { name: '梨', icon: '🍐' },
          { name: '白萝卜', icon: '🥔' }
        ]
      },
      '水': {
        name: '黑色海鲜类',
        icon: '🦐',
        description: '今日宜食黑色食物和海鲜，深海运势',
        advice: '水属性食物能带来深邃运势，灵感充沛，牌局顺畅',
        items: [
          { name: '海带', icon: '🌿' },
          { name: '黑木耳', icon: '🖤' },
          { name: '虾', icon: '🦐' },
          { name: '鱼', icon: '🐟' },
          { name: '咖啡', icon: '☕' }
        ]
      }
    };
    
    return foodMap[preferredElement] || foodMap['木'];
  },

  getSuitAngle: function(suit) {
    const angleMap = {
      '万': 0,
      '筒': 120,
      '条': 240
    };
    return angleMap[suit] || 0;
  },

  getDifficultyStars: function(pattern) {
    // 简单牌型: 2星, 中等: 3星, 困难: 4星
    const difficultyMap = {
      '平胡': ['full', 'full', 'empty', 'empty'],
      '碰碰胡': ['full', 'full', 'full', 'empty'],
      '清一色': ['full', 'full', 'full', 'full'],
      '七对': ['full', 'full', 'full', 'full'],
      '龙七对': ['full', 'full', 'full', 'full'],
      '清碰': ['full', 'full', 'full', 'full'],
      '十八罗汉': ['full', 'full', 'full', 'full'],
      '大三元': ['full', 'full', 'full', 'full'],
      '小四喜': ['full', 'full', 'full', 'full'],
      '大三喜': ['full', 'full', 'full', 'full'],
      '字一色': ['full', 'full', 'full', 'full'],
      '四杠子': ['full', 'full', 'full', 'full'],
      '九莲宝灯': ['full', 'full', 'full', 'full'],
      '四暗刻': ['full', 'full', 'full', 'full'],
    };
    return difficultyMap[pattern] || ['full', 'full', 'empty', 'empty'];
  },

  getDifficultyLevel: function(pattern) {
    const easyPatterns = ['平胡', '一般'];
    const mediumPatterns = ['碰碰胡', '七对', '断幺'];
    const hardPatterns = ['清一色', '龙七对', '清碰', '十八罗汉', '大三元', '小四喜', '大三喜', '字一色', '四杠子', '九莲宝灯', '四暗刻'];

    if (easyPatterns.includes(pattern)) return '简单';
    if (mediumPatterns.includes(pattern)) return '中等';
    if (hardPatterns.includes(pattern)) return '困难';
    return '中等';
  },

  goBack: function() {
    wx.navigateBack();
  },

  // 问题5修复：分享功能实现
  shareResult: function() {
    const that = this;
    // 启用分享菜单
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline'],
      success: function(res) {
        wx.showToast({
          title: '点击右上角菜单分享',
          icon: 'none',
          duration: 2000
        });
      },
      fail: function(err) {
        console.log('分享菜单调用失败', err);
        wx.showToast({
          title: '分享功能暂不可用',
          icon: 'none'
        });
      }
    });

    // 将结果保存到全局数据，以便分享后跳转
    const app = getApp();
    app.globalData.fortuneResult = {
      birthDate: that.data.userInfo.birthDate || that.data.userInfo,
      zodiac: that.data.userInfo.zodiac,
      fiveElements: that.data.fiveElements,
      patternResult: {
        pattern: that.data.recommendedPattern,
        score: that.data.patternScore,
        alternatives: that.data.alternativePatterns
      },
      suitResult: {
        suit: that.data.recommendedSuit,
        score: that.data.suitScore.value,
        breakdown: {
          '万': that.data.suitScore.wan?.value || 0,
          '筒': that.data.suitScore.tong?.value || 0,
          '条': that.data.suitScore.tiao?.value || 0
        }
      },
      fortuneText: that.data.patternDescription,
      fortuneDescription: that.data.overallFortune,
      timestamp: Date.now()
    };
  },

  // 微信分享给朋友
  onShareAppMessage: function() {
    return {
      title: `今日运势：推荐${this.data.recommendedSuit}${this.data.recommendedPattern}`,
      path: '/pages/input/input',
      imageUrl: '/images/share-cover.png'
    };
  },

  // 微信分享到朋友圈
  onShareTimeline: function() {
    return {
      title: `麻将今日运势 - 推荐${this.data.recommendedSuit}花色${this.data.recommendedPattern}`,
      query: '',
      imageUrl: '/images/share-cover.png'
    };
  },

  // 保存结果到相册
  saveResult: function() {
    const that = this;
    
    // 创建canvas来生成图片
    wx.showLoading({
      title: '生成图片中...',
      mask: true
    });

    // 使用 wx.createCanvasContext 生成分享图片
    const ctx = wx.createCanvasContext('shareCanvas', this);
    
    // 绘制背景
    ctx.setFillStyle('#FAF9F6');
    ctx.fillRect(0, 0, 300, 400);
    
    // 绘制标题
    ctx.setFillStyle('#2C3E50');
    ctx.setFontSize(20);
    ctx.setTextAlign('center');
    ctx.fillText('麻将今日运势', 150, 40);
    
    // 绘制推荐花色
    ctx.setFillStyle('#F57C00');
    ctx.setFontSize(32);
    ctx.fillText(this.data.recommendedSuit + ' - ' + this.data.suitScore.value + '分', 150, 90);
    
    // 绘制推荐牌型
    ctx.setFillStyle('#2C3E50');
    ctx.setFontSize(16);
    ctx.fillText(this.data.recommendedPattern, 150, 130);
    
    // 绘制吉方
    ctx.setFillStyle('#FFA500');
    ctx.setFontSize(18);
    ctx.fillText('今日宜坐: ' + this.data.luckyDirection, 150, 170);
    
    // 绘制五行
    ctx.setFillStyle('#2E7D32');
    ctx.setFontSize(14);
    ctx.fillText(this.data.fiveElements.preferredElement + '命 | 今日转运: ' + this.data.foodRecommendation.name, 150, 200);
    
    // 绘制底部提示
    ctx.setFillStyle('#7F8C8D');
    ctx.setFontSize(12);
    ctx.fillText('扫码体验麻将算命', 150, 380);
    
    ctx.draw(false, function() {
      // 绘制完成后导出图片
      setTimeout(function() {
        wx.canvasToTempFilePath({
          canvasId: 'shareCanvas',
          success: function(res) {
            const tempFilePath = res.tempFilePath;
            wx.saveImageToPhotosAlbum({
              filePath: tempFilePath,
              success: function() {
                wx.hideLoading();
                wx.showToast({
                  title: '已保存到相册',
                  icon: 'success'
                });
              },
              fail: function(err) {
                wx.hideLoading();
                // 需要授权
                if (err.errMsg.includes('auth deny')) {
                  wx.showModal({
                    title: '需要授权',
                    content: '需要授权保存图片到相册',
                    success: function(res) {
                      if (res.confirm) {
                        wx.openSetting();
                      }
                    }
                  });
                } else {
                  wx.showToast({
                    title: '保存失败',
                    icon: 'none'
                  });
                }
              }
            });
          },
          fail: function(err) {
            wx.hideLoading();
            wx.showToast({
              title: '生成图片失败',
              icon: 'none'
            });
            console.log('canvasToTempFilePath fail', err);
          }
        }, that);
      }, 500);
    });
  },

  // 再次测算
  retryCalculation: function() {
    wx.showModal({
      title: '确认',
      content: '确定要重新测算吗？',
      success: function(res) {
        if (res.confirm) {
          // 清除之前的数据
          app.globalData.fortuneResult = null;
          app.globalData.userInput = null;
          
          // 返回输入页
          wx.reLaunch({
            url: '/pages/input/input'
          });
        }
      }
    });
  },

  // 选择备选牌型
  selectAlternative: function(e) {
    const index = e.currentTarget.dataset.index;
    const pattern = this.data.alternativePatterns[index];
    if (pattern) {
      this.setData({
        recommendedPattern: pattern.pattern,
        patternScore: pattern.score,
        winningProbability: Math.min(95, Math.max(30, pattern.score))
      });
      wx.showToast({
        title: '已切换牌型',
        icon: 'none'
      });
    }
  },

  // 选择花色
  selectSuit: function(e) {
    const suit = e.currentTarget.dataset.suit;
    const suitNames = { wan: '万', tong: '筒', tiao: '条' };
    
    this.setData({
      recommendedSuit: suitNames[suit],
      indicatorAngle: this.getSuitAngle(suitNames[suit]),
      'suitScore.wan.active': suit === 'wan',
      'suitScore.tong.active': suit === 'tong',
      'suitScore.tiao.active': suit === 'tiao'
    });
  }
});
