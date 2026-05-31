// 行为信号采集 Hook
// 封装 keydown/mousemove/visibilitychange 监听逻辑，在组件挂载时注册、卸载时清理
// 每 30s 聚合信号调用 reportState，返回当前状态供组件使用
