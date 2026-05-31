# 题库批量生成脚本（一次性运行）
# 遍历 cards 表中所有卡片，调用 DeepSeek 为每张卡片生成3道测验题（简单/中等/困难各1道）
# 结果写入 questions 表，related_card_id 关联对应卡片
# 需在 generate_cards.py 成功运行且卡片已入库后执行
