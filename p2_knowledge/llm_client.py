# DeepSeek API 封装客户端
# 需实现：
#   generate_json(system_prompt, user_content) → dict，强制 JSON mode 输出
# 内置重试逻辑（最多3次，指数退避），JSON 解析失败时记录日志并返回空结果
# API Key 从环境变量 DEEPSEEK_API_KEY 读取，不硬编码
