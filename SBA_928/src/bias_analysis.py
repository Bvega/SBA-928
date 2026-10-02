"""Create a transparent bias review of the prompt collection and source dataset."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_DIR / "data" / "prompts.csv"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "bias_report.md"

RISK_EXPLANATIONS = {
    "demographic_assumptions": (
        "Behavioral records do not identify motives or protected traits. Segment labels can become unfair "
        "proxies if analysts invent demographic explanations."
    ),
    "regional_overrepresentation": (
        "The retailer is UK-based, so patterns may reflect UK customers, operations, currency, and holidays "
        "more strongly than other markets."
    ),
    "income_economic_assumptions": (
        "Unit price and order value are not reliable measures of customer income, affordability, or willingness "
        "to pay."
    ),
    "product_category_bias": (
        "The assortment of one gift-oriented retailer cannot represent all products, industries, or competitors."
    ),
    "historical_data_bias": (
        "Transactions from 2010-2011 reflect a past period and may not transfer to current demand, channels, "
        "prices, or customer expectations."
    ),
    "cultural_context_bias": (
        "Country fields alone do not explain language, cultural context, local events, or customer preferences."
    ),
}


def markdown_table(counter: Counter[str], first_header: str) -> list[str]:
    lines = [f"| {first_header} | Prompt count |", "|---|---:|"]
    lines.extend(f"| {label.replace('_', ' ')} | {count} |" for label, count in sorted(counter.items()))
    return lines


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing {INPUT_PATH}. Run generate_prompts.py first.")

    prompts = pd.read_csv(INPUT_PATH, dtype=str, keep_default_na=False)
    required = {"category", "bias_risk", "source_dataset"}
    missing = required.difference(prompts.columns)
    if missing:
        raise ValueError(f"prompts.csv is missing columns: {', '.join(sorted(missing))}")

    category_counts = Counter(prompts["category"])
    explicit_risk_counts = Counter(prompts["bias_risk"])
    # These contextual risks affect every prompt even when another risk is the row's primary label.
    contextual_risks = {"historical_data_bias", "cultural_context_bias"}
    assessed_risks = set(explicit_risk_counts).union(contextual_risks)
    unknown = assessed_risks.difference(RISK_EXPLANATIONS)
    if unknown:
        raise ValueError(f"Missing risk explanations for: {', '.join(sorted(unknown))}")

    source_modes = sorted(prompts["source_dataset"].unique())
    report = [
        "# Bias and Fairness Analysis",
        "",
        "## 1. Bias Assessment",
        "",
        f"This review covers {len(prompts)} prompts across {len(category_counts)} market-research categories. "
        "The counts below check prompt balance, but equal prompt counts do not by themselves make the source "
        "data representative or the model fair.",
        "",
        *markdown_table(category_counts, "Prompt category"),
        "",
        "Primary bias-risk labels recorded in `prompts.csv`:",
        "",
        *markdown_table(explicit_risk_counts, "Primary risk label"),
        "",
        "The following six risk areas were assessed:",
        "",
    ]
    for risk in sorted(RISK_EXPLANATIONS):
        label = risk.replace("_", " ").title()
        coverage = explicit_risk_counts.get(risk, 0)
        report.append(f"- **{label}:** {RISK_EXPLANATIONS[risk]} Primary label on {coverage} prompts.")

    report.extend(
        [
            "",
            "## 2. Dataset Limitations",
            "",
            "- The source covers transactions from one UK-based non-store retailer between December 2010 and "
            "December 2011; it is not a current or universal picture of retail.",
            "- UK activity is overrepresented, while some country groups may be too small for stable comparison.",
            "- Missing customer IDs, cancellations, returns, negative quantities, and unusual prices require "
            "documented cleaning choices.",
            "- The fields do not directly measure demographics, income, attitudes, satisfaction, motivations, "
            "competitor activity, marketing exposure, or cultural context.",
            "- Product descriptions and this retailer's assortment can create product/category bias.",
            f"- Prompt source mode(s): {'; '.join(source_modes)}. If fallback metadata was used, no "
            "transaction-level conclusion can be supported until the dataset is retrieved.",
            "",
            "## 3. Prompt-Level Risks",
            "",
            "- Segmentation or consumer-behavior prompts may invite stereotypes if behavior is translated into "
            "unsupported demographic profiles.",
            "- Regional comparisons may rank countries without reporting sample size, uncertainty, currency, "
            "operations, or local context.",
            "- Pricing prompts may confuse spending with income or mistake correlation for causal price response.",
            "- Competitor prompts may overstate what internal transactions reveal about external competitors.",
            "- Trend prompts may project 2010-2011 behavior onto a different economic and retail environment.",
            "- Product examples can focus attention on frequent categories and obscure the long tail.",
            "",
            "## 4. Mitigation Strategies",
            "",
            "1. **Demographic diversity:** Do not infer protected traits. If demographic research is necessary, "
            "collect consented, appropriately governed data and evaluate outcomes by relevant groups.",
            "2. **Regional diversity:** Use stratified regional samples, minimum sample thresholds, per-customer "
            "metrics, and locally informed interpretation rather than treating the UK pattern as global.",
            "3. **Avoiding stereotypes:** Describe observed transactions, not imagined identities or motives, and "
            "review segment names for stigmatizing language.",
            "4. **Representative sampling:** Compare the analytic sample with the target market by time, region, "
            "customer coverage, and product mix; reweight or collect additional data where justified.",
            "5. **Explicit uncertainty:** Report denominators, missingness, variability, confidence intervals where "
            "appropriate, and the difference between correlation and causation.",
            "6. **Human review:** Require analyst and stakeholder review before using model suggestions for pricing, "
            "targeting, exclusion, or market-entry decisions.",
            "7. **Source transparency:** Preserve the dataset citation, date range, retrieval/fallback status, "
            "cleaning rules, prompt version, model version, and known gaps.",
            "8. **Industry context:** Validate findings with current retail conditions, competitor research, policy, "
            "currency, fulfillment differences, and local expertise.",
            "",
            "## 5. Fairness Checklist",
            "",
            "- [ ] Are claims supported by calculated evidence rather than fallback metadata?",
            "- [ ] Are missing values, cancellations, returns, and outliers handled transparently?",
            "- [ ] Are demographic attributes and motives left unknown unless directly and ethically measured?",
            "- [ ] Are regional and product groups sufficiently represented, with sample sizes shown?",
            "- [ ] Are historical limits and current industry context stated?",
            "- [ ] Are uncertainty, alternative explanations, and non-causal relationships explicit?",
            "- [ ] Has a human checked for stereotypes, harmful proxies, and unsupported recommendations?",
            "- [ ] Are dataset, prompt, model, and analysis sources documented for reproducibility?",
            "",
        ]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"Analyzed {len(prompts)} prompts across {len(category_counts)} categories.")
    print(f"Primary bias-risk labels: {dict(sorted(explicit_risk_counts.items()))}")
    print(f"Bias report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
