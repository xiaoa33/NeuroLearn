# NeuroLearn — 脑与认知科学自适应学习平台

## 项目结构

```
neurolearn/
├── p1_algorithms/      # P1 — 纯算法层（SM-2、状态评分、难度调度）
├── p2_knowledge/       # P2 — 知识库层（数据库、PDF解析、LLM内容生成）
├── p3_server/          # P3 — 后端服务层（FastAPI 路由与业务逻辑）
├── p4_frontend/        # P4 — 前端层（Next.js 全部页面与组件）
├── data/               # 共用 — 课件 PDF 原始文件（各章节）
├── docs/               # P5 — 项目报告、接口文档
├── requirements.txt    # Python 依赖（见下方说明）
└── README.md
```

---

## ⚠️ 依赖管理规范（重要）

**所有新增 Python 依赖必须写入 `requirements.txt`，不允许在本地安装后不记录。**

安装依赖：
```bash
pip install -r requirements.txt
```

新增依赖时：
1. 先在 `requirements.txt` 中添加包名
2. 再执行 `pip install -r requirements.txt`
3. 提交代码时连同 `requirements.txt` 的变更一起提交

前端依赖在 `p4_frontend/package.json` 中管理，同样要确保安装的包都写入 `package.json`。

---

## 接口契约（开发必读）

> **所有模块必须严格按照以下接口开发，不得擅自更改函数签名、参数名、返回字段名。**
> 接口是五人并行开发的唯一协作基础，任何变更必须提前与相关成员对齐。

---

### 6.1 P3 调用 P1 算法函数（Python `import`）

P1 以纯函数实现，P3 在 `services/` 中直接 import 调用。

| 函数签名 | 输入 | 返回值 | 所在文件 |
|---|---|---|---|
| `review_card(card: CardData, quality: int)` | `card`：卡片当前参数；`quality`：用户评分 0~5 | `next_review_at`（datetime）、`memory_strength`（float）、`stability`（float） | `memory_engine.py` |
| `get_memory_strength(card: CardData)` | `card`：含 `last_reviewed_at` 和 `stability` 字段 | `float` 0.0~1.0，当前记忆保留率 | `memory_engine.py` |
| `get_forgetting_curve(card: CardData, days: int)` | `card`：卡片参数；`days`：预测天数（建议7~14） | `list[{day: int, strength: float}]` | `memory_engine.py` |
| `score_state(behavior: BehaviorSignal, sam: SAMScore, camera: CameraScore \| None)` | 三路信号，camera 可选 | `StateEnum` + 得分 `float` + 实际权重 `dict` | `state_scorer.py` |
| `next_difficulty(sched: dict, state: StateEnum, recent: list[bool])` | 调度器状态、当前状态枚举、最近3题对错 | 推荐难度 `int`(1/2/3) + 调整原因 `reason: str` | `difficulty_scheduler.py` |

---

### 6.2 P3 调用 P2 数据库函数（Python `import`）

P3 只通过 `p2_knowledge/db_service.py` 读写数据，不直接操作 ORM 或 SQL。

| 函数签名 | 功能说明 | 所在文件 |
|---|---|---|
| `get_next_card(chapter=None) → CardData` | 按 `next_review_at` 最早顺序取一张卡片，`chapter=None` 不过滤 | `db_service.py` |
| `update_card_memory(card_id: int, updates: dict)` | 将 P1 计算结果写入 `cards` 表 | `db_service.py` |
| `get_all_curves() → list[CurveData]` | 返回所有卡片稳定性参数，供 P3 调 P1 组装遗忘曲线 | `db_service.py` |
| `get_next_question(chapter: int, difficulty: int) → QuestionData` | 按章节和难度随机取题（排除最近5次已答） | `db_service.py` |
| `save_response(session_id, q_id, is_correct, time_ms, difficulty)` | 写入一条答题记录 | `db_service.py` |
| `get_dashboard_summary() → DashboardData` | 聚合查询：到期卡片数、连续天数、各章节记忆强度均值 | `db_service.py` |
| `get_state_history(n_days=7) → list[StateRecord]` | 返回最近 n 天每次会话末尾的状态记录 | `db_service.py` |
| `create_session() → int` | 插入新会话行，返回自增 `session_id` | `db_service.py` |
| `end_session(session_id, final_state, sam_valence, sam_arousal)` | 更新会话 `ended_at`、`final_state` 和 SAM 得分 | `db_service.py` |

---

### 6.3 P4 调用 P3 HTTP 接口

所有接口以 `/api` 为前缀，请求/响应均为 JSON。P4 统一在 `lib/api.ts` 中封装，页面不直接写 `fetch`。

| 方法 | 路径 | 功能说明 |
|---|---|---|
| `GET` | `/api/cards/next` | 获取下一张待复习卡片（可传 `?chapter=` 过滤） |
| `POST` | `/api/cards/{id}/review` | 提交复习结果，body：`{quality: 0-5, session_id}` |
| `GET` | `/api/cards/curve` | 返回所有卡片遗忘曲线数据 |
| `GET` | `/api/questions/next` | 获取下一道题，传 `?chapter=&difficulty=` |
| `POST` | `/api/questions/{id}/answer` | 提交答题，body：`{answer, time_ms, session_id}` |
| `POST` | `/api/state/report` | 上报三路信号，body：行为指标 + SAM 量表 |
| `GET` | `/api/state/history` | 返回最近7天状态变化时序 |
| `POST` | `/api/sessions/start` | 创建新学习会话，返回 `{session_id}` |
| `POST` | `/api/sessions/{id}/end` | 结束会话，body：`{sam_valence, sam_arousal}` |
| `GET` | `/api/insights/suggestion` | 触发 AI 建议生成，返回即时建议和今日计划 |
| `GET` | `/api/dashboard/summary` | 返回仪表盘汇总数据 |

#### 关键请求/响应示例

**GET `/api/cards/next` 响应：**
```json
{ "id": 1, "concept": "长时程增强（LTP）", "front": "LTP 的突触机制是什么？",
  "back": "...", "memory_strength": 0.72, "chapter": 8 }
```

**POST `/api/cards/{id}/review` 请求体：**
```json
{ "quality": 4, "session_id": "abc123" }
```
**响应：**
```json
{ "next_review_at": "2026-06-03T07:00:00", "new_memory_strength": 0.95, "interval_days": 6 }
```

**POST `/api/state/report` 请求体：**
```json
{
  "accuracy": 0.75, "avg_time_zscore": 0.3, "defocus_count": 1,
  "sam_valence": 7.0, "sam_arousal": 6.5,
  "session_id": "abc123"
}
```
**响应：**
```json
{ "state": "flow", "suggestion_text": "状态很好，继续保持！" }
```

**GET `/api/insights/suggestion` 响应：**
```json
{ "immediate_tip": "...", "daily_plan": "..." }
```

---

## 环境变量

在项目根目录创建 `.env` 文件（不要提交到代码库）：

```
DEEPSEEK_API_KEY=your_key_here
DATABASE_URL=sqlite:///./neurolearn.db
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 启动方式

**后端（P3）：**
```bash
cd p3_server
uvicorn main:app --reload --port 8000
```

**前端（P4）：**
```bash
cd p4_frontend
npm install
npm run dev
```

**首次初始化知识库（P2，仅运行一次）：**
```bash
cd p2_knowledge
python scripts/seed_db.py
python scripts/generate_cards.py
python scripts/generate_questions.py
```
