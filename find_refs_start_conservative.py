#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced PDF Reference/Appendix Start Page Detector

This script provides more conservative detection to find the FIRST page
where references likely begin, not just the page with the highest score.

Usage:
    python find_refs_start_conservative.py paper.pdf
"""

import re
import sys
import fitz  # PyMuPDF

# Common section headers that indicate start of references/appendices
HEAD_PATTERNS = [
    r"^\s*references\s*$",
    r"^\s*bibliography\s*$",
    r"^\s*reference\s*$",
    r"^\s*appendix\s*$",
    r"^\s*appendices\s*$",
    r"^\s*supplementary\s*(materials?|information)\s*$",
    r"^\s*acknowledg(e)?ments\s*$",
]


def is_heading_hit(text: str) -> bool:
    """Check if page contains a clear reference/appendix section heading."""
    lines = [ln.strip().lower() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:25]:
        for pat in HEAD_PATTERNS:
            if re.match(pat, ln):
                return True
    return False


def refs_likeness_score(text: str) -> float:
    """Calculate how much a page looks like a references section."""
    t = text.lower()
    if len(t) < 200:
        return 0.0

    bracket_cites = len(re.findall(r"\[\s*\d{1,3}\s*\]", t))
    year_hits     = len(re.findall(r"\b(19|20)\d{2}\b", t))
    doi_hits      = len(re.findall(r"\bdoi\b|10\.\d{4,9}/[-._;()/:a-z0-9]+", t))
    etal_hits     = len(re.findall(r"\bet al\.\b", t))
    url_hits      = len(re.findall(r"https?://", t))

    L = max(len(t), 1)
    score = (bracket_cites*6 + year_hits*1 + doi_hits*8 + etal_hits*4 + url_hits*2) / (L/1000)
    return score


def find_start_page(pdf_path: str, verbose: bool = False) -> int:
    """
    Find the page number where references/appendices likely start.
    Uses a more conservative approach to find the FIRST page with references.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}", file=sys.stderr)
        sys.exit(1)
    
    scores = []
    
    # Stage 1: Look for explicit headings
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text", sort=True)
        
        if is_heading_hit(text):
            if verbose:
                print(f"Found heading on page {i+1}", file=sys.stderr)
            doc.close()
            return i + 1
        
        scores.append(refs_likeness_score(text))
    
    # Stage 2: Find FIRST page that exceeds threshold (more conservative)
    # Lower threshold to catch earlier reference pages
    THRESHOLD = 30.0  # Lowered from 40.0
    
    if verbose:
        print(f"Page scores:", file=sys.stderr)
        for i, score in enumerate(scores):
            if score > 20:  # Only show pages with some reference-like content
                print(f"  Page {i+1}: {score:.2f}", file=sys.stderr)
    
    # Find first page that exceeds threshold
    for i, score in enumerate(scores):
        if score > THRESHOLD:
            if verbose:
                print(f"First page above threshold ({THRESHOLD}): page {i+1} (score: {score:.2f})", file=sys.stderr)
            doc.close()
            return i + 1
    
    # Stage 3: Find first page in a sequence of high-scoring pages
    # Look for where reference-like content starts to appear consistently
    WINDOW_SIZE = 3
    AVG_THRESHOLD = 25.0
    
    for i in range(len(scores) - WINDOW_SIZE + 1):
        window_avg = sum(scores[i:i+WINDOW_SIZE]) / WINDOW_SIZE
        if window_avg > AVG_THRESHOLD:
            if verbose:
                print(f"Found reference-like window starting at page {i+1} (avg score: {window_avg:.2f})", file=sys.stderr)
            doc.close()
            return i + 1
    
    # Stage 4: Fallback - return page with highest score
    if scores:
        best = max(range(len(scores)), key=lambda j: scores[j])
        if verbose:
            print(f"Fallback: highest scoring page is {best+1} (score: {scores[best]:.2f})", file=sys.stderr)
        doc.close()
        return best + 1
    
    doc.close()
    return doc.page_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_refs_start_conservative.py <pdf_file> [--verbose]", file=sys.stderr)
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    start_page = find_start_page(pdf_file, verbose=verbose)
    print(start_page)
