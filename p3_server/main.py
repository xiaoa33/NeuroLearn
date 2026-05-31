from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ORIGINS
from .core.exceptions import register_exception_handlers
from .routers import cards, questions, state, sessions, dashboard, insights

app = FastAPI(
    title="NeuroLearn API",
    description="脑与认知科学自适应学习平台 - 后端服务",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(cards.router)
app.include_router(questions.router)
app.include_router(state.router)
app.include_router(sessions.router)
app.include_router(dashboard.router)
app.include_router(insights.router)


@app.get("/")
async def root():
    return {"service": "NeuroLearn API", "version": "3.0.0"}