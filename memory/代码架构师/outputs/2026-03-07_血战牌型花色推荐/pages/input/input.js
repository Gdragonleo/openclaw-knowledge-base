// pages/input/input.js
const fortuneEngine = require('../../fortune_engine.js');

// 时辰对照表
const TIME_MAP = [
  { hour: '23-1', name: '子时' },
  { hour: '1-3', name: '丑时' },
  { hour: '3-5', name: '寅时' },
  { hour: '5-7', name: '卯时' },
  { hour: '7-9', name: '辰时' },
  { hour: '9-11', name: '巳时' },
  { hour: '11-13', name: '午时' },
  { hour: '13-15', name: '未时' },
  { hour: '15-17', name: '申时' },
  { hour: '17-19', name: '酉时' },
  { hour: '19-21', name: '戌时' },
  { hour: '21-23', name: '亥时' },
];

// 星座列表
const ZODIAC_LIST = [
  '白羊座', '金牛座', '双子座', '巨蟹座',
  '狮子座', '处女座', '天秤座', '天蝎座',
  '射手座', '摩羯座', '水瓶座', '双鱼座',
];

// 问题2：选择器数据
const YEAR_LIST = Array.from({length: 127}, (_, i) => String(1900 + i));
const MONTH_LIST = Array.from({length: 12}, (_, i) => String(i + 1));
const DAY_LIST = Array.from({length: 31}, (_, i) => String(i + 1));
const HOUR_LIST = Array.from({length: 24}, (_, i) => String(i));

