"""
题库批量生成脚本
流程：
1. 从数据库读取所有已生成的知识卡片
2. 为每张卡片生成 3 道题目（简单/中等/困难各1道）
3. 读取题目生成 Prompt 模板
4. 调用 LLM 生成标准 JSON 题目
5. 批量写入数据库

执行方式：python -m p2_knowledge.scripts.generate_questions
"""

import os
from pathlib import Path
from sqlalchemy.orm import Session
from tqdm import tqdm

# 导入项目内部模块
from p2_knowledge.database import get_db
from p2_knowledge.llm_client import generate_json
from p2_knowledge.models.card import Card
from p2_knowledge.models.question import Question

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "question_generation.txt"
QUESTIONS_PER_CARD = 3


def load_question_prompt() -> str:
    """加载题目生成系统提示词"""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"题目生成 Prompt 文件不存在：{PROMPT_PATH}")
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_questions_for_card(
        db: Session,
        card: Card,
        prompt: str
) -> int:
    """
    为单张卡片生成 3 道难度题目并写入数据库
    """
    card_content = f"""
    概念：{card.concept}
    卡片正面：{card.front}
    卡片背面：{card.back}
    章节：{card.chapter}
    难度：{card.difficulty}
    """

    result = generate_json(prompt, card_content)
    if not result or "questions" not in result:
        tqdm.write(f"卡片 {card.id} 生成题目失败")
        return 0

    question_list = result["questions"]
    success_count = 0

    for q in question_list:
        try:
            question = Question(
                related_card_id=card.id,
                chapter=card.chapter,
                stem=q["stem"],
                options=q["options"],
                answer=q["answer"],
                explanation=q.get("explanation", ""),
                type=q.get("type", "choice"),
                difficulty=q["difficulty"]
            )
            db.add(question)
            success_count += 1
        except Exception as e:
            tqdm.write(f"题目写入失败：{str(e)}")
            continue

    db.commit()
    return success_count


def run_generate_all_questions():
    """批量为所有卡片生成题目"""
    prompt = load_question_prompt()
    print("题目生成 Prompt 加载完成")

    db: Session = next(get_db())
    cards = db.query(Card).all()

    if not cards:
        print("数据库中无卡片，请先运行 generate_cards.py 生成卡片")
        db.close()
        return

    print(f"开始为 {len(cards)} 张卡片生成题目...")
    total_generated = 0

    with tqdm(total=len(cards), desc="生成题目进度", leave=True, unit="张") as pbar:
        for card in cards:
            count = generate_questions_for_card(db, card, prompt)
            total_generated += count
            pbar.update(1)

    print(f"\n题库生成完成！")
    print(f"总计生成题目：{total_generated} 道")
    print(f"卡片数量：{len(cards)} 张")

    db.close()


if __name__ == "__main__":
    run_generate_all_questions()