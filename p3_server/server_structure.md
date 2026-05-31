p3_server/
├── main.py                      # FastAPI 入口，CORS 配置，路由注册
├── requirements.txt             # 依赖清单
├── core/
│   ├── config.py                # 环境变量（DEEPSEEK_API_KEY, DATABASE_PATH, CORS_ORIGINS）
│   └── exceptions.py            # 统一异常处理（AppError / NotFound / Validation / ServiceUnavailable）
├── schemas/                     # Pydantic 模型（P4 mock 数据依据）
│   ├── card.py                  # CardResponse, ReviewRequest, ReviewResponse, CurveResponse
│   ├── question.py              # QuestionResponse, AnswerRequest, AnswerResult
│   ├── state.py                 # StateEnum(5状态), BehaviorSignal, SAMScore, CameraScore, StateReport*
│   ├── session.py               # SessionStartResponse, SessionEndRequest, SessionEndResponse
│   └── dashboard.py             # DashboardSummary, InsightResponse
├── routers/                     # 路由骨架（Day 2+ 实现逻辑）
│   ├── cards.py                 # GET /api/cards/next | POST /api/cards/{id}/review | GET /api/cards/curve
│   ├── questions.py             # GET /api/questions/next | POST /api/questions/{id}/answer
│   ├── state.py                 # POST /api/state/report | GET /api/state/history
│   ├── sessions.py              # POST /api/sessions/start | POST /api/sessions/{id}/end
│   ├── dashboard.py             # GET /api/dashboard/summary
│   └── insights.py              # GET /api/insights/suggestion
└── services/                    # 业务逻辑占位（Day 2+ 实现）
    ├── card_service.py
    ├── quiz_service.py
    ├── state_service.py
    └── insight_service.py
