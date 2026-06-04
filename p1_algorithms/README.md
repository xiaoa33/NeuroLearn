# p1_algorithms — 核心算法层

**负责人：P1**

纯 Python 算法实现，无数据库依赖，无网络调用，可独立单元测试。P3 通过 `import` 直接调用。

---

## 模块说明

### `schemas.py` — 数据类型定义

P1 与 P3 之间的类型契约，所有算法函数的输入输出均使用这里定义的数据类。

| 类型 | 说明 |
|------|------|
| `StateEnum` | 学习状态枚举：`flow / anxiety / boredom / confusion / fatigue`，基于 D'Mello & Graesser (2012) 五分类体系 |
| `CardData` | 知识卡片，含 SM-2 字段（`stability`、`easiness_factor`、`repetitions`）和复习时间 |
| `BehaviorSignal` | 行为信号：正确率、答题耗时 z-score、失焦次数、停顿时长（由前端每 30s 汇总上报） |
| `SAMScore` | 自报告情绪量表：效价轴 + 唤醒轴（各 0~10），基于 Russell (1980) 情绪环形模型 |
| `CameraScore` | 摄像头信号：专注度、眨眼频率、头部偏移（可选，由前端 face-api.js 提供） |

---

### `memory_engine.py` — 间隔重复引擎

**理论基础**：Ebbinghaus 遗忘曲线 + SM-2 算法（Wozniak & Gorzelanczyk, 1994）+ 睡眠记忆巩固（Stickgold, 2005）

**记忆强度公式**：R(t) = e^(−t / S)，其中 t 为距上次复习的天数，S 为记忆稳定性。

#### 函数

```python
review_card(card: CardData, quality: int, review_time: datetime | None = None) -> CardData
```
提交一次复习。`quality` 为 0~5 分（0=完全不会，5=非常熟悉），返回含新复习时间和记忆参数的卡片对象。

- `quality < 3`：重置计数，明天再复习
- `quality >= 3`：按 SM-2 序列延长间隔（1 天 → 6 天 → 按 EF 倍增）
- 21:00~23:59 复习：下次安排到次日 07:00，稳定性额外 ×1.2（睡眠巩固奖励）

```python
get_memory_strength(card: CardData, at_time: datetime | None = None) -> float
```
计算指定时刻的当前记忆保留率（0.0~1.0）。

```python
get_forgetting_curve(card: CardData, days: int = 7) -> list[dict]
```
预测未来 N 天的记忆强度，返回 `[{"day": int, "strength": float}, ...]`，供前端绘制遗忘曲线图。

---

### `state_scorer.py` — 学习状态评分

**理论基础**：Russell 情绪环形模型（效价×唤醒二维空间）+ D'Mello & Graesser 学习情绪体系（对应课程第 9、11 章）

#### 设计原则

SAM 自报告为**主要信号**，行为数据为**辅助修正**。SAM 滑条是用户对自身状态的直接表达，优先级高于行为推断；行为数据仅在有真实答题记录时才参与判断，避免默认值误触发。

信号权重（用于摄像头维度归一化，不决定判断优先级）：

| 信号来源 | 权重（有摄像头） | 权重（无摄像头） |
|----------|-----------------|-----------------|
| 行为信号 `BehaviorSignal` | 0.5 | 0.625 |
| 自报告 `SAMScore` | 0.3 | 0.375 |
| 摄像头 `CameraScore` | 0.2 | 0.0 |

#### 函数

```python
score_state(
    behavior: BehaviorSignal,
    sam: SAMScore,
    camera: CameraScore | None = None,
    session_duration_minutes: float = 0,
) -> tuple[StateEnum, float, dict[str, float]]
```

返回 `(状态枚举, 匹配度得分, 实际权重字典)`。摄像头不可用时权重自动重新归一化。

#### 三层判断逻辑（优先级从高到低）

**第一层：SAM 独立触发**（不依赖答题数据，在任意页面均有效）

| 状态 | SAM 条件 | 说明 |
|------|----------|------|
| `fatigue` | 唤醒 ≤ 2 | 用户明确报告精力耗尽，无需其他条件 |
| `anxiety` | 效价 ≤ 3 且 唤醒 ≥ 7 | Russell 模型第二象限：紧张/有压力 |
| `boredom` | 效价 ≤ 4 且 唤醒 ≤ 3 | Russell 模型第三象限：游离/提不起劲 |

**第二层：行为信号辅助**（仅当 `avg_time_zscore ≠ 0` 或 `accuracy ≠ 0.5` 时生效，即有真实答题数据）

| 状态 | 行为条件 | SAM 辅助条件 |
|------|----------|-------------|
| `anxiety` | 正确率 ≤ 40% 且 耗时 z > 1.0 | 效价 ≤ 5 |
| `confusion` | 正确率 < 60% 且 耗时 z > 1.0 | 失焦次数 ≤ 3 |
| `boredom` | 正确率 ≥ 90% 且 耗时 z < −1.0 | 无额外条件 |

**第三层：长时学习疲劳**

- 学习时长 ≥ 45 分钟 **且** 唤醒 ≤ 4 → `fatigue`
- 单独时长不触发（可能是专注），需结合低唤醒才认定疲劳

**兜底**：以上均不满足 → `flow`（最优学习状态）

---

### `difficulty_scheduler.py` — 自适应难度调度

**理论基础**：Csikszentmihalyi 心流理论（1990）——难度与能力匹配时进入最优学习状态。

难度三级：`1=简单 / 2=中等（默认）/ 3=困难`

#### 类 `DifficultyScheduler`

维护最近 3 题滑动窗口，每次答题后通过 `record_result()` 更新，通过 `next_question(state)` 获取推荐难度。

支持 `to_dict()` / `from_dict()` 序列化，供 P3 在请求间持久化调度器状态。

#### 函数 `next_difficulty`

```python
next_difficulty(sched: dict, state: StateEnum, recent: list[bool]) -> tuple[int, str]
```

P3 的无状态调用入口，批量录入结果后返回 `(推荐难度, 原因文本)`，原因文本直接用于前端提示气泡。

**调度规则**：
- 连续答错 3 题 → 强制降至简单（硬规则，优先于窗口逻辑）
- 窗口不足 3 题 → 维持当前难度（数据不足，不调整）
- 状态为 `anxiety` 或近期正确率 <40% → 降一级
- 状态为 `boredom` 或近期正确率 >85% → 升一级

---

## 运行测试

```bash
# 在项目根目录执行
pytest p1_algorithms/tests/ -v
```

测试覆盖 SM-2 各 quality 值边界、睡眠因子修正、状态判断规则、难度升降逻辑及序列化往返。

---

## 依赖关系

```
p1_algorithms/
├── schemas.py              ← 无外部依赖
├── memory_engine.py        ← 依赖 schemas.py
├── state_scorer.py         ← 依赖 schemas.py
├── difficulty_scheduler.py ← 依赖 schemas.py
└── tests/                  ← 依赖以上全部
```

P3 直接 `from p1_algorithms import ...` 调用，P1 不依赖 P2/P3/P4 的任何代码。
