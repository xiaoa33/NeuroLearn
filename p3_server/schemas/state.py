# 学习状态相关 Pydantic 请求/响应模型
# StateReportRequest  → POST /api/state/report 请求体
#                       包含行为指标(accuracy、avg_time_zscore、defocus_count)和 SAM 量表得分
# StateReportResponse → POST /api/state/report 返回体（state 枚举、suggestion_text）
