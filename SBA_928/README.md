# SBA 928: Enhancing Market Research with AI Prompt Engineering

## Project Objective

This educational project uses a public online-retail dataset to build diverse
market-research prompts, prepare supervised examples, demonstrate
parameter-efficient fine-tuning, compare the original and adapted models, and
review bias and fairness risks. It is a small, reproducible workflow rather
than a production analytics or modeling system.

## SBA Requirements Addressed

1. Source a public market-research-related dataset.
2. Generate multiple prompt forms across six market-research categories.
3. Prepare compact instruction-response training records.
4. Fine-tune `sshleifer/tiny-gpt2` with PEFT/LoRA.
5. Compare the base and fine-tuned models on six common prompts.
6. Analyze bias risks and propose practical fairness strategies.

## Dataset

The project attempts to retrieve UCI dataset ID 352 with `ucimlrepo`:

> Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
> https://doi.org/10.24432/C5BW33

The CC BY 4.0 dataset contains approximately 541,909 transactions from a
UK-based non-store retailer, dated 2010-12-01 through 2011-12-09. Its fields
include `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`,
`UnitPrice`, `CustomerID`, and `Country`.

The full source dataset is not committed. If retrieval is unavailable,
`generate_prompts.py` uses clearly labeled published metadata so the pipeline
can still be demonstrated. Fallback metadata is never presented as downloaded
transaction evidence.

## Folder Structure

```text
SBA_928/
|-- data/
|   |-- source/                 # ignored local source data, if used
|   |-- prompts.csv
|   `-- fine_tuning_data.jsonl
|-- models/                     # generated LoRA adapter; ignored by Git
|-- outputs/
|   |-- model_comparison.md
|   `-- bias_report.md
|-- report/                     # supplied report workspace
|-- screenshots/                # evidence captured for the SBA report
`-- src/
    |-- generate_prompts.py
    |-- prepare_finetuning.py
    |-- fine_tune.py
    |-- compare_models.py
    `-- bias_analysis.py
```

The supplied assignment PDF and Word report template remain unchanged.

## Setup

Install Python 3.11 or newer and
[uv](https://docs.astral.sh/uv/), then run from the repository root:

```powershell
uv sync
```

`uv sync` creates a local `.venv` and installs the dependencies declared in
`pyproject.toml`.

## Execution

Run the scripts in this order:

```powershell
uv run python SBA_928/src/generate_prompts.py
uv run python SBA_928/src/prepare_finetuning.py
uv run python SBA_928/src/fine_tune.py
uv run python SBA_928/src/compare_models.py
uv run python SBA_928/src/bias_analysis.py
```

The first run of prompt generation requires network access to retrieve UCI
data; otherwise it automatically uses labeled fallback metadata. The first
fine-tuning run requires network access to download `sshleifer/tiny-gpt2`.

## Expected Outputs

- `data/prompts.csv`: 30 deterministic prompts (five forms in each of six categories).
- `data/fine_tuning_data.jsonl`: 30 compact instruction-response records.
- `models/market-research-lora/`: the generated LoRA adapter and tokenizer files.
- `outputs/model_comparison.md`: six side-by-side model evaluations.
- `outputs/bias_report.md`: bias assessment, mitigations, and fairness checklist.

## Limitations

- The historical dataset represents one retailer and is heavily UK-centered;
  it is not representative of all consumers or markets.
- Fallback metadata supports workflow reproduction but not transactional
  findings.
- `tiny-gpt2` is intentionally tiny. One epoch over 30 examples demonstrates
  PEFT/LoRA mechanics, not strong language quality or reliable market insight.
- Generated text can be inaccurate or incoherent and always needs human review.
- The comparison is qualitative; it does not claim statistical accuracy or
  production readiness.
