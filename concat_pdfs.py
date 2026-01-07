#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Concatenation Utility

Merges all PDF files in a directory into a single PDF file.
Useful for combining trimmed papers into one file for batch processing with LLMs.

Usage:
    python concat_pdfs.py input_dir output.pdf
    
Example:
    python concat_pdfs.py ./output combined_papers.pdf
"""

import sys
import os
from pathlib import Path
import fitz  # PyMuPDF


def concat_pdfs(input_dir: str, output_file: str, verbose: bool = False):
    """
    Concatenate all PDF files in a directory into a single PDF.
    
    Args:
        input_dir: Directory containing PDF files to merge
        output_file: Path for the output merged PDF
        verbose: If True, print detailed information
    """
    input_path = Path(input_dir).resolve()
    
    if not input_path.exists():
        print(f"❌ Error: Directory '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.is_dir():
        print(f"❌ Error: '{input_path}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Find all PDF files
    pdf_files = sorted(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📁 Found {len(pdf_files)} PDF file(s) in {input_path}")
    print(f"📄 Output file: {output_file}")
    print("-" * 60)
    
    # Create output PDF
    output_doc = fitz.open()
    total_pages = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            if verbose:
                print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            else:
                print(f"[{i}/{len(pdf_files)}] {pdf_file.name}", end="")
            
            # Open source PDF
            src_doc = fitz.open(str(pdf_file))
            page_count = src_doc.page_count
            
            # Insert all pages from source PDF
            output_doc.insert_pdf(src_doc)
            
            total_pages += page_count
            
            if verbose:
                print(f"  ✓ Added {page_count} pages (total: {total_pages})")
            else:
                print(f" - {page_count} pages ✓")
            
            src_doc.close()
            
        except Exception as e:
            print(f"  ❌ Error processing {pdf_file.name}: {e}", file=sys.stderr)
            continue
    
    # Save merged PDF
    try:
        output_doc.save(output_file)
        output_doc.close()
        
        # Get file size
        file_size = os.path.getsize(output_file)
        size_mb = file_size / (1024 * 1024)
        
        print("=" * 60)
        print(f"✅ Successfully merged {len(pdf_files)} PDF files!")
        print(f"📊 Total pages: {total_pages}")
        print(f"💾 File size: {size_mb:.2f} MB")
        print(f"📄 Output: {output_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error saving merged PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python concat_pdfs.py <input_dir> [output_file] [--verbose]", file=sys.stderr)
        print("\nMerges all PDF files in a directory into a single PDF.", file=sys.stderr)
        print("\nArguments:", file=sys.stderr)
        print("  input_dir    Directory containing PDF files to merge", file=sys.stderr)
        print("  output_file  Output PDF filename (default: merged.pdf)", file=sys.stderr)
        print("  --verbose    Show detailed processing information", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python concat_pdfs.py ./output combined_papers.pdf", file=sys.stderr)
        sys.exit(1)
    
    input_dir = sys.argv[1]
    
    # Determine output file
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("--"):
        output_file = sys.argv[2]
    else:
        output_file = "merged.pdf"
    
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    concat_pdfs(input_dir, output_file, verbose=verbose)
