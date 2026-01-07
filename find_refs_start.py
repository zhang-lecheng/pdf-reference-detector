#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Reference/Appendix Start Page Detector

This script analyzes academic PDF papers to automatically detect where
references and appendices begin, helping reduce token usage when processing
papers with LLMs.

Usage:
    python find_refs_start.py paper.pdf
    
Output:
    Page number (1-based) where references/appendices likely start
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
    # Numbered section headings (e.g., "7. References", "A. Appendix")
    r"^\s*\d+\.?\s+references\s*$",
    r"^\s*\d+\.?\s+bibliography\s*$",
    r"^\s*\d+\.?\s+appendix\s*$",
    r"^\s*\d+\.?\s+appendices\s*$",
    r"^\s*[a-z]\.?\s+references\s*$",
    r"^\s*[a-z]\.?\s+appendix\s*$",
]


def is_heading_hit(text: str) -> bool:
    """
    Check if page contains a clear reference/appendix section heading.
    
    Args:
        text: Text content of a PDF page
        
    Returns:
        True if a reference/appendix heading is found
    """
    lines = [ln.strip().lower() for ln in text.splitlines() if ln.strip()]
    # Only check first 25 lines to avoid false positives from body text
    for ln in lines[:25]:
        for pat in HEAD_PATTERNS:
            if re.match(pat, ln):
                return True
    return False


def refs_likeness_score(text: str) -> float:
    """
    Calculate how much a page looks like a references section.
    
    Scores based on common reference patterns:
    - Citation brackets like [12]
    - Years (19xx, 20xx)
    - DOI patterns
    - "et al." occurrences
    - URLs
    
    Args:
        text: Text content of a PDF page
        
    Returns:
        Normalized score (higher = more reference-like)
    """
    t = text.lower()
    if len(t) < 200:
        return 0.0

    # Count reference-like patterns
    bracket_cites = len(re.findall(r"\[\s*\d{1,3}\s*\]", t))          # [12]
    year_hits     = len(re.findall(r"\b(19|20)\d{2}\b", t))           # 2019
    doi_hits      = len(re.findall(r"\bdoi\b|10\.\d{4,9}/[-._;()/:a-z0-9]+", t))
    etal_hits     = len(re.findall(r"\bet al\.\b", t))
    url_hits      = len(re.findall(r"https?://", t))

    # Normalize by text length to avoid bias toward longer pages
    L = max(len(t), 1)
    score = (bracket_cites*6 + year_hits*1 + doi_hits*8 + etal_hits*4 + url_hits*2) / (L/1000)
    return score


def find_start_page(pdf_path: str, verbose: bool = False) -> int:
    """
    Find the page number where references/appendices likely start.
    
    Uses a conservative approach to find the FIRST page with references,
    not just the page with the highest score.
    
    Args:
        pdf_path: Path to the PDF file
        verbose: If True, print debug information
        
    Returns:
        1-based page number where references/appendices start
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
            return i + 1  # 1-based page number
        
        scores.append(refs_likeness_score(text))
    
    # Stage 2: Look for consecutive high-scoring pages (most reliable for no-heading papers)
    # This catches reference sections that span multiple pages
    CONSECUTIVE_THRESHOLD = 35.0
    CONSECUTIVE_PAGES = 2
    
    for i in range(len(scores) - CONSECUTIVE_PAGES + 1):
        if all(s > CONSECUTIVE_THRESHOLD for s in scores[i:i+CONSECUTIVE_PAGES]):
            if verbose:
                print(f"Found consecutive high-scoring pages starting at {i+1}", file=sys.stderr)
                print(f"Scores: {scores[i:i+CONSECUTIVE_PAGES]}", file=sys.stderr)
            doc.close()
            return i + 1
    
    # Stage 3: Find FIRST page with very high score (likely references)
    # Higher threshold to avoid false positives from citation-heavy main text
    HIGH_THRESHOLD = 45.0
    
    if verbose:
        print(f"Page scores:", file=sys.stderr)
        for i, score in enumerate(scores):
            if score > 20:  # Only show pages with some reference-like content
                print(f"  Page {i+1}: {score:.2f}", file=sys.stderr)
    
    # Find first page that exceeds high threshold
    for i, score in enumerate(scores):
        if score > HIGH_THRESHOLD:
            if verbose:
                print(f"First page above high threshold ({HIGH_THRESHOLD}): page {i+1} (score: {score:.2f})", file=sys.stderr)
            doc.close()
            return i + 1
    
    # Stage 4: Find first page in a sequence of moderately high-scoring pages
    # Look for where reference-like content starts to appear consistently
    WINDOW_SIZE = 3
    AVG_THRESHOLD = 30.0
    
    for i in range(len(scores) - WINDOW_SIZE + 1):
        window_avg = sum(scores[i:i+WINDOW_SIZE]) / WINDOW_SIZE
        if window_avg > AVG_THRESHOLD:
            # Additional check: make sure at least one page in window has high score
            if any(s > 35 for s in scores[i:i+WINDOW_SIZE]):
                if verbose:
                    print(f"Found reference-like window starting at page {i+1} (avg score: {window_avg:.2f})", file=sys.stderr)
                doc.close()
                return i + 1
    
    # Stage 5: Fallback - return page with highest score if it's reasonably high
    if scores:
        best = max(range(len(scores)), key=lambda j: scores[j])
        if scores[best] > 30.0:  # Only use fallback if score is reasonable
            if verbose:
                print(f"Fallback: highest scoring page is {best+1} (score: {scores[best]:.2f})", file=sys.stderr)
            doc.close()
            return best + 1
    
    # If all else fails, assume last 20% of document is references
    fallback_page = max(1, int(len(scores) * 0.8))
    if verbose:
        print(f"No clear references found, using 80% heuristic: page {fallback_page}", file=sys.stderr)
    doc.close()
    return fallback_page


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_refs_start.py <pdf_file> [--verbose]", file=sys.stderr)
        print("\nDetects where references/appendices start in academic papers.", file=sys.stderr)
        print("Output: Page number (1-based) where references likely begin.", file=sys.stderr)
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    start_page = find_start_page(pdf_file, verbose=verbose)
    print(start_page)
