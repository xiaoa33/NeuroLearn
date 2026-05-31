// 会话生命周期管理 Hook
// 页面首次加载时调用 POST /api/sessions/start 获取 session_id 并存入 sessionStore
// 页面卸载/关闭时调用 POST /api/sessions/{id}/end 结束会话
