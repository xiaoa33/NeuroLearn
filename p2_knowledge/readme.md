步骤 1：初始化数据库
python -m p2_knowledge.scripts.seed_db
步骤 2：生成所有章节的知识卡片
python -m p2_knowledge.scripts.generate_cards
步骤 3：为所有卡片生成配套题目
python -m p2_knowledge.scripts.generate_questions
步骤 4（可选）：章节热替换（更新内容 + 保留学习进度）
以章节 1为例：
python -m p2_knowledge.scripts.refresh_chapter --chapter 1

备注：
08 运动控制pdf有问题，平台上也打不开
我用DB Browser for SQLite粗略检查后没发现问题，如果使用数据库时碰到问题我再改吧