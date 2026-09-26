#!/usr/bin/env python3
"""Pre-submission validation checker for the term paper LaTeX project."""

import os
import re
import sys
import glob
import subprocess

def get_page_texts_pdftotext(pdf_path: str):
    """Attempt extracting page texts using pdftotext executable."""
    try:
        proc = subprocess.run(["pdftotext", pdf_path, "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # Form feed \x0c separates pages in pdftotext
        pages = proc.stdout.split("\x0c")
        if pages and pages[-1].strip() == "":
            pages.pop()
        return pages
    except Exception:
        return None

def get_page_texts_pypdf(pdf_path: str):
    """Fallback extraction using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return pages
    except Exception:
        return None

def main():
    paper_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(paper_dir)

    print("=" * 80)
    print(" PAPER PRE-SUBMISSION VALIDATION REPORT")
    print("=" * 80)

    reasons = []

    # ---------------------------------------------------------
    # Check 1: TODO Count
    # ---------------------------------------------------------
    print("\n[1] TODO Check:")
    tex_files = sorted(glob.glob("*.tex") + glob.glob("sections/*.tex") + glob.glob("appendix/*.tex"))
    todo_list = []
    for tf in tex_files:
        if os.path.exists(tf):
            with open(tf, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, start=1):
                    if r"\todo{" in line:
                        clean_line = line.strip()
                        todo_list.append((tf, line_idx, clean_line))

    print(f"  Total \\todo occurrences found: {len(todo_list)}")
    if todo_list:
        for tf, l_no, text in todo_list:
            print(f"    - {tf}:{l_no} -> {text}")
        reasons.append(f"TODO count is {len(todo_list)} (must be 0 at submission)")
    else:
        print("  PASS: 0 \\todo occurrences found.")

    # ---------------------------------------------------------
    # Check 2: Body Page Count
    # ---------------------------------------------------------
    print("\n[2] Body Page Count Check:")
    pdf_path = "main.pdf"
    if not os.path.exists(pdf_path):
        print(f"  ERROR: {pdf_path} does not exist. Run build.sh first.")
        reasons.append("main.pdf not found; build failed or has not been run")
    else:
        pages = get_page_texts_pdftotext(pdf_path)
        if pages is None:
            pages = get_page_texts_pypdf(pdf_path)

        if pages is None:
            print("  WARN: Neither pdftotext nor pypdf available to extract PDF pages.")
            reasons.append("Could not extract pages from main.pdf to check body page count")
        else:
            total_pages = len(pages)
            ref_page = None
            is_at_top = False

            for p_idx, p_text in enumerate(pages, start=1):
                # Search for References heading
                lines = [l.strip() for l in p_text.splitlines() if l.strip()]
                for l_idx, line in enumerate(lines):
                    if re.search(r'^\s*(?:\d+\.?\s*)?References\s*$', line, re.IGNORECASE):
                        ref_page = p_idx
                        # Check if within the first 3 lines on page
                        is_at_top = (l_idx < 3)
                        break
                if ref_page is not None:
                    break

            if ref_page is None:
                # References heading not found (e.g. skeleton with no citations)
                body_pages = total_pages
                print(f"  Total PDF pages: {total_pages}")
                print("  'References' section heading not yet found in document.")
                print(f"  Estimated body pages: {body_pages}")
            else:
                body_pages = (ref_page - 1) if is_at_top else ref_page
                print(f"  Total PDF pages: {total_pages}")
                print(f"  'References' heading found on page {ref_page} (at top of page: {is_at_top})")
                print(f"  Computed body pages: {body_pages}")

            if not (8 <= body_pages <= 10):
                print(f"  WARN: Body page count {body_pages} is outside the target 8-10 range.")
                reasons.append(f"Body pages ({body_pages}) outside required 8-10 range")
            else:
                print(f"  PASS: Body page count {body_pages} is within the required 8-10 range.")

    # ---------------------------------------------------------
    # Check 3: Reference Count in references.bib
    # ---------------------------------------------------------
    print("\n[3] Reference Count in references.bib:")
    bib_path = "references.bib"
    bib_entries = []
    bib_keys = set()
    bib_entry_data = {}

    if os.path.exists(bib_path):
        with open(bib_path, "r", encoding="utf-8") as f:
            bib_content = f.read()

        # Find entry matches
        pattern = re.compile(r'@(\w+)\s*\{\s*([^,]+),([^@]*)(?=\n@|\Z)', re.DOTALL)
        for match in pattern.finditer(bib_content):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            body = match.group(3)
            bib_entries.append(key)
            bib_keys.add(key)
            bib_entry_data[key] = (entry_type, body)

        n_refs = len(bib_entries)
        print(f"  Number of bib entries: {n_refs}")
        if not (10 <= n_refs <= 15):
            print(f"  WARN: Reference count {n_refs} is outside 10-15 range.")
            reasons.append(f"Reference count ({n_refs}) is outside 10-15 range")
        else:
            print(f"  PASS: Reference count {n_refs} is within 10-15 range.")
    else:
        print("  ERROR: references.bib does not exist.")
        reasons.append("references.bib not found")

    # ---------------------------------------------------------
    # Check 4: Citation Check (Bidirectional)
    # ---------------------------------------------------------
    print("\n[4] Citation Key Consistency Check:")
    cited_keys = set()
    cite_pattern = re.compile(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}')
    for tf in tex_files:
        if os.path.exists(tf):
            with open(tf, "r", encoding="utf-8") as f:
                content = f.read()
            for match in cite_pattern.finditer(content):
                keys = [k.strip() for k in match.group(1).split(",") if k.strip()]
                cited_keys.update(keys)

    missing_keys = cited_keys - bib_keys
    unused_keys = bib_keys - cited_keys

    print(f"  Total unique cited keys in .tex: {len(cited_keys)}")
    if missing_keys:
        print(f"  MISSING KEYS (cited but not in references.bib): {sorted(missing_keys)}")
        reasons.append(f"Missing citation keys in bib: {sorted(missing_keys)}")
    else:
        print("  PASS: No cited keys missing from references.bib.")

    if unused_keys:
        print(f"  UNUSED KEYS (in references.bib but never cited): {sorted(unused_keys)}")
        reasons.append(f"Unused reference keys: {sorted(unused_keys)}")
    else:
        print("  PASS: All keys in references.bib are cited in text.")

    # ---------------------------------------------------------
    # Check 5: Undefined References in main.log
    # ---------------------------------------------------------
    print("\n[5] Undefined References Check in main.log:")
    log_path = "main.log"
    undefined_warnings = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if re.search(r'undefined', line, re.IGNORECASE):
                    # Ignore harmless font/package info unless it's reference/citation
                    if any(w in line.lower() for w in ["reference", "citation", "label"]):
                        undefined_warnings.append(line.strip())
        if undefined_warnings:
            print(f"  Found {len(undefined_warnings)} undefined reference/citation warning(s):")
            for uw in undefined_warnings:
                print(f"    - {uw}")
            reasons.append(f"{len(undefined_warnings)} undefined reference/citation warnings in main.log")
        else:
            print("  PASS: No undefined reference or citation warnings found in main.log.")
    else:
        print("  WARN: main.log not found. Please compile first with build.sh.")
        reasons.append("main.log not found")

    # ---------------------------------------------------------
    # Check 6: DOI, URL, or Eprint for every Bib Entry
    # ---------------------------------------------------------
    print("\n[6] Persistent Identifier Check (doi / url / eprint):")
    missing_id_keys = []
    for key, (etype, body) in bib_entry_data.items():
        has_doi = bool(re.search(r'\bdoi\s*=', body, re.IGNORECASE))
        has_url = bool(re.search(r'\burl\s*=', body, re.IGNORECASE))
        has_eprint = bool(re.search(r'\beprint\s*=', body, re.IGNORECASE))
        if not (has_doi or has_url or has_eprint):
            missing_id_keys.append(key)

    if missing_id_keys:
        print(f"  Bib entries missing doi, url, or eprint ({len(missing_id_keys)}):")
        for k in missing_id_keys:
            print(f"    - {k}")
        reasons.append(f"Bib entries missing doi/url/eprint: {missing_id_keys}")
    else:
        print("  PASS: Every bib entry contains a valid doi, url, or eprint.")

    # ---------------------------------------------------------
    # Check 7: Final Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    if not reasons:
        print("READY TO SUBMIT")
        sys.exit(0)
    else:
        print("NOT READY")
        print("\nReasons:")
        for idx, r in enumerate(reasons, start=1):
            print(f"  {idx}. {r}")
        sys.exit(1)

if __name__ == "__main__":
    main()
