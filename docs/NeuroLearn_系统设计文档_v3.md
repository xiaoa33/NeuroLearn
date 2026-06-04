**NeuroLearn**

脑与认知科学自适应学习平台 · 系统设计文档

v3.0 · 2026

# **阅读本文档前：项目整体说明**

本文档是 NeuroLearn 项目的系统设计文档，供五位开发成员参考。请在开始开发前完整阅读本章，了解整个项目的目标、各部分的用途以及你的工作在整体中的位置。

## **这是一个什么项目？**

NeuroLearn 是一个专门用来学习《脑与认知科学基础》这门课程的 Web 学习平台。它的核心思路是：用这门课所讲的神经科学理论，来指导我们自己学习这门课——也就是「用脑科学原理来学脑科学」。

举个例子：课程第8章讲了海马体如何在睡眠中巩固记忆、LTP（长时程增强）是记忆形成的突触机制。我们的平台就据此设计了间隔复习功能：在你「快要遗忘但还没完全忘」的时间点推送复习，并在睡前学习后优先安排次日早晨复习，这正是睡眠记忆巩固理论的直接应用。

类似地，课程第9章讲情绪对认知的影响、第11章讲注意资源的有限性，我们据此设计了学习状态感知：当系统检测到你焦虑或疲劳时，自动降低题目难度或提示休息，而不是继续强迫学习。

## **项目分为哪几个部分？**

整个项目分为四个开发模块，每人负责一个，通过约定好的接口协作：

