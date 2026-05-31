// 行为信号采集组件（透明覆盖层，不影响正常交互）
// 监听 keydown、mousemove、visibilitychange 等原生 JS 事件
// 每 30s 汇总一次答题速度、正确率、失焦次数，调用 POST /api/state/report 上报
