# p3_server — 服务层

**负责人：P3**

FastAPI 后端服务，连接算法层（P1）与数据层（P2），向前端（P4）提供统一的 REST API。

---

## 启动方式

```bash
# 在项目根目录执行
uvicorn p3_server.main:app --reload --port 8000
```

启动后访问 `http://localhost:8000/docs` 可查看自动生成的 Swagger 接口文档。

## 环境变量

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEPSEEK_API_KEY` | （必填） | DeepSeek API 密钥，用于 `/api/insights/suggestion` |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API 地址 |
| `DATABASE_PATH` | `data/neurolearn.db` | SQLite 数据库文件路径 |
| `CORS_ORIGINS` | `http://localhost:3000` | 允许跨域的前端地址，多个用逗号分隔 |

---

## 目录结构

```
p3_server/
├── main.py               # FastAPI 实例，注册路由和中间件
├── core/
│   ├── config.py         # 读取环境变量
│   └── exceptions.py     # 统一异常类型和错误响应格式
├── routers/              # HTTP 路由（薄层，只做参数解析和响应组装）
│   ├── cards.py
│   ├── questions.py
│   ├── state.py
│   ├── sessions.py
│   ├── dashboard.py
│   └── insights.py
├── services/             # 业务逻辑（调用 P1 算法 + P2 数据库）
│   ├── card_service.py
│   ├── quiz_service.py
│   ├── state_service.py
│   └── insight_service.py
└── schemas/              # Pydantic 请求/响应模型（P4 开发的类型依据）
    ├── card.py
    ├── question.py
    ├── state.py
    ├── session.py
    └── dashboard.py
```

---

## API 接口清单

所有接口以 `/api` 为前缀，请求/响应均为 JSON。

### 卡片 `/api/cards`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/cards/next` | 获取下一张待复习卡片，可传 `?chapter=N` 筛选章节 |
| `POST` | `/api/cards/{id}/review` | 提交复习评分（`quality: 0~5`），调用 P1 `review_card()` 更新记忆参数 |
| `GET` | `/api/cards/curve` | 返回各章节平均遗忘曲线（14天预测），供仪表盘折线图使用 |

### 题目 `/api/questions`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/questions/next` | 获取下一道题，传 `?chapter=N&difficulty=1/2/3` |
| `POST` | `/api/questions/{id}/answer` | 提交答案，返回对错、解析、P1 难度调度结果（下一题推荐难度和原因） |

### 状态 `/api/state`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/state/report` | 上报三路信号（行为 + SAM + 可选摄像头），调用 P1 `score_state()` 返回状态枚举和建议文本 |
| `GET` | `/api/state/history` | 返回最近 N 天状态记录，`?n_days=7`（默认），供洞察页面绘图 |

### 会话 `/api/sessions`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/sessions/start` | 创建新学习会话，返回 `session_id`（前端整个会话周期持有） |
| `POST` | `/api/sessions/{id}/end` | 结束会话，传入最终 SAM 得分，写入 `ended_at` |

### 洞察与仪表盘

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/insights/suggestion` | 汇总当前记忆和状态数据，调用 DeepSeek 生成即时建议和今日计划 |
| `GET` | `/api/dashboard/summary` | 返回仪表盘摘要：今日到期卡片数、连续学习天数、各章节记忆强度均值 |

---

## 调用关系

```
P4（前端）→ routers/ → services/ → P1 算法函数（直接 import）
                                  → P2 db_service.py（直接 import）
```

`routers/` 只负责 HTTP 层（参数校验、状态码、响应组装），业务逻辑全部在 `services/` 中。

## 错误响应格式

所有错误统一返回以下结构，由 `core/exceptions.py` 注册的全局处理器保证：

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "没有找到需要复习的卡片"
  }
}
```

---

## 依赖

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.7.0
sqlalchemy>=2.0.0
httpx>=0.27.0
```

安装：`pip install -r p3_server/requirements.txt`
