"""
PDF 解析模块
功能：提取PDF文本内容，按章节批量解析
遵循系统设计：仅作为LLM生成卡片/题目的上下文，不做向量存储
命名规范：data目录下文件为 两位数字 章节名.pdf（例：01 绪论.pdf、08 学习与记忆.pdf）
"""
import os
from pathlib import Path
from typing import Dict, Optional
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

# 核心解析函数
def extract_text(pdf_path: str) -> str:
    """
    提取单份PDF文件的全部文本（逐页拼接）
    :param pdf_path: PDF文件绝对/相对路径
    :return: 拼接后的纯文本字符串，空则返回""
    """
    try:
        # 校验文件是否存在
        if not os.path.exists(pdf_path):
            print(f"文件不存在：{pdf_path}")
            return ""

        # 初始化PDF读取器
        reader = PdfReader(pdf_path)
        full_text = []

        # 逐页提取文本
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                full_text.append(page_text.strip())

        # 拼接所有页面文本
        raw_text = "\n".join(full_text)
        print(f"成功提取PDF：{Path(pdf_path).name}，总页数：{len(reader.pages)}")
        return raw_text

    except PdfReadError:
        print(f"解析失败：该文件不是有效的PDF -> {pdf_path}")
        return ""
    except Exception as e:
        print(f"PDF提取异常：{str(e)} -> {pdf_path}")
        return ""

#批量章节解析函数
def extract_by_chapter(data_dir: str = "./data") -> Dict[int, str]:
    """
    按命名规范批量提取data目录下的所有章节PDF
    命名规则：两位数字 章节名称.pdf（例：01 绪论.pdf、08 学习与记忆.pdf）
    :param data_dir: 存放章节PDF的目录（默认根目录data）
    :return: 字典 {章节号(int): 章节文本(str)}
    """
    chapter_text_map: Dict[int, str] = {}
    data_path = Path(data_dir)

    # 校验目录是否存在
    if not data_path.exists():
        print(f"数据目录不存在，自动创建：{data_dir}")
        data_path.mkdir(parents=True)
        return chapter_text_map

    # 遍历目录所有PDF文件
    for file in data_path.glob("*.pdf"):
        filename = file.name
        # 按空格分割，提取章节号
        if " " not in filename:
            print(f"跳过命名不规范文件：{filename}（需：两位数字 章节名.pdf）")
            continue

        try:
            # 提取前缀数字作为章节号（自动去掉前导零）
            chapter_num_str = filename.split(" ")[0]
            chapter_num = int(chapter_num_str)
            # 提取当前PDF文本
            chapter_text = extract_text(str(file))
            # 存入字典
            chapter_text_map[chapter_num] = chapter_text
            print(f"章节 {chapter_num} 文本提取完成：{filename}")

        except ValueError:
            print(f"跳过非数字章节文件：{filename}")
            continue

    print(f"\n批量解析完成！成功提取章节数：{len(chapter_text_map)}")
    return chapter_text_map

# 本地测试
if __name__ == "__main__":
    # 测试：提取根目录data下所有章节PDF
    test_result = extract_by_chapter("./data")
    # 打印结果预览
    for chapter, text in test_result.items():
        print(f"\n=== 章节 {chapter} 文本预览（前200字符）===")
        print(text[:200] + "..." if len(text) > 200 else text)