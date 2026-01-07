#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Trimming Utility

Trims a PDF to keep only pages before references/appendices start.
This helps reduce file size and token usage when processing papers with LLMs.

Usage:
    python trim_pdf.py input.pdf refs_start_page output.pdf
    
Example:
    python trim_pdf.py paper.pdf 9 paper_trimmed.pdf
    # Keeps pages 1-9 (including References page), removes page 10 onwards
"""

import sys
import fitz  # PyMuPDF


def trim_pdf(input_path: str, end_page: int, output_path: str) -> None:
    """
    Trim PDF to keep only pages 1 through end_page (inclusive).
    
    Args:
        input_path: Path to input PDF
        end_page: Page number where references start (1-based, this page will be kept)
        output_path: Path for output trimmed PDF
    """
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"Error opening PDF: {e}", file=sys.stderr)
        sys.exit(1)
    
    total_pages = doc.page_count
    
    # Validate page number
    if end_page < 1:
        print(f"Error: end_page must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    if end_page > total_pages:
        print(f"Warning: end_page ({end_page}) exceeds total pages ({total_pages})", file=sys.stderr)
        print(f"Keeping all pages.", file=sys.stderr)
        end_page = total_pages + 1
    
    # Create new PDF with only the pages we want
    output_doc = fitz.open()  # Create empty PDF
    
    # Copy pages 0 to end_page-1 (0-indexed, so this is pages 1 to end_page in 1-based)
    pages_to_keep = end_page
    
    if pages_to_keep == 0:
        print(f"Warning: No pages to keep (end_page=0)", file=sys.stderr)
    else:
        output_doc.insert_pdf(doc, from_page=0, to_page=pages_to_keep-1)
    
    # Save the trimmed PDF
    try:
        output_doc.save(output_path)
        print(f"✓ Trimmed PDF saved to: {output_path}")
        print(f"  Original: {total_pages} pages")
        print(f"  Trimmed: {pages_to_keep} pages (removed {total_pages - pages_to_keep} pages)")
    except Exception as e:
        print(f"Error saving PDF: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        doc.close()
        output_doc.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python trim_pdf.py <input.pdf> <end_page> <output.pdf>", file=sys.stderr)
        print("\nTrims PDF to keep pages 1 through end_page (inclusive).", file=sys.stderr)
        print("Example: python trim_pdf.py paper.pdf 9 trimmed.pdf", file=sys.stderr)
        print("         (keeps pages 1-9, removes page 10 onwards)", file=sys.stderr)
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    try:
        end_page = int(sys.argv[2])
    except ValueError:
        print(f"Error: end_page must be an integer, got '{sys.argv[2]}'", file=sys.stderr)
        sys.exit(1)
    
    output_pdf = sys.argv[3]
    
    trim_pdf(input_pdf, end_page, output_pdf)
