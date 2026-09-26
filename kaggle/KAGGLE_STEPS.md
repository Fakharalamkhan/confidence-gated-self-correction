# Instructions for Running Llama Settings on Kaggle

## Prerequisites
1. In the Kaggle notebook web editor for `fakharalam1/cgsc-run`:
   - Open **Add-ons -> Secrets**.
   - Make sure your Hugging Face token is stored with label `HF_TOKEN`.
   - **Crucially**: Ensure the toggle/checkbox next to `HF_TOKEN` is turned **ON** (attached to the notebook).
   - Verify **Settings -> Accelerator** is set to **GPU T4 x2**.
   - Verify **Settings -> Internet** is turned **ON**.

## Steps to Run Llama Settings (Tomorrow)
1. Open [`fakharalam1/cgsc-run`](https://www.kaggle.com/code/fakharalam1/cgsc-run) in the Kaggle Web Notebook Editor.
2. In **Cell 0 (PARAMETERS CELL)**, change:
   ```python
   SETTINGS = [
       "llama/gsm8k",
       "llama/hotpotqa",
   ]
   ```
3. Click **Save Version -> Save & Run All (Commit)**.
4. The notebook will:
   - Create the clean isolated virtual environment `/tmp/venv` with `vllm`.
   - Securely read `HF_TOKEN` from `kaggle_secrets.UserSecretsClient().get_secret("HF_TOKEN")` (never printing it) and pass it into the subprocess environment as `HF_TOKEN` and `HUGGING_FACE_HUB_TOKEN`.
   - Run the 20-item dry run for `llama/gsm8k`, run the 7 built-in sanity checks, and if passed, run the full 500 items.
   - Automatically write `llama_gsm8k.jsonl`, `sanity_report_llama_gsm8k.txt`, and `llama_gsm8k_bundle.zip` directly to `/kaggle/working/`.
   - Proceed to `llama/hotpotqa`, run dry run, sanity checks, and full 500 items, and write `llama_hotpotqa.jsonl`, `sanity_report_llama_hotpotqa.txt`, and `llama_hotpotqa_bundle.zip` directly to `/kaggle/working/`.
   - If any step fails or gets an authorization error, it logs the error to `/kaggle/working/errors.txt` without crashing the notebook.
5. Once finished, download the outputs using:
   ```powershell
   kaggle kernels output fakharalam1/cgsc-run -p results/raw/
   ```
