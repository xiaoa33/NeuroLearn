"""
卡片批量生成脚本
流程：
1. 从 ./data 目录读取所有章节 PDF
2. 调用 PDF 解析器提取文本
3. 读取 Prompt 模板
4. 调用 LLM 生成知识卡片（JSON 格式）
5. 批量写入数据库
执行方式：python -m p2_knowledge.scripts.generate_cards
"""
import os
from pathlib import Path
from sqlalchemy.orm import Session
from tqdm import tqdm

# 导入项目内部模块
from p2_knowledge.database import get_db
from p2_knowledge.pdf_parser import extract_by_chapter
from p2_knowledge.llm_client import generate_json
from p2_knowledge import db_service

# Prompt 模板路径
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "card_generation.txt"
# 数据目录（存放章节 PDF）
DATA_DIR = "./data"
# 每章生成卡片数量（可根据需求调整）
CARDS_PER_CHAPTER = 20


def load_card_prompt() -> str:
    """
    加载卡片生成系统提示词模板
    """
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"卡片生成 Prompt 文件不存在：{PROMPT_PATH}")

    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_cards_for_chapter(db: Session, chapter: int, text: str, prompt: str):
    """
    为单个章节生成并保存卡片
    """
    tqdm.write(f"\n======================================")
    tqdm.write(f"开始处理章节 {chapter}")
    tqdm.write(f"======================================")

    if not text or len(text.strip()) == 0:
        tqdm.write(f"章节 {chapter} 文本为空，跳过")
        return

    # 调用 LLM 生成卡片
    result = generate_json(prompt, text)
    if not result or "cards" not in result:
        tqdm.write(f"章节 {chapter} 卡片生成失败")
        return

    card_list = result["cards"]
    tqdm.write(f"LLM 返回 {len(card_list)} 张卡片")

    # 批量写入数据库
    success_count = db_service.bulk_insert_cards(db, chapter, card_list)
    tqdm.write(f"章节 {chapter} 成功写入数据库：{success_count} 张卡片")


def run_generate_all_cards():
    """
    主函数：批量生成所有章节卡片
    """
    # 加载提示词
    prompt = load_card_prompt()
    print("卡片生成 Prompt 加载完成")

    # 批量提取所有章节 PDF 文本
    chapter_text_map = extract_by_chapter(DATA_DIR)
    if not chapter_text_map:
        print("未提取到任何章节文本，请检查 ./data 目录下的 PDF 文件")
        return

    print(f"\n开始为 {len(chapter_text_map)} 个章节生成知识卡片...")

    # 获取数据库会话
    db: Session = next(get_db())

    # 遍历所有章节生成卡片
    with tqdm(total=len(chapter_text_map), desc="生成卡片进度", leave=True, unit="章") as pbar:
        for chapter, text in chapter_text_map.items():
            generate_cards_for_chapter(db, chapter, text, prompt)
            pbar.update(1)

    print("\n所有章节卡片生成完成！")
    db.close()


if __name__ == "__main__":
    run_generate_all_cards()