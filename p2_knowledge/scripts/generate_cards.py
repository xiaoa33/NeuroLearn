# 知识卡片批量生成脚本（一次性运行）
# 流程：pdf_parser 提取各章 PDF 文本 → llm_client 调用 DeepSeek 生成卡片 JSON → db_service 写入 cards 表
# 每章调用一次 LLM，每次生成约 20 张卡片，输出 JSON 格式（见 prompts/card_generation.txt）
# 运行前确保 data/ 目录下已放置所有章节 PDF，且数据库已初始化（seed_db.py 已运行）
