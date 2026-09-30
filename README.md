# Knowing When to Revise: Confidence-Gated Self-Correction in Large Language Models

Term paper, Advanced Topics in Computational Text and Media Sciences, University of Trier.
Fakhr E Alam Khan, Matriculation No. 1818211.

## Idea
LLMs often break correct answers when they "self-correct". This project tests whether the model
should revise **only when it is unsure** about its first answer (confidence gating).

## How it works
1. The model (Qwen2.5-7B-Instruct) answers a question.
2. A confidence score is computed: verbalised confidence, self-consistency (10 samples) or P(True).
3. If the confidence is below a threshold, the answer is revised; otherwise it is kept.

## What I did
- Derived a simple analytical model of when gating can help, and how much.
- Built the pipeline and ran it on GSM8K and HotpotQA (500 questions each, 100 dev / 400 test) on Kaggle GPUs.
- Compared the three signals against never / always revising, IoE, majority voting and an oracle gate.
- Tested the analytical model's predictions against the measured results.

## Result
Self-critique almost never fixes a wrong answer, so no gate beats never revising. Self-consistency spots
wrong answers well (AUROC 0.95 on GSM8K), and used as the revision step it does fix errors, matching the
model's prediction. **The bottleneck is the revision step, not the decision of when to revise.**

## Repository
| Folder | Contents |
|---|---|
| `paper/` | LaTeX sources and final PDF |
| `cgsc/` | Code: data, prompts, scoring, pipeline, analysis |
| `kaggle/` | Kaggle notebook used for inference (2× T4, vLLM) |
| `results/` | Raw outputs, summary, tables and figures |

## Reproduce
1. Run `kaggle/cgsc_run.ipynb` on Kaggle (2× T4 GPUs) and copy the two `.jsonl` outputs to `results/raw/`.
2. Run `python cgsc/analyze.py` to regenerate all tables and figures.
3. Build the paper: `cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main`.

Note: the reported results come from a full run plus a re-run of only the self-consistency samples,
because a seeding bug made the first samples identical. With the fixed code, one notebook run reproduces everything.
