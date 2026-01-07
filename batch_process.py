#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch PDF Processing Script

Processes all PDF files in the current directory:
1. Detects where references/appendices start
2. Trims PDFs to keep only main content (including References page)
3. Saves trimmed PDFs to ./output directory

Usage:
    python batch_process.py
    
Optional arguments:
    --input-dir DIR     Input directory (default: current directory)
    --output-dir DIR    Output directory (default: ./output)
    --verbose          Show detailed processing information
"""

import os
import sys
import argparse
from pathlib import Path
from find_refs_start import find_start_page
from trim_pdf import trim_pdf


def process_all_pdfs(input_dir: str = ".", output_dir: str = "./output", verbose: bool = False):
    """
    Process all PDF files in the input directory.
    
    Args:
        input_dir: Directory containing PDF files to process
        output_dir: Directory to save trimmed PDFs
        verbose: If True, print detailed information
    """
    # Convert to Path objects
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files in input directory
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_path}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s) in {input_path}")
    print(f"📂 Output directory: {output_path}")
    print("-" * 60)
    
    # Process each PDF
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_name = pdf_file.name
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_name}")
        
        try:
            # Detect reference start page
            if verbose:
                print(f"  🔍 Detecting references...")
            
            start_page = find_start_page(str(pdf_file), verbose=verbose)
            
            if verbose:
                print(f"  ✓ References start at page {start_page}")
            else:
                print(f"  📄 References start at page {start_page}")
            
            # Create output filename
            output_file = output_path / f"trimmed_{pdf_name}"
            
            # Trim PDF
            if verbose:
                print(f"  ✂️  Trimming PDF...")
            
            # Temporarily redirect stdout to capture trim_pdf output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                trim_pdf(str(pdf_file), start_page, str(output_file))
            
            trim_output = f.getvalue()
            
            # Parse the output to get page counts
            if "Trimmed:" in trim_output:
                # Extract page info from output
                for line in trim_output.split('\n'):
                    if "Trimmed:" in line:
                        print(f"  {line.strip()}")
            
            print(f"  ✅ Saved to: {output_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1
            if verbose:
                import traceback
                traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Processing Summary:")
    print(f"  ✅ Successfully processed: {success_count} file(s)")
    if error_count > 0:
        print(f"  ❌ Failed: {error_count} file(s)")
    print(f"  📂 Output directory: {output_path}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Batch process PDF files to detect and trim references/appendices"
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Input directory containing PDF files (default: current directory)"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for trimmed PDFs (default: ./output)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed processing information"
    )
    
    args = parser.parse_args()
    
    process_all_pdfs(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