Page({
  data: {
    formData: {
      year: '',
      month: '',
      day: '',
      hour: '',
      zodiac: '',
    },
    errors: {
      year: '',
      month: '',
      day: '',
      hour: '',
    },
    timeMap: TIME_MAP,
    zodiacList: ZODIAC_LIST,
    showZodiacPanel: false,
    loading: false,
    // 问题2：输入模式
    inputMode: 'picker', // 'picker' | 'manual'
    yearList: YEAR_LIST,
    monthList: MONTH_LIST,
    dayList: DAY_LIST,
    hourList: HOUR_LIST,
    yearIndex: 0,
    monthIndex: 0,
    dayIndex: 0,
    hourIndex: 0,
  },

  onLoad() {
    // 问题1：检查是否有分享后的数据，有则直接跳转到结果页
    const app = getApp();
    if (app.globalData && app.globalData.fortuneResult) {
      wx.redirectTo({
        url: '/pages/result/result',
        fail: (err) => {
          console.error('跳转结果页失败', err);
        }
      });
    }
  },

  // === 输入处理 ===
  onYearInput(e) {
    const val = e.detail.value;
    this.setData({ 'formData.year': val, 'errors.year': '' });
  },

  onMonthInput(e) {
    const val = e.detail.value;
    this.setData({ 'formData.month': val, 'errors.month': '' });
  },

  onDayInput(e) {
    const val = e.detail.value;
    this.setData({ 'formData.day': val, 'errors.day': '' });
  },

  onHourInput(e) {
    const val = e.detail.value;
    this.setData({ 'formData.hour': val, 'errors.hour': '' });
  },

  // === 星座选择 ===
  onZodiacTap() {
    this.setData({ showZodiacPanel: !this.data.showZodiacPanel });
  },

  selectZodiac(e) {
    const zodiac = e.currentTarget.dataset.zodiac;
    this.setData({
      'formData.zodiac': zodiac,
      showZodiacPanel: false,
    });
  },

  clearZodiac() {
    this.setData({
      'formData.zodiac': '',
      showZodiacPanel: false,
    });
  },

  // 问题2：输入模式切换
  switchInputMode(e) {
    const mode = e.currentTarget.dataset.mode;
    this.setData({ inputMode: mode });
    // 切换模式时，自动填充表单数据
    if (mode === 'picker' && !this.data.formData.year) {
      this.setData({
        'formData.year': YEAR_LIST[0],
        'formData.month': MONTH_LIST[0],
        'formData.day': DAY_LIST[0],
        'formData.hour': HOUR_LIST[0],
      });
    }
  },

  // 问题2：选择器事件
  onYearChange(e) {
    const index = e.detail.value;
    this.setData({
      yearIndex: index,
      'formData.year': YEAR_LIST[index],
      'errors.year': '',
    });
  },

  onMonthChange(e) {
    const index = e.detail.value;
    this.setData({
      monthIndex: index,
      'formData.month': MONTH_LIST[index],
      'errors.month': '',
    });
  },

  onDayChange(e) {
    const index = e.detail.value;
    this.setData({
      dayIndex: index,
      'formData.day': DAY_LIST[index],
      'errors.day': '',
    });
  },

  onHourChange(e) {
    const index = e.detail.value;
    this.setData({
      hourIndex: index,
      'formData.hour': HOUR_LIST[index],
      'errors.hour': '',
    });
  },

  // === 表单校验 ===
  validateForm() {
    const { year, month, day, hour } = this.data.formData;
    let valid = true;
    const errors = { year: '', month: '', day: '', hour: '' };

    // 年份校验
    const y = parseInt(year, 10);
    if (!year || isNaN(y)) {
      errors.year = '请输入出生年份';
      valid = false;
    } else if (y < 1900 || y > 2026) {
      errors.year = '年份范围：1900 - 2026';
      valid = false;
    }

    // 月份校验
    const m = parseInt(month, 10);
    if (!month || isNaN(m)) {
      errors.month = '请输入出生月份';
      valid = false;
    } else if (m < 1 || m > 12) {
      errors.month = '月份范围：1 - 12';
      valid = false;
    }

    // 日期校验
    const d = parseInt(day, 10);
    if (!day || isNaN(d)) {
      errors.day = '请输入出生日期';
      valid = false;
    } else if (d < 1 || d > 31) {
      errors.day = '日期范围：1 - 31';
      valid = false;
    }

    // 时辰校验
    const h = parseInt(hour, 10);
    if (hour === '' || hour === undefined || isNaN(h)) {
      errors.hour = '请输入出生时辰（0-23）';
      valid = false;
    } else if (h < 0 || h > 23) {
      errors.hour = '时辰范围：0 - 23';
      valid = false;
    }

    this.setData({ errors });
    return valid;
  },

  // === 提交计算 ===
  onSubmit() {
    if (this.data.loading) return;
    if (!this.validateForm()) return;

    this.setData({ loading: true });

    const { year, month, day, hour, zodiac } = this.data.formData;
    const birthDate = {
      year: parseInt(year, 10),
      month: parseInt(month, 10),
      day: parseInt(day, 10),
      hour: parseInt(hour, 10),
    };

    try {
      // 调用算法引擎计算
      const fiveElements = fortuneEngine.calculateFiveElements(
        birthDate.year,
        birthDate.month,
        birthDate.day,
        birthDate.hour,
      );

      // 传入当前查询时间，确保每次算法带时间因子
      const queryDate = new Date().toISOString();
      const patternResult = fortuneEngine.recommendPattern(fiveElements, zodiac || null, queryDate);
      const suitResult = fortuneEngine.recommendSuit(fiveElements, queryDate);

      // 问题6修复：确保主牌型得分最高
      if (patternResult.alternatives && patternResult.alternatives.length > 0) {
        const maxAlternativeScore = Math.max(...patternResult.alternatives.map(a => a.score));
        if (maxAlternativeScore >= patternResult.score) {
          // 提高主牌型分数或降低备选分数，确保主牌型得分最高
          const newMainScore = maxAlternativeScore + 5;
          patternResult.score = newMainScore;
          // 可选：将备选牌型分数降低到主牌型之下
          patternResult.alternatives = patternResult.alternatives.map(alt => ({
            pattern: alt.pattern,
            score: Math.min(alt.score, newMainScore - 5)
          }));
        }
      }

      // 正确调用：生成运势描述文字（传入正确参数：牌型/分数/花色/分数/五行）
      const fortuneText = fortuneEngine.generateFortuneDescription(
        patternResult.pattern,
        patternResult.score,
        suitResult.suit,
        suitResult.score,
        fiveElements,
      );

      // 组装结果数据传递到结果页
      const resultData = {
        birthDate,
        zodiac: zodiac || '',
        fiveElements,
        patternResult,
        suitResult,
        fortuneText,
        timestamp: Date.now(),
      };

      // 存储到全局，结果页读取
      const app = getApp();
      app.globalData = app.globalData || {};
      app.globalData.fortuneResult = resultData;

      this.setData({ loading: false });

      wx.navigateTo({
        url: '/pages/result/result',
        fail: (err) => {
          console.error('页面跳转失败', err);
          wx.showToast({ title: '跳转失败，请重试', icon: 'none' });
        },
      });
    } catch (err) {
      console.error('算命引擎计算错误', err);
      this.setData({ loading: false });

      // 降级：使用默认推荐
      try {
        const defaultResult = fortuneEngine.getDefaultRecommendation();
        const app = getApp();
        app.globalData = app.globalData || {};
        app.globalData.fortuneResult = {
          birthDate: { year: parseInt(year), month: parseInt(month), day: parseInt(day), hour: parseInt(hour) },
          zodiac: zodiac || '',
          ...defaultResult,
          timestamp: Date.now(),
          isDefault: true,
        };
        wx.navigateTo({ url: '/pages/result/result' });
      } catch (e) {
        wx.showModal({
          title: '推算失败',
          content: '命盘推算出现异常，请检查输入信息后重试',
          showCancel: false,
        });
      }
    }
  },
});
