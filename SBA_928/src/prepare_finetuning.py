"""Convert the generated prompt collection into compact supervised examples."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_DIR / "data" / "prompts.csv"
OUTPUT_PATH = PROJECT_DIR / "data" / "fine_tuning_data.jsonl"
REQUIRED_COLUMNS = {
    "prompt_id",
    "category",
    "scenario",
    "prompt",
    "variation_type",
    "source_dataset",
    "bias_risk",
}


CATEGORY_GUIDANCE = {
    "consumer_behavior": (
        "Clean cancellations and missing customer IDs, then examine repeat-purchase rate, order frequency, "
        "basket size, recency, and returns. Compare cohorts over consistent observation windows."
    ),
    "market_trends": (
        "Aggregate orders, units, and revenue by consistent time period; inspect seasonality and product mix, "
        "and flag unusual events before interpreting a trend."
    ),
    "competitor_analysis": (
        "The data has no competitor observations. Use category, assortment, price-band, and retention metrics "
        "only as internal benchmarks, then collect comparable external evidence before competitor claims."
    ),
    "pricing": (
        "Create comparable product and price bands, then measure units, revenue, repeat purchase, and returns. "
        "Control for season and product mix; an association does not establish price causality."
    ),
    "customer_segmentation": (
        "Build behavior-based segments with recency, frequency, monetary value, basket size, and returns. "
        "Validate segment size and stability without inferring demographic or protected traits."
    ),
    "regional_analysis": (
        "Compare countries only after checking customer and order counts. Report per-customer and per-order "
        "metrics with uncertainty, and avoid treating UK-heavy coverage as globally representative."
    ),
}


VARIATION_CLOSERS = {
    "direct_question": "Report the method first, followed by supported findings and limitations.",
    "analyst_role": "Document filters and assumptions so another analyst can reproduce the work.",
    "comparison": "Use like-for-like groups and show sample sizes before interpreting differences.",
    "evidence_focused": "Label calculated observations, interpretations, and unknowns separately.",
    "decision_support": "Define a reversible test and require human review before acting.",
}


def create_response(row: pd.Series) -> str:
    guidance = CATEGORY_GUIDANCE[row["category"]]
    closer = VARIATION_CLOSERS[row["variation_type"]]
    return (
        f"Recommended approach: {guidance} {closer} "
        f"This addresses {row['scenario'].lower()} Exact conclusions must be calculated from the retrieved "
        "data; fallback metadata alone cannot support transaction-level findings."
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing {INPUT_PATH}. Run generate_prompts.py first.")

    prompts = pd.read_csv(INPUT_PATH, dtype=str, keep_default_na=False)
    missing = REQUIRED_COLUMNS.difference(prompts.columns)
    if missing:
        raise ValueError(f"prompts.csv is missing columns: {', '.join(sorted(missing))}")
    if prompts.empty:
        raise ValueError("prompts.csv contains no records")

    unknown_categories = set(prompts["category"]).difference(CATEGORY_GUIDANCE)
    unknown_variations = set(prompts["variation_type"]).difference(VARIATION_CLOSERS)
    if unknown_categories or unknown_variations:
        raise ValueError(
            f"Unsupported categories={sorted(unknown_categories)}; "
            f"variations={sorted(unknown_variations)}"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as output_file:
        for _, row in prompts.iterrows():
            text = f"Instruction:\n{row['prompt'].strip()}\n\nResponse:\n{create_response(row)}"
            output_file.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")

    categories = sorted(prompts["category"].unique())
    print(f"Number of records created: {len(prompts)}")
    print(f"Categories represented: {', '.join(categories)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
