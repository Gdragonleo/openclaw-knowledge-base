// app.js — 麻将算命微信小程序入口
App({
  /**
   * 小程序初始化
   */
  onLaunch() {
    console.log('[麻将算命] 小程序启动');
    // 初始化全局数据
    this.globalData = this.globalData || {};
  },

  /**
   * 小程序显示（前台）
   */
  onShow(options) {
    console.log('[麻将算命] 小程序进入前台', options);
  },

  /**
   * 小程序隐藏（后台）
   */
  onHide() {
    console.log('[麻将算命] 小程序进入后台');
  },

  /**
   * 全局错误监听
   */
  onError(msg) {
    console.error('[麻将算命] 全局错误', msg);
  },

  /**
   * 全局数据
   * fortuneResult: 算命结果，由 input 页写入，result 页读取
   */
  globalData: {
    fortuneResult: null,
  },
});
