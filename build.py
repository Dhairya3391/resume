#!/usr/bin/env python3
"""Validate resume LaTeX files and compile PDFs into ./pdfs/{sde,backend,ai_ml_engineer}."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent
LATEX_DIR = REPO_ROOT / "latex"
PDF_DIR = REPO_ROOT / "pdfs"

TARGET_FILES = [
    "resume_sde.tex",
    "resume_sde_2page.tex",
    "resume_backend.tex",
    "resume_backend_2page.tex",
    "resume_ai_ml_engineer.tex",
    "resume_ai_ml_engineer_2page.tex",
]

REQUIRED_GLOBAL_STRINGS = [
    "Dhairya Adroja",
    "9664847885",
    "dhairyaadroja3391@gmail.com",
    "CGPA: 8.68/10",
    "First Class with Distinction",
    "Multiicon Hackathon Winner",
    "University Chess Gold Medalist",
]

REQUIRED_HEADER_LINKS = [
    r"\href{https://www.linkedin.com/in/adrojadhairya}{LinkedIn}",
    r"\href{https://www.github.com/Dhairya3391}{GitHub}",
    r"\href{https://dhairya.codes}{Portfolio}",
]

FORBIDDEN_STRINGS = [
    "Teaching Assistant",
]

AUX_FILE_SUFFIXES = (
    ".aux",
    ".log",
    ".out",
    ".toc",
    ".fls",
    ".fdb_latexmk",
    ".synctex.gz",
    ".nav",
    ".snm",
    ".vrb",
    ".xdv",
)

PDFLATEX_PAGE_RE = re.compile(r"Output written on .*?\(\s*(\d+)\s+pages?", re.DOTALL)


def find_achievements_block(tex: str, file_name: str) -> str:
    section_re = re.compile(
        r"\\section\{Achievements\}(.*?)(?=\\section\{|\\end\{document\})",
        re.DOTALL,
    )
    match = section_re.search(tex)
    if not match:
        raise ValueError(f"{file_name}: missing Achievements section")
    return match.group(1)


def validate_tex_file(path: Path) -> List[str]:
    errors: List[str] = []
    tex = path.read_text(encoding="utf-8")
    name = path.name

    for required in REQUIRED_GLOBAL_STRINGS:
        if required not in tex:
            errors.append(f"{name}: missing required text: {required}")

    for required_link in REQUIRED_HEADER_LINKS:
        if required_link not in tex:
            errors.append(f"{name}: missing required header link: {required_link}")

    for forbidden in FORBIDDEN_STRINGS:
        if forbidden.lower() in tex.lower():
            errors.append(f"{name}: forbidden text found: {forbidden}")

    if "\\section{Experience}" not in tex:
        errors.append(f"{name}: missing Experience section")
    if "\\section{Education}" not in tex:
        errors.append(f"{name}: missing Education section")

    try:
        achievements_block = find_achievements_block(tex, name)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    achievement_items = re.findall(r"\\resumeItem\{", achievements_block)
    if len(achievement_items) != 2:
        errors.append(
            f"{name}: Achievements should contain exactly 2 items, found {len(achievement_items)}"
        )

    if "Multiicon Hackathon Winner" not in achievements_block:
        errors.append(f"{name}: Achievements missing Multiicon Hackathon entry")
    if "University Chess Gold Medalist" not in achievements_block:
        errors.append(f"{name}: Achievements missing Chess entry")

    return errors


def compile_tex(path: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={output_dir}",
        str(path),
    ]
    return subprocess.run(cmd, text=True, capture_output=True, cwd=REPO_ROOT)


def extract_page_count(text: str) -> Optional[int]:
    match = PDFLATEX_PAGE_RE.search(text)
    if match:
        return int(match.group(1))
    return None


def expected_page_count(tex_name: str) -> int:
    return 2 if tex_name.endswith("_2page.tex") else 1


def extract_resume_type(tex_name: str) -> str:
    """Extract resume type from filename.

    Examples:
    - resume_sde.tex -> sde
    - resume_sde_2page.tex -> sde
    - resume_backend.tex -> backend
    - resume_ai_ml_engineer_2page.tex -> ai_ml_engineer
    """
    # Remove 'resume_' prefix and '.tex' suffix
    name = tex_name.replace("resume_", "").replace(".tex", "")
    # Remove '_2page' suffix if present
    name = name.replace("_2page", "")
    return name


def output_subdir_for(tex_name: str) -> Path:
    resume_type = extract_resume_type(tex_name)
    return PDF_DIR / resume_type


def output_pdf_path_for(tex_name: str) -> Path:
    return output_subdir_for(tex_name) / Path(tex_name).with_suffix(".pdf").name


def cleanup_aux_files(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for path in output_dir.rglob("*"):
        if path.is_file() and any(path.name.endswith(s) for s in AUX_FILE_SUFFIXES):
            path.unlink()


def cleanup_target_pdfs() -> None:
    target_pdf_names = {Path(name).with_suffix(".pdf").name for name in TARGET_FILES}
    # Get all resume type directories
    resume_types = {extract_resume_type(name) for name in TARGET_FILES}
    candidate_dirs = [PDF_DIR] + [PDF_DIR / resume_type for resume_type in resume_types]

    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for pdf_name in target_pdf_names:
            path = directory / pdf_name
            if path.exists() and path.is_file():
                path.unlink()


def validate_page_counts(compiler_outputs: Dict[str, str]) -> List[str]:
    errors: List[str] = []
    for name in TARGET_FILES:
        pdf_path = output_pdf_path_for(name)
        pdf_name = pdf_path.name
        if not pdf_path.exists():
            errors.append(f"{pdf_path.relative_to(PDF_DIR)}: missing PDF output")
            continue

        page_count = extract_page_count(compiler_outputs.get(name, ""))
        if page_count is None:
            log_path = output_subdir_for(name) / Path(name).with_suffix(".log").name
            if log_path.exists():
                log_text = log_path.read_text(encoding="utf-8", errors="ignore")
                page_count = extract_page_count(log_text)

        if page_count is None:
            errors.append(
                f"{pdf_path.relative_to(PDF_DIR)}: could not determine page count from pdflatex output"
            )
            continue

        expected = expected_page_count(name)
        if page_count != expected:
            errors.append(
                f"{pdf_path.relative_to(PDF_DIR)}: expected {expected} page(s), found {page_count} page(s)"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-page-check",
        action="store_true",
        help="Skip strict one-page/two-page PDF count validation.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep pdflatex auxiliary files (.aux/.log/.out) in ./pdfs.",
    )
    args = parser.parse_args()

    missing = [name for name in TARGET_FILES if not (LATEX_DIR / name).exists()]
    if missing:
        print("Missing expected .tex files:")
        for name in missing:
            print(f"  - {name}")
        return 1

    print("Validating resume sources...")
    validation_errors: List[str] = []
    for name in TARGET_FILES:
        validation_errors.extend(validate_tex_file(LATEX_DIR / name))

    if validation_errors:
        print("Validation failed:")
        for err in validation_errors:
            print(f"  - {err}")
        return 1
    print("Source validation passed.")

    # Create output directories by resume type
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    resume_types = {extract_resume_type(name) for name in TARGET_FILES}
    for resume_type in sorted(resume_types):
        (PDF_DIR / resume_type).mkdir(parents=True, exist_ok=True)

    print(f"Compiling PDFs into: {PDF_DIR}")
    for resume_type in sorted(resume_types):
        print(f"  - {resume_type}: {PDF_DIR / resume_type}")

    if shutil.which("pdflatex") is None:
        print("pdflatex not found in PATH. Install a TeX distribution and rerun.")
        return 2

    cleanup_aux_files(PDF_DIR)
    cleanup_target_pdfs()

    compile_failures = False
    compiler_outputs: Dict[str, str] = {}
    for name in TARGET_FILES:
        tex_path = LATEX_DIR / name
        output_dir = output_subdir_for(name)
        result = compile_tex(tex_path, output_dir)
        pdf_name = tex_path.with_suffix(".pdf").name
        combined_output = (result.stdout + "\n" + result.stderr).strip()
        compiler_outputs[name] = combined_output
        relative_pdf_path = output_pdf_path_for(name).relative_to(PDF_DIR)

        if result.returncode != 0:
            compile_failures = True
            print(f"  - FAILED: {name}")
            # Print trailing output for easier debugging.
            combined = combined_output.splitlines()
            tail = combined[-30:] if combined else ["(no compiler output)"]
            for line in tail:
                print(f"      {line}")
        else:
            page_count = extract_page_count(combined_output)
            if page_count is not None:
                print(f"  - OK: {relative_pdf_path} ({page_count} page(s))")
            else:
                print(f"  - OK: {relative_pdf_path}")

    if compile_failures:
        return 1

    page_errors: List[str] = []
    if not args.skip_page_check:
        print("Validating PDF page counts...")
        page_errors = validate_page_counts(compiler_outputs)
        if page_errors:
            print("Page validation failed:")
            for err in page_errors:
                print(f"  - {err}")
            return 1
        print("Page validation passed.")

    if not args.keep_artifacts:
        cleanup_aux_files(PDF_DIR)

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
