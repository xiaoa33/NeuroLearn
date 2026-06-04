# p4_frontend — 前端层

**负责人：P4**

Next.js 14 前端应用，包含五个学习页面、行为采集、状态展示和数据可视化。

---

## 启动方式

```bash
cd p4_frontend
npm install
npm run dev       # 开发模式，访问 http://localhost:3000
npm run build     # 生产构建
npm run start     # 运行生产构建
```

## 环境变量

在 `p4_frontend/` 目录下创建 `.env.local`：

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

默认指向本地 P3 服务，部署时替换为实际后端地址。

---

## 目录结构

```
p4_frontend/
├── app/                        # Next.js App Router（文件即路由）
│   ├── layout.tsx              # 根布局：左侧导航栏 + 右侧内容区
│   ├── page.tsx                # / 重定向到 /dashboard
│   ├── dashboard/page.tsx      # 记忆仪表盘
│   ├── learn/page.tsx          # 卡片学习
│   ├── quiz/page.tsx           # 章节测验
│   ├── review/page.tsx         # 复习队列
│   └── insights/page.tsx       # 学习洞察
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx         # 左侧图标导航栏
│   │   └── TopBar.tsx          # 顶部状态标签 + 学习时长
│   ├── cards/
│   │   ├── FlipCard.tsx        # 3D 翻转卡片（正面概念/背面答案）+ 0~5 评分按钮
│   │   └── CardQueue.tsx       # 复习队列列表
│   ├── quiz/
│   │   ├── QuestionCard.tsx    # 题目渲染 + 答题反馈
│   │   └── DifficultyBadge.tsx # 当前难度标签（简单/中等/困难）
│   ├── charts/
│   │   ├── ForgettingCurve.tsx # 遗忘曲线折线图（Recharts）
│   │   ├── MemoryHeatmap.tsx   # 章节记忆强度热力图
│   │   └── RadarChart.tsx      # 章节掌握度雷达图
│   └── state/
│       ├── SAMSlider.tsx       # SAM 量表（效价轴 + 唤醒轴两滑条）
│       ├── BehaviorTracker.tsx # 透明覆盖层，监听键鼠和页面可见性事件
│       └── StateIndicator.tsx  # 当前状态标签（心流/焦虑/…）
├── hooks/
│   ├── useBehavior.ts          # 行为采集 + 状态上报 Hook
│   └── useSession.ts           # 会话生命周期管理（start/end）
├── lib/
│   ├── api.ts                  # 所有后端接口调用函数（含 TypeScript 类型定义）
│   └── utils.ts                # 工具函数（时间格式化、记忆强度颜色映射等）
└── store/
    └── sessionStore.ts         # Zustand 全局状态
```

---

## 页面说明

### `/dashboard` 记忆仪表盘
展示今日待复习卡片数、连续学习天数、整体记忆强度，以及各章节遗忘曲线折线图和记忆强度热力图。调用 `getDashboardSummary()` 和 `getCardCurves()`。

### `/learn` 卡片学习
展示可翻转的 3D 记忆卡片，用户看完背面后按 0~5 分评分，触发 SM-2 复习计算并更新下次复习时间。

### `/quiz` 章节测验
选择章节后进入答题流程，题目难度由 P1 难度调度器动态决定，答错后显示解析，状态变化时出现难度调整提示气泡。

### `/review` 复习队列
按紧迫程度列出所有待复习卡片，可直接进入学习。

### `/insights` 学习洞察
展示 AI 生成的即时建议和今日计划、章节掌握度雷达图、最近 7 天状态历史折线图。

---

## 核心机制

### 行为采集：`useBehavior.ts`

监听三类浏览器事件采集行为信号，每 30 秒自动汇总上报一次（也在每次答题后触发）：

| 信号 | 采集方式 |
|------|----------|
| 答题正确率 | 记录每次 `recordAnswer(isCorrect, timeMs)` 调用 |
| 答题耗时 z-score | 与会话内历史均值比较（最近 20 条滚动窗口） |
| 页面失焦次数 | 监听 `visibilitychange` 事件 |

上报调用 `POST /api/state/report`，响应的状态枚举写入全局 store，TopBar 实时显示。

### 全局状态：`sessionStore.ts`（Zustand）

跨页面共享的会话数据：

| 字段 | 说明 |
|------|------|
| `sessionId` | 当前会话 ID，由 `/api/sessions/start` 返回，每个接口调用都需要传 |
| `currentState` | 最新状态枚举（`flow/anxiety/boredom/confusion/fatigue`） |
| `duration` | 本次学习时长（秒），每秒递增 |
| `samValence` / `samArousal` | SAMSlider 当前值，上报行为信号时一并携带 |

### 接口封装：`lib/api.ts`

所有 fetch 调用集中在此文件，页面和组件只 import 具名函数，不直接写 fetch。文件同时导出完整的 TypeScript 接口类型（`CardResponse`、`StateReportRequest` 等），与 P3 的 Pydantic schema 一一对应。

---

## 技术栈

| 库 | 用途 |
|----|------|
| Next.js 14 (App Router) | 路由、SSR、页面框架 |
| Tailwind CSS | 样式（深色主题，主色 `#0A1628`，强调色 `#00D4AA`） |
| Recharts | 遗忘曲线折线图、状态历史折线图、雷达图 |
| Zustand | 全局会话状态管理 |
| lucide-react | 图标 |
