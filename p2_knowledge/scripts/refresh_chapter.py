"""
章节内容热替换脚本（保留记忆进度，只替换内容）
功能：
1. 重新解析指定章节的 PDF
2. 删除该章节旧卡片（但保留记忆参数）
3. 重新生成新卡片 + 新题目
4. 自动恢复原有记忆进度（稳定性、复习时间等）
执行方式：
python -m p2_knowledge.scripts.refresh_chapter --chapter 1
"""
import argparse
from pathlib import Path
from sqlalchemy.orm import Session
from tqdm import tqdm

# 导入项目模块
from p2_knowledge.database import get_db
from p2_knowledge.pdf_parser import extract_text
from p2_knowledge.llm_client import generate_json
from p2_knowledge.models.card import Card
from p2_knowledge.models.question import Question
from p2_knowledge import db_service

PROMPT_CARD = Path(__file__).parent.parent / "prompts" / "card_generation.txt"
PROMPT_QUESTION = Path(__file__).parent.parent / "prompts" / "question_generation.txt"
DATA_DIR = "./data"


def load_prompt(path: Path) -> str:
    """加载提示词模板"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def find_chapter_pdf(chapter: int) -> Path | None:
    """
    精确查找指定章节对应的PDF文件
    匹配规则：两位数字前缀 + 空格 + 任意名称.pdf
    例：章节1 → 匹配 "01 *.pdf"
    """
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        tqdm.write(f"数据目录不存在：{DATA_DIR}")
        return None

    # 精确匹配指定章节的PDF（自动补零为两位数字）
    pattern = f"{chapter:02d} *.pdf"
    pdf_files = list(data_path.glob(pattern))

    if not pdf_files:
        tqdm.write(f"未找到章节 {chapter} 的PDF文件")
        tqdm.write(f"请确保文件命名为：{chapter:02d} 章节名.pdf")
        return None

    if len(pdf_files) > 1:
        tqdm.write(f"找到多个章节 {chapter} 的PDF文件，将使用第一个：{pdf_files[0].name}")

    return pdf_files[0]


def backup_memory_params(db: Session, chapter: int) -> dict:
    """备份指定章节所有卡片的记忆参数"""
    cards = db.query(Card).filter(Card.chapter == chapter).all()
    backup = {}
    for card in cards:
        backup[card.concept.strip()] = {
            "memory_strength": card.memory_strength,
            "stability": card.stability,
            "easiness_factor": card.easiness_factor,
            "repetitions": card.repetitions,
            "next_review_at": card.next_review_at,
            "last_reviewed_at": card.last_reviewed_at,
        }
    tqdm.write(f"备份章节 {chapter} 记忆数据：{len(backup)} 条")
    return backup


def delete_old_chapter_content(db: Session, chapter: int):
    """删除旧章节卡片 + 题目"""
    db.query(Question).filter(Question.chapter == chapter).delete()
    db.query(Card).filter(Card.chapter == chapter).delete()
    db.commit()
    tqdm.write(f"已清空章节 {chapter} 旧内容")


def generate_new_cards(
    db: Session,
    chapter: int,
    text: str,
    prompt: str,
    memory_backup: dict
) -> list:
    """生成新卡片并恢复记忆参数"""
    result = generate_json(prompt, text)
    if not result or "cards" not in result:
        tqdm.write("LLM返回卡片格式错误")
        return []

    card_list = result["cards"]
    new_cards = []

    for data in card_list:
        try:
            concept = data["concept"].strip()
            card = Card(
                chapter=chapter,
                concept=data["concept"],
                front=data["front"],
                back=data["back"],
                difficulty=data["difficulty"],
                related_concepts=data.get("related_concepts", []),
            )

            if concept in memory_backup:
                param = memory_backup[concept]
                card.memory_strength = param["memory_strength"]
                card.stability = param["stability"]
                card.easiness_factor = param["easiness_factor"]
                card.repetitions = param["repetitions"]
                card.next_review_at = param["next_review_at"]
                card.last_reviewed_at = param["last_reviewed_at"]

            db.add(card)
            db.flush()
            new_cards.append(card)

        except Exception as e:
            tqdm.write(f"跳过无效卡片：{str(e)}")
            continue

    db.commit()
    tqdm.write(f"新卡片生成完成：{len(new_cards)} 张")
    return new_cards


def generate_new_questions(db: Session, cards: list, prompt: str):
    """为新卡片生成新题目"""
    success = 0
    with tqdm(total=len(cards), desc="生成题目", leave=True, unit="张") as pbar:
        for card in cards:
            content = f"概念：{card.concept}\n正面：{card.front}\n背面：{card.back}"
            res = generate_json(prompt, content)

            if not res or "questions" not in res:
                tqdm.write(f"卡片 {card.id} 生成题目失败")
                pbar.update(1)
                continue

            for q in res["questions"]:
                try:
                    db.add(Question(
                        card_id=card.id,
                        chapter=card.chapter,
                        stem=q["stem"],
                        options=q["options"],
                        answer=q["answer"],
                        explanation=q.get("explanation", ""),
                        question_type="single_choice",
                        difficulty=q["difficulty"]
                    ))
                    success += 1
                except Exception as e:
                    tqdm.write(f"题目写入失败：{str(e)}")
                    continue

            pbar.update(1)

    db.commit()
    tqdm.write(f"新题目生成完成：{success} 道")


def refresh_chapter(chapter: int):
    """热替换主流程"""
    tqdm.write(f"\n开始热替换章节 {chapter}（保留学习进度）")
    db: Session = next(get_db())

    try:
        backup = backup_memory_params(db, chapter)
        delete_old_chapter_content(db, chapter)

        pdf_path = find_chapter_pdf(chapter)
        if not pdf_path:
            return

        chapter_text = extract_text(str(pdf_path))
        if not chapter_text.strip():
            tqdm.write("未找到章节 PDF 或 PDF 为空")
            return

        card_prompt = load_prompt(PROMPT_CARD)
        q_prompt = load_prompt(PROMPT_QUESTION)

        new_cards = generate_new_cards(db, chapter, chapter_text, card_prompt, backup)
        if not new_cards:
            tqdm.write("未生成任何新卡片")
            return

        generate_new_questions(db, new_cards, q_prompt)

        tqdm.write(f"\n章节 {chapter} 热替换完成！记忆进度已保留")

    except Exception as e:
        db.rollback()
        tqdm.write(f"\n热替换失败：{str(e)}")
        tqdm.write("已回滚所有更改，数据库未受影响")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="章节内容热替换（保留学习进度）")
    parser.add_argument("--chapter", type=int, required=True, help="要刷新的章节号")
    args = parser.parse_args()

    refresh_chapter(args.chapter)