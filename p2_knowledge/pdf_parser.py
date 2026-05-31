# 课件 PDF 文本提取模块（使用 pdfplumber）
# 需实现：
#   extract_text(pdf_path)        → str，逐页提取并拼接为整章文本
#   extract_by_chapter(data_dir)  → dict {chapter_num: text}，扫描 data/ 目录批量处理
# 文件命名约定：08_学习与记忆.pdf（章节号_章节名.pdf）
# 提取结果作为 LLM 的输入上下文，无需向量数据库
