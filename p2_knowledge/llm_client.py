"""
LLM 客户端封装模块
严格遵循系统设计：
1. 调用 DeepSeek API，强制 JSON 模式输出
2. 内置 3 次重试 + 指数退避机制
3. 从环境变量读取 API Key，禁止硬编码
4. JSON 解析失败自动返回空字典
5. 作为 generate_cards/questions 的唯一 LLM 调用入口
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from tqdm import tqdm

# 环境变量初始化
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

if not DEEPSEEK_API_KEY:
    raise ValueError("环境变量 DEEPSEEK_API_KEY 未配置，请在 .env 文件中添加")

# 初始化 LLM 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# 核心 LLM 调用函数
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(APIError),
    reraise=True
)
def generate_json(system_prompt: str, user_content: str) -> dict:
    """
    调用 DeepSeek API，强制返回 JSON 格式数据
    优化：成功调用不输出任何信息，仅错误时打印
    """
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        raw_content = response.choices[0].message.content.strip()
        json_result = json.loads(raw_content)
        return json_result

    except json.JSONDecodeError:
        tqdm.write(f"LLM 返回格式非 JSON，原始内容：{raw_content[:100]}...")
        return {}

    except APIError as e:
        tqdm.write(f"DeepSeek API 调用失败：{str(e)}")
        return {}

    except Exception as e:
        tqdm.write(f"LLM 客户端未知错误：{str(e)}")
        return {}