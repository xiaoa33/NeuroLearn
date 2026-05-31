# 数据库 CRUD 接口层 —— P3 访问数据库的唯一入口
# P3 只调用此文件中的函数，不直接操作 ORM 模型或 SQL 语句
#
# 需实现以下函数（详见接口契约 6.2 节）：
#   get_next_card(chapter=None)                              → CardData
#   update_card_memory(card_id, updates)
#   get_all_curves()                                         → list[CurveData]
#   get_next_question(chapter, difficulty)                   → QuestionData
#   save_response(session_id, q_id, is_correct, time_ms, difficulty)
#   get_dashboard_summary()                                  → DashboardData
#   get_state_history(n_days=7)                              → list[StateRecord]
#   create_session()                                         → int (session_id)
#   end_session(session_id, final_state, sam_valence, sam_arousal)
#   bulk_insert_cards(chapter, cards)                        → 供生成脚本批量写入
