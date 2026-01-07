# PDF Reference/Appendix Detection Tool | PDF引用附录检测工具

[English](#english) | [中文](#中文)

---

## English

Automatically detect where references and appendices begin in academic PDF papers, helping reduce token usage and costs when processing papers with LLMs.

### Features

- 🔍 **Auto-detect reference sections** - Uses heading matching and content analysis
- ✂️ **PDF trimming** - Automatically remove references and appendices
- 💰 **Save token costs** - Reduce text sent to GPT and other LLMs by ~50%
- 🚀 **Lightweight** - Only requires PyMuPDF, no additional tools needed

### Installation

Install PyMuPDF dependency:

```bash
pip install pymupdf
```

### Usage

#### 1. Detect Reference Start Page

```bash
python find_refs_start.py paper.pdf
```

Example output:
```
9
```

This means references/appendices start from page 9.

**Verbose mode** (shows detection process):

```bash
python find_refs_start.py paper.pdf --verbose
```

#### 2. Trim PDF

Trim PDF based on detected page number, keeping only main content:

```bash
# First detect
START_PAGE=$(python find_refs_start.py paper.pdf)

# Then trim (keeps pages 1-9, including References page)
python trim_pdf.py paper.pdf $START_PAGE trimmed.pdf
```

Or specify page number directly:

```bash
python trim_pdf.py paper.pdf 9 trimmed.pdf
```

#### 3. Complete Workflow

Full workflow for processing papers before sending to LLMs:

```bash
# 1. Download or prepare PDF
# paper.pdf

# 2. Detect reference start page
python find_refs_start.py paper.pdf
# Output: 9

# 3. Trim PDF
python trim_pdf.py paper.pdf 9 paper_main_content.pdf

# 4. Convert trimmed PDF to text or send directly to LLM
# Token count is now significantly reduced!
```

#### 4. Batch Processing

Process all PDF files in a directory at once:

```bash
# Process all PDFs in current directory, output to ./output
python batch_process.py

# Specify custom input and output directories
python batch_process.py --input-dir /path/to/pdfs --output-dir /path/to/output

# Verbose mode for detailed information
python batch_process.py --verbose
```

#### 5. Concatenate PDFs

Merge all trimmed PDFs into a single file for easier processing:

```bash
# Merge all PDFs in output directory
python concat_pdfs.py ./output all_papers_combined.pdf

# Use default output filename (merged.pdf)
python concat_pdfs.py ./output

# Verbose mode
python concat_pdfs.py ./output combined.pdf --verbose
```

### How It Works

The tool uses a three-stage detection strategy:

#### Stage 1: Heading Matching
Scans each page for common reference/appendix headers:
- References / Bibliography
- Appendix / Appendices
- Supplementary Materials
- Acknowledgements

#### Stage 2: Content Scoring
If no clear heading is found, scores each page based on reference-like features:
- Citation brackets `[12]` (weight: 6)
- Year patterns `2019` (weight: 1)
- DOI patterns (weight: 8)
- "et al." occurrences (weight: 4)
- URLs (weight: 2)

Finds consecutive pages with high scores to identify reference sections.

#### Stage 3: Fallback
Returns the page with the highest reference-likeness score.

### Adjusting Detection Thresholds

If detection results are inaccurate, modify parameters in `find_refs_start.py`:

```python
# Around line 90
THRESHOLD = 40.0  # Increase for more conservative detection
CONSECUTIVE_PAGES = 2  # Number of consecutive high-scoring pages needed
```

### Example Output

```bash
$ python find_refs_start.py sample-paper.pdf --verbose
Found heading on page 9

$ python trim_pdf.py sample-paper.pdf 9 output.pdf
✓ Trimmed PDF saved to: output.pdf
  Original: 12 pages
  Trimmed: 9 pages (removed 3 pages)
```

### Files

- `find_refs_start.py` - Main detection script
- `trim_pdf.py` - PDF trimming utility
- `batch_process.py` - Batch processing script for multiple PDFs
- `concat_pdfs.py` - PDF concatenation utility
- `README.md` - This documentation

### Notes

- Optimized for English academic papers
- Non-standard formats may require threshold adjustments
- Use `--verbose` mode to verify detection results
- Backup original PDFs before trimming

### License

MIT

---

## 中文

自动检测学术论文PDF中引用和附录的起始页码，帮助在使用LLM处理论文时减少token使用量和成本。

### 功能特点

- 🔍 **自动检测引用区起始页** - 使用标题匹配和内容特征分析
- ✂️ **PDF裁剪功能** - 自动移除引用和附录部分
- 💰 **节省token成本** - 减少发送给GPT等LLM的文本量约50%
- 🚀 **轻量级** - 只依赖PyMuPDF，无需额外工具

### 安装

安装PyMuPDF依赖：

```bash
pip install pymupdf
```

### 使用方法

#### 1. 检测引用起始页

```bash
python find_refs_start.py paper.pdf
```

输出示例：
```
9
```

表示从第9页开始是引用/附录部分。

**详细模式**（显示检测过程）：

```bash
python find_refs_start.py paper.pdf --verbose
```

#### 2. 裁剪PDF

根据检测到的页码裁剪PDF，只保留主要内容：

```bash
# 先检测
START_PAGE=$(python find_refs_start.py paper.pdf)

# 再裁剪（保留第1-9页，包括References页）
python trim_pdf.py paper.pdf $START_PAGE trimmed.pdf
```

或者直接指定页码：

```bash
python trim_pdf.py paper.pdf 9 trimmed.pdf
```

#### 3. 完整工作流

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

#### 4. 批量处理

一次处理目录中的所有PDF文件：

```bash
# 处理当前目录所有PDF，输出到 ./output
python batch_process.py

# 指定自定义输入和输出目录
python batch_process.py --input-dir /path/to/pdfs --output-dir /path/to/output

# 详细模式显示处理信息
python batch_process.py --verbose
```

#### 5. 合并PDF

将所有裁剪后的PDF合并为一个文件，方便批量处理：

```bash
# 合并output目录中的所有PDF
python concat_pdfs.py ./output all_papers_combined.pdf

# 使用默认输出文件名 (merged.pdf)
python concat_pdfs.py ./output

# 详细模式
python concat_pdfs.py ./output combined.pdf --verbose
```

### 工作原理

工具使用三阶段检测策略：

#### 阶段1：标题匹配
扫描每一页，查找常见的引用/附录标题：
- References / Bibliography
- Appendix / Appendices  
- Supplementary Materials
- Acknowledgements

#### 阶段2：内容特征打分
如果没找到明确标题，则基于以下特征对每页打分：
- 引用括号 `[12]` 的数量（权重：6）
- 年份模式 `2019` 的数量（权重：1）
- DOI模式的数量（权重：8）
- "et al." 的数量（权重：4）
- URL的数量（权重：2）

找到连续多页得分都很高的位置，判定为引用区开始。

#### 阶段3：兜底策略
如果前两个阶段都没有明确结果，返回得分最高的页面。

### 调整检测阈值

如果检测结果不准确，可以修改 `find_refs_start.py` 中的参数：

```python
# 第90行附近
THRESHOLD = 40.0  # 提高此值会更保守（更晚才认为是引用区）
CONSECUTIVE_PAGES = 2  # 需要连续多少页高分才判定为引用区
```

### 示例输出

```bash
$ python find_refs_start.py sample-paper.pdf --verbose
Found heading on page 9

$ python trim_pdf.py sample-paper.pdf 9 output.pdf
✓ Trimmed PDF saved to: output.pdf
  Original: 12 pages
  Trimmed: 9 pages (removed 3 pages)
```

### 文件说明

- `find_refs_start.py` - 主检测脚本
- `trim_pdf.py` - PDF裁剪工具
- `batch_process.py` - 批量处理脚本
- `concat_pdfs.py` - PDF合并工具
- `README.md` - 本文档

### 注意事项

- 工具主要针对英文学术论文优化
- 对于非标准格式的论文可能需要调整阈值
- 建议先用 `--verbose` 模式检查检测结果是否合理
- 裁剪前建议备份原始PDF

### 许可证

MIT
