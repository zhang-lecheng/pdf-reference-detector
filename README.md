# PDF Reference/Appendix Detection Tool

自动检测学术论文PDF中引用和附录的起始页码，帮助在使用LLM处理论文时减少token使用量和成本。

## 功能特点

- 🔍 **自动检测引用区起始页** - 使用标题匹配和内容特征分析
- ✂️ **PDF裁剪功能** - 自动移除引用和附录部分
- 💰 **节省token成本** - 减少发送给GPT等LLM的文本量
- 🚀 **轻量级** - 只依赖PyMuPDF，无需额外工具

## 安装

安装PyMuPDF依赖：

```bash
pip install pymupdf
```

## 使用方法

### 1. 检测引用起始页

```bash
python find_refs_start.py sample-paper.pdf
```

输出示例：
```
9
```

表示从第9页开始是引用/附录部分。

**详细模式**（显示检测过程）：

```bash
python find_refs_start.py sample-paper.pdf --verbose
```

### 2. 裁剪PDF

根据检测到的页码裁剪PDF，只保留主要内容：

```bash
# 先检测
START_PAGE=$(python find_refs_start.py sample-paper.pdf)

# 再裁剪（保留第1页到第8页）
python trim_pdf.py sample-paper.pdf $START_PAGE trimmed.pdf
```

或者直接指定页码：

```bash
python trim_pdf.py sample-paper.pdf 9 trimmed.pdf
```

### 3. 完整工作流

处理论文并发送给LLM的完整流程：

```bash
# 1. 下载或准备PDF
# paper.pdf

# 2. 检测引用起始页
python find_refs_start.py paper.pdf
# 输出: 9

# 3. 裁剪PDF
python trim_pdf.py paper.pdf 9 paper_main_content.pdf

# 4. 将裁剪后的PDF转换为文本或直接发送给LLM
# 现在token数量大大减少！
```

## 工作原理

工具使用两阶段检测策略：

### 阶段1：标题匹配
扫描每一页，查找常见的引用/附录标题：
- References / Bibliography
- Appendix / Appendices  
- Supplementary Materials
- Acknowledgements

### 阶段2：内容特征打分
如果没找到明确标题，则基于以下特征对每页打分：
- 引用括号 `[12]` 的数量（权重：6）
- 年份模式 `2019` 的数量（权重：1）
- DOI模式的数量（权重：8）
- "et al." 的数量（权重：4）
- URL的数量（权重：2）

找到连续多页得分都很高的位置，判定为引用区开始。

### 阶段3：兜底策略
如果前两个阶段都没有明确结果，返回得分最高的页面。

## 调整检测阈值

如果检测结果不准确，可以修改 `find_refs_start.py` 中的参数：

```python
# 第90行附近
THRESHOLD = 40.0  # 提高此值会更保守（更晚才认为是引用区）
CONSECUTIVE_PAGES = 2  # 需要连续多少页高分才判定为引用区
```

## 示例输出

```bash
$ python find_refs_start.py sample-paper.pdf --verbose
Found heading on page 9

$ python trim_pdf.py sample-paper.pdf 9 output.pdf
✓ Trimmed PDF saved to: output.pdf
  Original: 12 pages
  Trimmed: 8 pages (removed 4 pages)
```

## 文件说明

- `find_refs_start.py` - 主检测脚本
- `trim_pdf.py` - PDF裁剪工具
- `sample-paper.pdf` - 示例论文
- `README.md` - 本文档

## 注意事项

- 工具主要针对英文学术论文优化
- 对于非标准格式的论文可能需要调整阈值
- 建议先用 `--verbose` 模式检查检测结果是否合理
- 裁剪前建议备份原始PDF

## License

MIT
