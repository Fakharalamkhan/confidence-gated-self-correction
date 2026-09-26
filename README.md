# Knowing When to Revise: Confidence-Gated Self-Correction in Large Language Models

This repository contains the complete experimental code, raw pipeline outputs, evaluation data, and LaTeX source files for the term paper on confidence-gated self-correction. We study whether training-free confidence gating (verbalized confidence, self-consistency agreement, and P(True) verification) can prevent accuracy degradation during intrinsic self-correction. Experiments evaluate Qwen2.5-7B-Instruct on grade-school mathematics (GSM8K) and multi-hop question answering (HotpotQA).

## Repository Overview

- **`cgsc/`**: Core Python package for dataset loading, prompt construction, answer extraction, scoring (exact match, lenient, F1), sanity checks, and full evaluation analysis.
- **`kaggle/`**: Kaggle execution notebooks and automation scripts for dual-T4 GPU inference using vLLM.
- **`paper/`**: Complete LaTeX sources, section texts, tables, figures, bibliography (`references.bib`), and pre-submission validation script (`check_paper.py`).
- **`results/`**: Raw evaluation runs (`results/raw/*.jsonl`), summary metrics (`summary.json`), transition logs (`rw_cases.csv`), sanity reports, environment metadata, and compiled LaTeX/CSV result tables and figures.

## Models and Datasets

- **Model**: `Qwen/Qwen2.5-7B-Instruct` (served via vLLM with tensor parallelism across 2x NVIDIA T4 GPUs in 16-bit precision).
- **Datasets**:
  - **GSM8K** (`main`, test set split): 500 questions (100 dev / 400 test, seed 42).
  - **HotpotQA** (`distractor`, validation set split): 500 questions (100 dev / 400 test, seed 42).

## Reproduction

1. **Inference Pipeline**:
   - Run `kaggle/cgsc_run.ipynb` on a Kaggle notebook equipped with 2x NVIDIA T4 GPUs (or any dual-GPU environment).
   - The notebook installs `vllm==0.6.6.post1`, runs the initial answer generation ($A_0$), the three confidence signals ($S_{\text{verb}}$, $S_{\text{sc10}}$, $S_{\text{verif}}$), revision ($A_1$), IoE baseline, and majority voting.

2. **Analysis and Table Generation**:
   - Compute all metrics, transition matrices, bootstrap AUROCs, cost models, and LaTeX tables:
     ```bash
     python cgsc/analyze.py
     ```

3. **Paper Build and Validation**:
   - Compile the paper and verify pre-submission criteria (page limits, reference counts, formatting):
     ```bash
     cd paper
     pdflatex main.tex
     bibtex main
     pdflatex main.tex
     pdflatex main.tex
     python check_paper.py
     ```