| **模块** | **负责人** | **用一句话说清楚它在做什么** |
| --- | --- | --- |
| **p1_algorithms/** | P1 | 三个核心算法的纯计算逻辑：「什么时候该复习」「现在状态是心流还是焦虑」「下一题应该出难还是出简单」。只负责计算，不碰数据库，不发网络请求，给输入返回输出。 |
| **p2_knowledge/** | P2 | 知识库的建立与维护：读取课件 PDF，调用 DeepSeek 生成知识卡片和测验题目，存入数据库；同时提供数据库读写接口供 P3 调用。是整个项目数据的来源和仓库。 |
| **p3_server/** | P3 | 后端服务层，连接一切：接收前端的请求，调用 P1 的算法计算结果，调用 P2 的接口读写数据，再把结果返回给前端。前端看到的所有数据都经过这里。 |
| **p4_frontend/** | P4 | 用户看到的全部界面：仪表盘、卡片学习、章节测验、复习队列、学习洞察五个页面，以及行为采集、状态展示等交互逻辑。调用 P3 提供的接口获取数据并展示。 |

## **三个核心算法：用在哪里，解决什么问题？**

P1 负责实现以下三个算法，它们是整个平台区别于普通背单词 App 的关键所在。

### **算法一：间隔重复引擎（SM-2 + 睡眠因子修正）**

**解决的问题：什么时候该复习一张卡片？**

背景：人类记忆会随时间衰减（Ebbinghaus 遗忘曲线），但如果在「快要遗忘」的节点及时复习，记忆稳定性会大幅提升，下次遗忘的速度也会变慢。这正是海马体记忆巩固的神经机制——重复激活突触，促进 LTP 形成。

实现：每次复习一张卡片后，用户给自己的掌握程度打分（0-5分）。算法根据分数计算这张卡片下次应该在几天后出现：答得越好，下次间隔越长（最长可达数月）；答错则重置，明天再来。此外，如果用户在晚上9点后学习，系统会将复习时间优先安排在次日早晨，利用睡眠巩固记忆的神经科学依据。

效果：每张卡片都有一个「记忆强度」值（0~1），在仪表盘以遗忘曲线图的形式可视化展示，让用户直观看到哪些知识正在被遗忘、哪些已经牢固掌握。

### **算法二：学习状态评分（三路信号融合）**

**解决的问题：用户现在是专注、焦虑、无聊还是疲劳？**

背景：课程第9章指出情绪状态直接影响记忆编码效率；第11章指出注意资源是有限的，持续学习会导致注意衰竭。D'Mello & Graesser 的研究专门针对学习场景定义了五类状态：心流（最佳学习状态）、焦虑（难度太高）、无聊（难度太低）、困惑（需要额外解释）、疲劳（需要休息）。

实现：系统从三个渠道采集信号，加权融合得出当前状态——行为信号（答题速度、正确率、页面失焦次数，权重50%）、用户自报告的 SAM 量表（效价和唤醒两个滑条，权重30%）、可选的摄像头面部表情（权重20%）。

效果：状态结果实时显示在页面顶部，并驱动算法三的难度调度。同时记录历史数据，在洞察页面展示用户的状态变化趋势。

### **算法三：自适应难度调度**

**解决的问题：下一道题应该出简单、中等还是困难？**

背景：心流理论（Csikszentmihalyi）指出，当任务难度与个人能力精确匹配时，人会进入最佳学习状态；难度过高导致焦虑，过低导致无聊。

实现：维护一个「最近3题」的滑动窗口，结合算法二的状态判断，动态调整难度级别（简单/中等/困难）。检测到焦虑时降低难度并插入已掌握的卡片建立信心；检测到无聊时提升难度或推送跨章节联系题；检测到疲劳时强制弹出休息提示。

效果：用户在测验时无需手动选择难度，系统自动保持在合适的挑战水平，最大化学习效率。

## **数据库的目的：存什么，为什么这样设计？**

项目使用 SQLite 数据库，由 P2 负责建表和维护。数据库存储四类数据：

· 知识卡片（cards 表）：LLM 根据课件生成的概念卡片，以及每张卡片的记忆参数（稳定性、下次复习时间等）。这是间隔重复算法运行的基础数据。

· 题库（questions 表）：每张卡片对应的三道测验题（简单/中等/困难各一道），由 LLM 生成。

· 学习会话（sessions 表）：每次打开平台学习算一个会话，记录开始/结束时间、本次状态、完成情况。供洞察页面展示历史趋势。

· 答题记录（question_responses 表）：每道题的作答情况，包括耗时和当时的难度级别。供状态评分算法计算行为信号。

P2 还负责用 pdfplumber 读取课件 PDF，提取各章文字内容，再调用 DeepSeek API 批量生成卡片和题目写入数据库。这个步骤只需要在开发时一次性运行，之后数据库就已备好，P3 和 P4 直接使用。

## **各模块之间如何协作？**

四个模块通过「接口契约」协作——每个模块只需要知道「我能调用什么函数/接口、传什么参数、得到什么返回值」，不需要了解对方内部怎么实现的。具体的接口定义见第六章。协作关系如下：

· P4（前端）向 P3（服务端）发 HTTP 请求，获取卡片、题目、状态判断结果、学习建议等数据。

· P3（服务端）收到请求后，调用 P1（算法）的纯函数做计算，调用 P2（数据库）的函数读写数据，组装结果返回 P4。

· P2（数据库）在开发初期先跑脚本生成知识库内容，之后对外只暴露 db_service.py 里的函数供 P3 调用。

· P1（算法）不依赖任何人，独立开发独立测试，P3 直接 import 调用。

这种设计的好处是：四人可以在约定好接口格式后完全并行开发，互不等待。P4 可以先用 mock 数据（假数据）开发页面，等 P3 接口完成后再替换为真实数据。

# **一、项目概述**

NeuroLearn 是一个面向《脑与认知科学基础》课程的 Web 学习平台，将课程核心理论（学习与记忆、情绪认知、注意机制）直接转化为系统设计依据，实现「用神经科学原理指导神经科学学习」的闭环。

**核心功能：**

· 基于 SM-2 + 睡眠因子修正的间隔重复引擎（对应第8章 学习与记忆）

· 三路信号融合的学习状态感知（对应第9章 情绪、第11章 注意与意识）

· LLM 驱动的知识卡片与题库自动生成（Claude API，JSON mode）

· 遗忘曲线实时可视化 + 个性化 AI 学习建议

**技术栈：**

| **层级** | **技术选型与说明** |
| --- | --- |
| 前端 | Next.js 14（App Router）+ Tailwind CSS + shadcn/ui + Recharts — 路由、页面、组件、样式统一在一个框架内管理，由 P4 独立完成 |
| 后端框架 | Python 3.11 + FastAPI + SQLAlchemy — 提供 REST API，由 P3 负责路由与业务逻辑 |
| 数据库 | SQLite — 存储卡片记忆参数（SM-2 字段）、题库、答题记录、会话状态，由 P2 负责建表与 CRUD 接口 |
| PDF 解析 | pdfplumber — 本地提取课件 PDF 文本，作为 LLM 输入上下文，无需向量数据库，由 P2 负责 |
| LLM 服务 | DeepSeek API（deepseek-chat）— 读取课件文本，批量生成卡片与题目；实时生成学习建议。JSON mode 结构化输出，由 P2 负责 Prompt 工程与调用 |
| 核心算法 | SM-2 间隔重复引擎、三路信号状态评分（行为×0.5 + SAM×0.3 + 摄像头×0.2）、自适应难度调度，由 P1 以纯函数形式实现 |
| 行为监测 | 原生 JS 事件监听（keydown / mousemove / visibilitychange），每 30s 汇总上报，集成在前端 P4 代码中 |

# **二、代码目录结构**

项目按成员职责划分为四个顶层文件夹，每人独立负责一个文件夹，互不干扰，仅通过接口协议（第六章）协作。P5 负责 docs/ 文档目录。

## **2.1 顶层结构**

| neurolearn/   ├── p1_algorithms/     # P1 负责 — 纯算法层（无 I/O，无网络，可独立单测）   ├── p2_knowledge/      # P2 负责 — 数据库 + PDF解析 + LLM内容生成   ├── p3_server/         # P3 负责 — FastAPI 路由 + 业务逻辑（调用P1/P2）   ├── p4_frontend/       # P4 负责 — Next.js 前端（所有页面/组件/交互）   ├── data/              # 共用 — 课件 PDF 原始文件（各章节）   └── docs/              # P5 负责 — 项目报告、接口文档、设计说明 |
| --- |

## **2.2 P1 — 算法层（p1_algorithms/）**

职责：实现所有核心算法，以纯 Python 函数暴露，无数据库依赖，无网络调用，可独立单元测试。P3 直接 import 调用。

| p1_algorithms/   ├── memory_engine.py        # SM-2 间隔重复算法   │     # review_card(card, quality) → 返回下次复习时间、新记忆强度   │     # get_memory_strength(card) → 当前记忆保留率 float(0~1)   │     # get_forgetting_curve(card, days) → 未来N天强度预测列表   │   ├── state_scorer.py         # 三路信号状态评分   │     # score_state(behavior, sam, camera=None) → 状态枚举 + 得分   │     # 输出状态：flow / anxiety / boredom / confusion / fatigue   │   ├── difficulty_scheduler.py # 自适应难度调度   │     # next_difficulty(scheduler_state, state, recent_results) → 1/2/3   │     # 维护最近3题窗口，结合状态决定升/降/保持难度   │   ├── schemas.py              # 算法层数据类定义（dataclass）   │     # CardData, BehaviorSignal, SAMScore, CameraScore, StateEnum   │   └── tests/                  # 单元测试（pytest）         ├── test_memory.py    # SM-2 各 quality 值输出验证         ├── test_scorer.py    # 三路信号融合逻辑验证         └── test_scheduler.py # 难度窗口升降逻辑验证 |
| --- |

## **2.3 P2 — 知识库层（p2_knowledge/）**

职责：课件 PDF 解析、DeepSeek API 调用生成内容、SQLite 数据库建表与 CRUD。对外暴露 db_service.py 函数供 P3 调用，对外暴露 scripts/ 脚本供一次性运行生成数据。

| p2_knowledge/   ├── database.py             # SQLAlchemy engine 初始化，Session 工厂   │   ├── models/                 # ORM 模型（对应 SQLite 表结构）   │     ├── card.py           # Card 表：概念卡片 + SM-2 参数字段   │     ├── question.py       # Question 表：题目 + 选项 + 答案 + 难度   │     ├── session.py        # LearningSession 表：会话记录 + 状态快照   │     └── response.py       # QuestionResponse 表：每次答题记录   │   ├── db_service.py           # 数据库 CRUD 接口（P3 调用的唯一入口）   │     # get_next_card(chapter) / update_card_memory(id, updates)   │     # get_next_question(chapter, difficulty) / save_response(...)   │     # get_all_curves() / get_dashboard_summary() / get_state_history()   │     # create_session() / end_session(id, state, sam)   │   ├── pdf_parser.py           # 课件 PDF 文本提取（pdfplumber）   │     # extract_text(pdf_path) → str  按页提取并拼接   │     # extract_by_chapter(data_dir) → {chapter: text}  批量处理   │   ├── llm_client.py           # DeepSeek API 封装   │     # generate_json(system, user, schema) → dict  统一调用入口   │     # 包含重试逻辑（最多3次）、JSON 解析失败回退处理   │   ├── scripts/                # 离线内容生成脚本（一次性运行）   │     ├── seed_db.py        # 初始化数据库表结构   │     ├── generate_cards.py # PDF文本 → DeepSeek → 批量写入 cards 表   │     │     # 每章 PDF 独立调用，每次生成 20 张，输出 JSON 格式卡片   │     ├── generate_questions.py  # cards 表内容 → DeepSeek → 写入 questions 表   │     │     # 每张卡片生成 3 道题（简单/中等/困难各1道）   │     └── refresh_chapter.py    # 重新生成指定章节内容（不覆盖记忆参数）   │   └── prompts/                # Prompt 模板（与代码分离，便于迭代）         ├── card_generation.txt   # 卡片生成系统提示词         └── question_generation.txt # 题目生成系统提示词 |
| --- |

## **2.4 P3 — 服务层（p3_server/）**

职责：FastAPI 应用入口、所有 HTTP 路由、业务逻辑编排。调用 p1_algorithms/ 的算法函数和 p2_knowledge/db_service.py 的数据接口，组合成前端需要的 API 响应。

| p3_server/   ├── main.py                 # FastAPI app 实例，注册所有路由，配置 CORS   │   ├── routers/                # 按功能拆分的路由模块   │     ├── cards.py          # GET /api/cards/next   │     │                     # POST /api/cards/{id}/review   │     │                     # GET /api/cards/curve   │     ├── questions.py      # GET /api/questions/next   │     │                     # POST /api/questions/{id}/answer   │     ├── state.py          # POST /api/state/report（三路信号→状态判断）   │     │                     # GET /api/state/history   │     ├── sessions.py       # POST /api/sessions/start   │     │                     # POST /api/sessions/{id}/end   │     ├── insights.py       # GET /api/insights/suggestion（调 DeepSeek）   │     └── dashboard.py      # GET /api/dashboard/summary   │   ├── schemas/                # Pydantic 请求/响应模型（接口契约）   │     ├── card.py           # CardResponse, ReviewRequest, CurveResponse   │     ├── question.py       # QuestionResponse, AnswerRequest, AnswerResult   │     ├── state.py          # StateReportRequest, StateReportResponse   │     └── dashboard.py      # DashboardSummary, InsightResponse   │   ├── services/               # 业务逻辑编排（路由调用这里，这里调P1/P2）   │     ├── card_service.py   # 取卡 → 调P1算法 → 调P2写库 → 返回结果   │     ├── quiz_service.py   # 取题 → 调P1难度调度 → 调P2记录答题   │     ├── state_service.py  # 收信号 → 调P1评分 → 调P2存状态 → 返建议   │     └── insight_service.py # 组装上下文 → 调DeepSeek → 返回建议文本   │   └── core/         ├── config.py         # 环境变量读取（DEEPSEEK_API_KEY 等）         └── exceptions.py     # 统一异常处理与错误响应格式 |
| --- |

## **2.5 P4 — 前端层（p4_frontend/）**

职责：完整的 Next.js 前端应用，包含所有页面、组件、状态管理、行为采集。使用 shadcn/ui 组件库，Tailwind CSS 样式，Recharts 绘图。

| p4_frontend/   ├── app/                    # Next.js App Router（每个文件夹即一个路由）   │     ├── layout.tsx        # 根布局：左侧导航栏 + 右侧内容区   │     ├── page.tsx          # / 首页（重定向到 /dashboard）   │     ├── dashboard/   │     │     └── page.tsx    # /dashboard 记忆仪表盘   │     ├── learn/   │     │     └── page.tsx    # /learn 卡片学习   │     ├── quiz/   │     │     └── page.tsx    # /quiz 章节测验   │     ├── review/   │     │     └── page.tsx    # /review 复习队列   │     └── insights/   │           └── page.tsx    # /insights 学习洞察   │   ├── components/   │     ├── layout/   │     │     ├── Sidebar.tsx       # 左侧图标导航栏   │     │     └── TopBar.tsx        # 顶部：当前状态标签 + 学习时长   │     ├── cards/   │     │     ├── FlipCard.tsx      # 3D翻转卡片（正面概念/背面答案）   │     │     └── CardQueue.tsx     # 复习队列列表展示   │     ├── quiz/   │     │     ├── QuestionCard.tsx  # 题目渲染（选择/判断）+ 答题反馈   │     │     └── DifficultyBadge.tsx # 当前难度标签（简单/中等/困难）   │     ├── charts/   │     │     ├── ForgettingCurve.tsx  # 遗忘曲线折线图（Recharts）   │     │     ├── MemoryHeatmap.tsx    # 章节记忆强度热力图   │     │     └── RadarChart.tsx       # 章节掌握度雷达图   │     └── state/   │           ├── SAMSlider.tsx        # SAM量表（效价轴+唤醒轴两滑条）   │           ├── BehaviorTracker.tsx  # 透明覆盖层，采集键鼠行为   │           └── StateIndicator.tsx   # 当前状态标签（心流/焦虑…）   │   ├── hooks/   │     ├── useBehavior.ts      # 行为信号采集 Hook（30s 汇总上报）   │     └── useSession.ts       # 会话生命周期管理（start/end）   │   ├── lib/   │     ├── api.ts             # 所有后端 API 调用函数（fetch 封装）   │     └── utils.ts           # 时间格式化、记忆强度颜色映射等工具函数   │   └── store/         └── sessionStore.ts    # Zustand 全局状态（session_id、当前状态、时长） |
| --- |

# **三、核心算法详细设计**

## **3.1 间隔重复引擎（memory_engine.py）**

理论基础：Ebbinghaus 遗忘曲线 + SuperMemo SM-2 算法 + 神经科学睡眠巩固理论（第8章）。

记忆强度公式（可视化展示用）：

R(t) = e^( -t / S )

R: 记忆保留率（0~1），t: 距上次复习的天数，S: 记忆稳定性（随复习次数增长）

SM-2 核心逻辑（答题后调用）：

| 输入：card_id, quality（0-5，用户对本次作答的评分） 1. quality < 3（答错/不确定）：    重置 repetitions = 0，interval = 1，next_review = 明天 2. quality >= 3（答对）：    if repetitions == 0: interval = 1    elif repetitions == 1: interval = 6    else: interval = round(prev_interval × easiness_factor) 3. 更新 easiness_factor（记忆难度系数，初始2.5）：    EF = EF + (0.1 - (5-q)×(0.08 + (5-q)×0.02))    EF 最小值限制为 1.3 4. 睡眠因子修正：    if 学习时间 in [21:00, 23:59]:        next_review_time = 次日 07:00（优先晨间复习）        记忆稳定性 S × 1.2（睡眠巩固奖励） 输出：next_review_at（datetime），memory_strength（float 0~1） |
| --- |

## **3.2 状态评分算法（state_scorer.py）**

理论基础：Russell 情绪环形模型（效价×唤醒二维空间）+ D'Mello & Graesser 学习情绪体系（第9章、第11章）。

三路信号说明：

| **信号来源** | **采集方式** | **权重** | **关键指标** |
| --- | --- | --- | --- |
| 行为信号 | JS 事件监听 + 答题记录 | × 0.5（无摄像头时 0.625） | 答题时间 z-score、正确率、窗口失焦次数 |
| 自报告 | SAM 量表滑条 | × 0.3（无摄像头时 0.375） | 效价轴（好/差）+ 唤醒轴（清醒/困倦），各 0~10 分 |
| 摄像头（可选） | face-api.js | × 0.2 | 专注度（中性占比）、眨眼频率、头部朝向偏移 |

**设计原则：SAM 自报告为主要信号，行为数据为辅助修正。** SAM 滑条是用户对自身状态的直接表达，可独立触发状态判断；行为数据仅在有真实答题记录时才参与，避免默认值误触发。

状态判断采用三层优先级结构（高 → 低）：

**第一层：SAM 独立触发（任意页面均有效，无需答题数据）**

| **状态** | **SAM 条件** | **神经科学依据** |
| --- | --- | --- |
| 疲劳（Fatigue） | 唤醒 ≤ 2 | 唤醒极低即精力耗尽，无需其他条件 |
| 焦虑（Anxiety） | 效价 ≤ 3 且 唤醒 ≥ 7 | Russell 模型第二象限：高唤醒负效价 = 紧张/压力 |
| 无聊（Boredom） | 效价 ≤ 4 且 唤醒 ≤ 3 | Russell 模型第三象限：低唤醒负效价 = 游离/提不起劲 |

**第二层：行为信号辅助（有真实答题数据时生效）**

| **状态** | **行为条件** | **辅助条件** | **调度策略** |
| --- | --- | --- | --- |
| 焦虑（Anxiety） | 正确率 ≤ 40% 且 耗时 z > 1.0 | 效价 ≤ 5 | 难度 −1 级 |
| 困惑（Confusion） | 正确率 < 60% 且 耗时 z > 1.0 | 失焦次数 ≤ 3 | 推送补充解释 |
| 无聊（Boredom） | 正确率 ≥ 90% 且 耗时 z < −1.0 | — | 难度 +1 级 |

**第三层：长时学习疲劳**（学习时长 ≥ 45 分钟 且 唤醒 ≤ 4）→ 疲劳；单独时长不触发，避免专注学习被误判。

**兜底**：以上均不满足 → 心流（最优学习状态，保持当前节奏）。

> **实现说明**：前端 `useBehavior` hook 将答题正确率和耗时以模块级变量共享，每 30 秒随 SAM 值一并上报至 `POST /api/state/report`；P3 从数据库读取会话 `started_at` 实时计算学习时长后传入算法。状态更新后存入全局 store，下次答题时随请求体发给后端，驱动难度调度器。

## **3.3 自适应难度调度器（difficulty_scheduler.py）**

题目难度分为三级：Easy（1）/ Medium（2，默认）/ Hard（3）。调度器维护最近 3 题滑动窗口，每次答题后触发一次评估并决定是否切换难度。

**调度规则（优先级从高到低）**：

| **规则** | **触发条件** | **结果** |
| --- | --- | --- |
| 强制降级 | 连续答错 3 题 | 强制降至简单，重置连错计数 |
| 数据不足 | 窗口不足 3 题 | 维持当前难度，不调整 |
| 状态/正确率降级 | 状态为焦虑 **或** 近期正确率 < 40% | 难度 −1 |
| 状态/正确率升级 | 状态为无聊 **或** 近期正确率 > 85% | 难度 +1 |

> **状态与难度的联动**：前端在每次提交答案时，将当前学习状态（由状态评分算法每 30 秒更新，存于全局 store）一并发送给后端 `POST /api/questions/{id}/answer`。P3 将状态字符串映射为 `StateEnum` 后传入 `next_difficulty()`，实现状态感知的难度调度。调度结果（推荐难度 + 原因文本）返回给前端，原因文本直接显示为难度变化气泡提示。

## **3.4 LLM 内容生成（generate_cards.py / llm_advisor.py）**

卡片生成 Prompt 设计（JSON mode，批量输出）：

| SYSTEM: 你是一位神经科学教育专家。根据给定的课程文本，提取核心概念并生成记忆卡片。         严格以 JSON 数组格式输出，不要有任何其他文字。 USER:   以下是第8章《学习与记忆》的课程内容：{text}         请生成 {n} 张记忆卡片，每张包含：         - concept: 概念名称（简洁）         - front: 问题面（一句话提问）         - back: 答案面（50-80字，包含机制说明）         - difficulty: 1（基础）/ 2（理解）/ 3（应用）         - related_concepts: 相关概念列表（2-3个） 输出示例： [   {"concept": "长时程增强（LTP）",    "front": "LTP 的突触机制是什么？",    "back": "突触前神经元反复高频刺激后，突触后膜AMPA受体数量增加、             NMDA受体去Mg²⁺封闭，Ca²⁺内流激活蛋白激酶，导致突触传递             效能持久增强，是陈述性记忆形成的细胞机制。",    "difficulty": 2,    "related_concepts": ["NMDA受体", "突触可塑性", "海马体"]} ] |
| --- |

学习建议生成 Prompt（llm_advisor.py，实时调用）：

| SYSTEM: 你是学习伙伴，根据用户的学习状态数据给出简短、具体的建议（2-3句话）。         语气亲切，不要说废话，建议必须可执行。 USER:   当前状态：{state}（{state_desc}）         本次学习时长：{duration} 分钟         今日完成章节：{chapters}         即将遗忘的卡片：{forgetting_cards}（将在{hours}小时内跌破阈值）         近期各章节记忆强度：{memory_summary} 请给出：1条即时建议 + 1条今日计划建议（JSON格式输出） |
| --- |

# **四、数据库详细设计**

## **4.1 cards 表（知识卡片）**

| **字段名** | **类型** | **约束** | **说明** |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 主键 |
| chapter | INTEGER | NOT NULL | 章节号（1-11） |
| concept | TEXT | NOT NULL | 概念名称 |
| front | TEXT | NOT NULL | 卡片问题面 |
| back | TEXT | NOT NULL | 卡片答案面 |
| difficulty | INTEGER | DEFAULT 2 | 1基础/2理解/3应用 |
| memory_strength | REAL | DEFAULT 1.0 | 当前记忆强度（0~1） |
| stability | REAL | DEFAULT 1.0 | 记忆稳定性 S（遗忘曲线参数） |
| easiness_factor | REAL | DEFAULT 2.5 | SM-2 难度系数（≥1.3） |
| repetitions | INTEGER | DEFAULT 0 | 累计复习次数 |
| next_review_at | DATETIME | NOT NULL | 下次复习时间 |
| last_reviewed_at | DATETIME | NULL | 上次复习时间 |
| related_concepts | TEXT | NULL | 相关概念（JSON 数组） |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

## **4.2 questions 表（题库）**

| **字段名** | **类型** | **约束** | **说明** |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 主键 |
| chapter | INTEGER | NOT NULL | 章节号 |
| stem | TEXT | NOT NULL | 题干 |
| options | TEXT | NULL | 选项 JSON 数组（选择题） |
| answer | TEXT | NOT NULL | 正确答案 |
| explanation | TEXT | NULL | 解析文字 |
| type | TEXT | DEFAULT 'choice' | choice / truefalse / fill |
| difficulty | INTEGER | NOT NULL | 1/2/3 |
| related_card_id | INTEGER | FK→cards | 关联卡片（可为空） |

## **4.3 learning_sessions 表（学习会话）**

| **字段名** | **类型** | **约束** | **说明** |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 主键 |
| started_at | DATETIME | NOT NULL | 会话开始时间 |
| ended_at | DATETIME | NULL | 会话结束时间 |
| state_log | TEXT | NULL | 状态变化记录（JSON 数组，每分钟一条） |
| sam_valence | REAL | NULL | SAM 效价轴最终值（0~10） |
| sam_arousal | REAL | NULL | SAM 唤醒轴最终值（0~10） |
| final_state | TEXT | NULL | 会话末尾状态枚举 |
| cards_reviewed | INTEGER | DEFAULT 0 | 本次复习卡片数 |
| questions_answered | INTEGER | DEFAULT 0 | 本次答题数 |

## **4.4 question_responses 表（答题记录）**

| **字段名** | **类型** | **约束** | **说明** |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 主键 |
| session_id | INTEGER | FK→sessions | 所属会话 |
| question_id | INTEGER | FK→questions | 所答题目 |
| is_correct | BOOLEAN | NOT NULL | 是否答对 |
| time_spent_ms | INTEGER | NOT NULL | 答题耗时（毫秒） |
| difficulty_at_time | INTEGER | NOT NULL | 答题时的当前难度级别 |
| answered_at | DATETIME | DEFAULT NOW | 答题时间戳 |

# **五、后端 API 接口清单**

所有接口以 /api 为前缀，由 P3 实现，P4 调用。请求/响应均为 JSON 格式。

| **方法** | **路径** | **实现方** | **功能说明** |
| --- | --- | --- | --- |
| **GET** | /api/cards/next | P3 | 获取下一张待学或待复习卡片。按 next_review_at 最紧迫顺序排序，可传 chapter 参数过滤章节 |
| **POST** | /api/cards/{id}/review | P3 | 提交卡片复习结果。请求体传入 quality（0-5分）和 session_id，P3 调用 P1 的 review_card() 计算新参数后写库 |
| **GET** | /api/cards/curve | P3 | 返回各章节所有卡片的记忆强度随时间衰减数据，供前端绘制遗忘曲线折线图 |
| **GET** | /api/questions/next | P3 | 获取下一道题目。传入 chapter（章节）和 difficulty（1/2/3），P3 调用 P1 难度调度器后从 P2 数据库取题 |
| **POST** | /api/questions/{id}/answer | P3 | 提交答题结果。传入 answer、答题耗时 time_ms 和 session_id，返回是否正确、题目解析、下一题推荐难度 |
| **POST** | /api/state/report | P3 | 上报三路学习状态信号。传入行为指标（正确率/平均耗时/失焦次数）+ SAM量表得分，P3 调用 P1 评分算法，返回状态枚举和即时建议文本 |
| **GET** | /api/state/history | P3 | 返回最近7天的状态变化时序记录，供 Insights 页面绘制历史状态趋势图 |
| **POST** | /api/sessions/start | P3 | 创建新学习会话，在 P2 数据库写入一条 session 记录，返回 session_id（前端全局持有） |
| **POST** | /api/sessions/{id}/end | P3 | 结束会话，传入最终 SAM 得分，P3 更新会话记录的结束时间和状态快照 |
| **GET** | /api/insights/suggestion | P3 | 触发 AI 学习建议生成。P3 从 P2 汇总当前状态和记忆数据，调用 DeepSeek API 生成个性化建议，返回即时建议和今日计划两段文本 |
| **GET** | /api/dashboard/summary | P3 | 返回仪表盘所需汇总数据：今日到期卡片数、连续学习天数、各章节平均记忆强度、最近状态记录 |

# **六、接口契约详细定义**

接口契约是五人并行开发的核心协议。P1 实现算法函数、P2 实现数据库函数、P3 实现 HTTP 接口、P4 调用 HTTP 接口，各方只需遵守本章定义，无需了解其他人的内部实现。

## **6.1 P3 调用 P1 算法函数（Python 直接 import）**

P1 以纯函数形式提供，输入确定则输出确定，无任何副作用。P3 在 services/ 中 import 后直接调用。

| **函数签名** | **输入说明** | **返回值说明** | **所在文件** |
| --- | --- | --- | --- |
| review_card(card: CardData, quality: int) | card：卡片当前参数（稳定性、重复次数等）；quality：用户本次作答质量 0~5 | 下次复习时间 next_review_at、新记忆强度 memory_strength、新稳定性 stability | memory_engine.py |
| get_memory_strength(card: CardData) | card：卡片参数，需含 last_reviewed_at 和 stability 字段 | float 0.0~1.0，表示当前记忆保留率（越低越需要复习） | memory_engine.py |
| get_forgetting_curve(card: CardData, days: int) | card：卡片参数；days：预测未来天数（建议7~14） | 列表 [{day: int, strength: float}]，供前端折线图使用 | memory_engine.py |
| score_state(behavior: BehaviorSignal, sam: SAMScore, camera: CameraScore │ None) | behavior：行为指标（正确率、平均耗时z-score、失焦次数）；sam：效价+唤醒各0~10；camera 可选 | StateEnum（flow/anxiety/boredom/confusion/fatigue）+ 得分 float + 实际使用的权重 dict | state_scorer.py |
| next_difficulty(sched: dict, state: StateEnum, recent: list[bool]) | sched：调度器当前状态（当前难度级、连对数等）；state：当前状态枚举；recent：最近3题对错列表 | 推荐难度 int(1/2/3) + 调整原因 reason str（用于前端提示气泡） | difficulty_scheduler.py |

## **6.2 P3 调用 P2 数据库函数（Python 直接 import）**

P2 的 db_service.py 是数据库的唯一对外接口。P3 只通过这里读写数据，不直接操作 ORM 模型或 SQL 语句。

| **函数签名** | **功能说明** | **所在文件** |
| --- | --- | --- |
| get_next_card(chapter=None) → CardData | 按 next_review_at 最早顺序取一张卡片，chapter 为 None 时不过滤章节 | db_service.py |
| update_card_memory(card_id: int, updates: dict) | 将 P1 算法计算结果（新稳定性、下次复习时间等）写入 cards 表 | db_service.py |
| get_all_curves() → list[CurveData] | 返回所有卡片的稳定性参数，P3 调用 P1 的 get_forgetting_curve() 后组装返回前端 | db_service.py |
| get_next_question(chapter: int, difficulty: int) → QuestionData | 按章节和难度随机取一道题（排除最近5次已答的题目，避免重复） | db_service.py |
| save_response(session_id, q_id, is_correct, time_ms, difficulty) | 在 question_responses 表写入一条答题记录 | db_service.py |
| get_dashboard_summary() → DashboardData | 聚合查询：今日到期卡片数、连续天数、各章节 memory_strength 均值 | db_service.py |
| get_state_history(n_days=7) → list[StateRecord] | 返回最近 n 天每次会话末尾的状态记录 | db_service.py |
| create_session() → int | 在 learning_sessions 表插入新行，返回自增主键 session_id | db_service.py |
| end_session(session_id, final_state, sam_valence, sam_arousal) | 更新会话的 ended_at、final_state 和 SAM 得分 | db_service.py |

## **6.3 P2 调用 DeepSeek API（内容生成，离线脚本）**

P2 的 llm_client.py 封装了 DeepSeek API 调用。generate_cards.py 和 generate_questions.py 调用此客户端，一次性生成全量知识库内容。

| # pdf_parser.py — 提取课件文本 def extract_by_chapter(data_dir: str) -> dict:     # 扫描 data/ 目录下所有 PDF，文件名格式：08_学习与记忆.pdf     # 用 pdfplumber 逐页提取文字，拼接为整章文本     # 返回 {chapter_num: text_str} # llm_client.py — DeepSeek API 封装 def generate_json(system_prompt: str, user_content: str) -> dict:     # 调用 DeepSeek API，强制 JSON mode 输出     # 内置重试逻辑（最多3次，指数退避）     # JSON 解析失败时记录日志并返回空结果 # generate_cards.py — 卡片批量生成示例 chapters = pdf_parser.extract_by_chapter('data/') for ch_num, text in chapters.items():     cards = llm_client.generate_json(         system_prompt=open('prompts/card_generation.txt').read(),         user_content=f'以下是第{ch_num}章课件内容：\n{text}\n请生成20张卡片'     )     db_service.bulk_insert_cards(ch_num, cards) |
| --- |

## **6.4 P4 调用 P3 HTTP 接口（前端 fetch 封装）**

P4 的 lib/api.ts 统一封装所有 HTTP 调用，页面和组件只 import 这里的函数，不直接写 fetch。

| // lib/api.ts — 接口调用示例（TypeScript） const BASE = process.env.NEXT_PUBLIC_API_URL  // http://localhost:8000 // 获取下一张卡片 export async function getNextCard(chapter?: number) {     const url = chapter ? `${BASE}/api/cards/next?chapter=${chapter}`                         : `${BASE}/api/cards/next`     const res = await fetch(url)     return res.json()  // → { id, concept, front, back, memory_strength, chapter } } // 提交卡片复习结果 export async function reviewCard(id: number, quality: number, sessionId: string) {     const res = await fetch(`${BASE}/api/cards/${id}/review`, {         method: 'POST',         headers: { 'Content-Type': 'application/json' },         body: JSON.stringify({ quality, session_id: sessionId })     })     return res.json()  // → { next_review_at, new_memory_strength, interval_days } } // 上报学习状态（行为信号 + SAM 量表） export async function reportState(payload: StateReportPayload) {     const res = await fetch(`${BASE}/api/state/report`, {         method: 'POST',         headers: { 'Content-Type': 'application/json' },         body: JSON.stringify(payload)     })     return res.json()  // → { state: 'flow'│'anxiety'│..., suggestion_text } } |
| --- |

# **七、详细分工方案**

## **7.1 分工总览**

每人独立负责一个顶层文件夹，通过第六章的接口契约协作，可在 Week 1 完成接口约定后立即并行开发。

| **成员** | **角色** | **专属文件夹** | **核心职责** | **工作量** |
| --- | --- | --- | --- | --- |
| **P1** | 算法工程师 | p1_algorithms/ | SM-2 间隔重复、三路状态评分、自适应难度调度，全部以纯函数实现，附单元测试 | 约 20% |
| **P2** | 知识库工程师 | p2_knowledge/ | SQLite 数据库建模、PDF 课件解析、DeepSeek API 调用、卡片与题目批量生成入库、db_service.py CRUD 接口 | 约 25% |
| **P3** | 服务端工程师 | p3_server/ | FastAPI 框架搭建、全部 HTTP 路由实现、调用 P1 算法和 P2 数据库组装业务逻辑、DeepSeek 学习建议接口 | 约 25% |
| **P4** | 前端工程师 | p4_frontend/ | Next.js 全部页面与组件（仪表盘/卡片学习/测验/洞察）、行为采集 Hook、SAM 量表、遗忘曲线可视化 | 约 20% |
| **P5** | 文档负责人 | docs/ | 项目报告撰写（背景/文献/算法描述/创新点）、演示 PPT、操作录屏，Week 1 即可开始写研究背景部分 | 约 10% （含前期调研） |

## **7.2 各成员详细任务清单**

### **P1 — 算法工程师**

| **优先级** | **任务** | **涉及文件** | **预计工时** |
| --- | --- | --- | --- |
| **P0** | 定义 schemas.py 数据类（CardData、BehaviorSignal、SAMScore、StateEnum），这是 P3 import 的类型基础 | p1_algorithms/schemas.py | 2h |
| **P0** | 实现 memory_engine.py：review_card()、get_memory_strength()、get_forgetting_curve()，含睡眠因子修正 | p1_algorithms/memory_engine.py | 5h |
| **P0** | 实现 state_scorer.py：三路加权融合、五类状态判断规则，摄像头缺失时自动重新归一化权重 | p1_algorithms/state_scorer.py | 4h |
| **P1** | 实现 difficulty_scheduler.py：维护最近3题窗口，结合状态枚举输出推荐难度和原因文本 | p1_algorithms/difficulty_scheduler.py | 3h |
| **P1** | 编写单元测试：覆盖 SM-2 各 quality 值边界、状态判断规则、难度升降逻辑 | p1_algorithms/tests/ | 3h |
| **P2** | 配合 P3 联调：提供本地调用示例，确认函数签名与 P3 调用方式一致 | （联调） | 1h |

### **P2 — 知识库工程师**

| **优先级** | **任务** | **涉及文件** | **预计工时** |
| --- | --- | --- | --- |
| **P0** | 建表：编写 models/ 四张 ORM 模型（cards、questions、sessions、responses），运行 seed_db.py 初始化 SQLite | p2_knowledge/models/ + scripts/seed_db.py | 3h |
| **P0** | 实现 pdf_parser.py：用 pdfplumber 批量提取 data/ 下各章 PDF 文本，按章节编号返回字典 | p2_knowledge/pdf_parser.py | 2h |
| **P0** | 实现 llm_client.py：封装 DeepSeek API 调用，JSON mode，含重试和解析失败回退 | p2_knowledge/llm_client.py | 3h |
| **P0** | 编写 prompts/ 提示词：卡片生成模板（要求输出概念/正面/背面/难度/相关概念）、题目生成模板（每卡生成简单/中等/困难各1道） | p2_knowledge/prompts/ | 3h |
| **P0** | 运行 generate_cards.py 生成全部11章卡片并入库，人工抽检质量，迭代 Prompt 直至准确率满意 | p2_knowledge/scripts/generate_cards.py | 4h |
| **P1** | 运行 generate_questions.py 生成题库并入库，覆盖三个难度级 | p2_knowledge/scripts/generate_questions.py | 3h |
| **P1** | 实现 db_service.py 全部 CRUD 函数，这是 P3 访问数据库的唯一入口 | p2_knowledge/db_service.py | 4h |
| **P2** | 实现 refresh_chapter.py 支持单章节内容热替换（不覆盖已有的 memory_strength 参数） | p2_knowledge/scripts/refresh_chapter.py | 2h |

### **P3 — 服务端工程师**

| **优先级** | **任务** | **涉及文件** | **预计工时** |
| --- | --- | --- | --- |
| **P0** | 搭建 FastAPI 项目框架：main.py 入口、CORS 配置、统一异常处理，确保 P4 可以跨域调用 | p3_server/main.py + core/ | 2h |
| **P0** | 定义全部 Pydantic 请求/响应模型（schemas/），这是 P4 开发时 mock 数据的依据 | p3_server/schemas/ | 3h |
| **P0** | 实现 card_service.py + cards.py 路由：/api/cards/next、/api/cards/{id}/review、/api/cards/curve | p3_server/services/card_service.py + routers/cards.py | 4h |
| **P0** | 实现 sessions.py 路由：/api/sessions/start、/api/sessions/{id}/end（P4 最先调用，需优先完成） | p3_server/routers/sessions.py | 2h |
| **P1** | 实现 quiz_service.py + questions.py 路由：/api/questions/next、/api/questions/{id}/answer（含难度调度） | p3_server/services/quiz_service.py + routers/questions.py | 4h |
| **P1** | 实现 state_service.py + state.py 路由：/api/state/report、/api/state/history | p3_server/services/state_service.py + routers/state.py | 3h |
| **P1** | 实现 dashboard.py 路由：/api/dashboard/summary 聚合数据查询 | p3_server/routers/dashboard.py | 2h |
| **P2** | 实现 insight_service.py + insights.py 路由：组装上下文，调用 DeepSeek API 生成学习建议 | p3_server/services/insight_service.py + routers/insights.py | 3h |

### **P4 — 前端工程师**

| **优先级** | **任务** | **涉及文件** | **预计工时** |
| --- | --- | --- | --- |
| **P0** | 搭建 Next.js 14 项目：配置 Tailwind CSS、shadcn/ui、Recharts，建好 app/ 路由结构和根布局（Sidebar + TopBar） | p4_frontend/ 根配置 + app/layout.tsx + components/layout/ | 3h |
| **P0** | 实现 lib/api.ts：封装全部后端接口调用函数（P3 schema 定好后即可按 mock 数据先行开发） | p4_frontend/lib/api.ts | 3h |
| **P0** | 实现 FlipCard 组件（3D 翻转动画、评分按钮 0-5）和 /learn 页面（调 getNextCard、reviewCard） | components/cards/FlipCard.tsx + app/learn/page.tsx | 5h |
| **P0** | 实现 SAMSlider 组件和 BehaviorTracker 组件（键鼠事件采集，30s 汇总调 reportState） | components/state/SAMSlider.tsx + BehaviorTracker.tsx | 4h |
| **P1** | 实现 QuestionCard 组件和 /quiz 页面（答题反馈、难度变化提示气泡） | components/quiz/QuestionCard.tsx + app/quiz/page.tsx | 4h |
| **P1** | 实现 ForgettingCurve、MemoryHeatmap 组件和 /dashboard 页面 | components/charts/ + app/dashboard/page.tsx | 4h |
| **P1** | 实现 /review 复习队列页和 /insights 洞察页（RadarChart + LLM 建议打字机展示） | app/review/ + app/insights/ + charts/RadarChart.tsx | 4h |
| **P2** | 实现 useSession Hook、sessionStore 全局状态，完成与 P3 的端到端联调测试 | hooks/useSession.ts + store/sessionStore.ts | 3h |

### **P5 — 文档负责人**

| **优先级** | **任务** | **涉及文件** | **时间节点** |
| --- | --- | --- | --- |
| **P0** | Day 1 即开始：文献检索，整理7篇核心参考文献（Ebbinghaus遗忘曲线、SM-2算法、Russell情绪模型、D'Mello学习情绪体系、睡眠巩固、心流理论、间隔重复实验效果） | docs/参考文献.txt | Day 1 |
| **P0** | 撰写报告【研究主题】部分：项目背景（现实需求 + 理论依据）、国内外相关文献分析、用户需求分析、创新性/可行性/实用性分析、参考文献列表 | docs/报告_研究主题.docx | Day 1-2 |
| **P0** | 撰写报告【研究方法】部分：研究内容概述、三大核心算法的设计原理（结合课程第8/9/11章理论阐述合理性）、关键技术说明（SM-2、状态评分、DeepSeek 内容生成） | docs/报告_研究方法.docx | Day 3-4 |
| **P1** | 撰写报告【项目创新点】部分：与现有产品（Anki等）的差异化对比、三个创新点的详细说明 | docs/报告_创新点.docx | Day 4-5 |
| **P1** | Day 5-6：向各成员收集功能截图，整合【成果展示】部分，汇总为完整报告定稿 | docs/项目报告_完整版.docx | Day 5-6 |
| **P1** | 填写报告封面表格（项目名称、类型、关联章节等），确认报告格式符合模板要求 | docs/项目报告_完整版.docx | Day 6 |

# **八、开发里程碑**

总开发周期 6 天。Day 1 重点是把接口契约全部对齐，Day 2 起四人并行开发，Day 5-6 联调收尾。

| **天** | **阶段** | **各成员目标** | **关键检查点** |
| --- | --- | --- | --- |
| **Day 1** | 接口对齐 | P1：发布 schemas.py（CardData、BehaviorSignal、SAMScore、StateEnum 数据类定义） P2：运行 seed_db.py 建好四张空表，确认字段；编写 prompts/ 提示词初稿 P3：发布全部 Pydantic schemas（请求/响应模型），搭好 FastAPI 框架，CORS 配置完成 P4：搭好 Next.js 项目，建好五个页面路由骨架，lib/api.ts 按 P3 schemas 写好 mock 函数 P5：开始撰写报告研究背景（文献检索） | 四人接口文件互相确认，无歧义后开始并行 |
| **Day 2** | 核心开发 | P1：完成 memory_engine.py（SM-2 + 睡眠修正）和 state_scorer.py，附单元测试 P2：完成 pdf_parser.py + llm_client.py，跑通至少两章卡片生成入库 P3：完成 sessions 路由（start/end）、cards 路由（next/review/curve） P4：完成 FlipCard 组件（3D翻转+评分按钮）、/learn 页面对接 mock 数据 | P3 sessions 接口上线，P4 可拿到真实 session_id |
| **Day 3** | 核心开发 | P1：完成 difficulty_scheduler.py，全部算法单测通过 P2：完成全部11章卡片和题库入库，完成 db_service.py 全部 CRUD 函数 P3：完成 questions 路由（next/answer）、state 路由（report/history） P4：完成 SAMSlider + BehaviorTracker 组件、/quiz 页面对接 mock 数据 | P2 数据库就绪，P3 开始接入真实数据 |
| **Day 4** | 功能整合 | P3：完成 dashboard 路由、insights 路由（DeepSeek 建议接口）；P3 全部接口对接 P1 算法和 P2 数据库 P4：/dashboard 页（遗忘曲线图 + 热力图）、/review 页、/insights 页完成；开始替换 mock 为真实 API P5：完成报告研究方法章节（三大算法描述） | P3 全部接口可用，P4 开始全面替换 mock 数据 |
| **Day 5** | 联调测试 | P4：完成全部页面真实数据接入，修复交互 Bug，完善样式 P3：配合 P4 联调，修复接口问题 P1/P2：提供调试支持，修复算法边界问题 P5：完成报告创新点章节，汇总各成员截图 | 完整流程（登录→学习→测验→洞察）可端到端跑通 |
| **Day 6** | 收尾 | 全员：最终 Bug 修复，准备演示数据（确保各章有足量卡片和题目） P5：整合完整报告，确认格式和参考文献 | 报告定稿，系统可演示 |

# **九、前端 UI 设计描述（Claude Design 参考稿）**

**以下描述用于输入 Claude Design 或其他 AI 设计工具生成 UI 原型。**

## **8.1 总体设计语言**

| 整体风格：深色科技感 + 神经元/突触视觉元素 主色：深靛蓝 #0A1628（背景）+ 青绿 #00D4AA（强调色） 字体：标题用 Space Grotesk，正文用 Inter 布局：左侧固定导航栏（64px宽，图标导航）+ 右侧主内容区 装饰：页面背景有极淡的神经网络连接线纹理（SVG，低不透明度） |
| --- |

## **8.2 /dashboard 记忆仪表盘**

| 顶部：三个横向指标卡（今日待复习 N 张 / 连续学习 X 天 / 整体记忆强度 XX%）        卡片风格：深色玻璃质感，数字大字，下方有趋势小箭头 中部左（60%宽）：遗忘曲线折线图   - X轴：未来7天日期，Y轴：记忆保留率 0-100%   - 多条曲线，每条代表一个章节，颜色区分   - 曲线下方填充渐变，Y=70%处有一条红色虚线（复习阈值线）   - 右上角有章节筛选下拉菜单 中部右（40%宽）：各章节记忆强度热力图   - 11个章节排列成网格，每格颜色从红（弱）→黄→绿（强）   - 悬停显示该章节的详细数据（卡片数、平均强度、下次复习时间） 底部：今日任务列表   - 卡片列表，每项显示：章节图标 / 任务描述 / 预计时间 / 开始按钮（青绿色） |
| --- |

## **8.3 /learn 卡片学习页**

| 中央大卡片（可翻转，3D CSS动画）：   正面：章节标签（小胶囊） + 概念名（大字，32px）+ 难度星级   背面：答案正文（18px，行距1.8） + 相关概念标签组（底部，胶囊样式）   翻转方式：点击卡片或按空格键 卡片下方：六个评分按钮（0-5）   0=完全不会（红）1=很难（橙）2=困难（黄）3=一般（灰）4=容易（浅绿）5=非常熟悉（绿）   选中后按钮放大+发光，自动加载下一张 右侧边栏：   - 当前队列进度（N/M，环形进度条）   - 记忆强度变化预览（选不同评分时实时预览下次复习时间） 底部固定栏（SAM量表）：   半透明玻璃背景，两个水平滑条：   效价：左端😞 右端😊，当前值显示在滑块上   唤醒：左端😴 右端⚡   右侧：当前状态标签（心流/焦虑/无聊/疲劳，对应不同颜色） |
| --- |

## **8.4 /quiz 章节测验页**

| 顶部：章节选择标签页（11章，横向滚动）+ 当前难度指示器（Easy/Medium/Hard胶囊） 主区域：题目卡片   - 题号 + 题干（大字） + 题目图（如有）   - 选项：A/B/C/D 四个大按钮，左侧字母圆圈 + 右侧文字   - 选中后：正确选项变绿（✓图标）+ 错误选项变红（✗图标）   - 答对：右上角出现+10分动画飘字（青绿色）   - 答错：底部弹出解析面板（卡片样式，显示正确答案和原理说明） 左侧：答题统计侧边栏   - 本题用时（秒表）/ 正确率 / 当前连对数   - 难度变化提示：检测到状态变化时，出现小提示气泡（如「感觉有些困难，降低难度~」） 底部：下一题按钮（选完答案后激活） + 结束本轮按钮 |
| --- |

## **8.5 /insights 学习洞察页**

| 顶部：AI 建议卡片   - 左侧有小机器人头像图标（青绿色线条风格）   - 建议文字以打字机效果逐字出现   - 底部有「刷新建议」按钮 中部左（50%）：章节掌握度雷达图   - 11个维度，多边形填充（青绿色，30%透明度）   - 背景有灰色网格线   - 每个顶点标注章节名缩写 中部右（50%）：历史状态折线图   - X轴：最近7天日期，Y轴：状态类型（心流/无聊/焦虑/疲劳）   - 每个数据点是彩色圆点，悬停显示当天详细数据 底部：学习统计汇总卡片组   总学习时长 / 累计复习卡片数 / 最长连续学习天数 / 掌握最好的章节 |
| --- |

# **十、关键参考文献**

1. Ebbinghaus, H. (1885). Über das Gedächtnis. 遗忘曲线原始文献，间隔重复理论基础。

2. Wozniak, P.A. & Gorzelanczyk, E.J. (1994). SM-2 Algorithm. SuperMemo算法原文，本项目间隔重复引擎的实现依据。

3. Russell, J.A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology. SAM量表与情绪二维模型的理论来源。

4. D'Mello, S. & Graesser, A. (2012). Dynamics of affective states during complex learning. Learning and Instruction. 学习情绪体系（心流/焦虑/无聊/困惑）分类依据。

5. Stickgold, R. (2005). Sleep-dependent memory consolidation. Nature. 睡眠记忆巩固理论，睡眠因子修正的依据。

6. Csikszentmihalyi, M. (1990). Flow: The Psychology of Optimal Experience. 心流理论，难度自适应设计的依据。

7. Kornell, N. & Bjork, R.A. (2008). Optimising self-regulated study: The benefits and costs of dropping flashcards. Memory. 间隔重复在实际学习中的应用研究。