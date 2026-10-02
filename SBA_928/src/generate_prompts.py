"""Generate deterministic market-research prompts from UCI Online Retail context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = 352
DATASET_NAME = "UCI Online Retail (ID 352)"
PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_DIR / "data" / "prompts.csv"


@dataclass(frozen=True)
class MarketContext:
    source_label: str
    provenance_note: str
    transaction_count: str
    countries: str
    products: str
    quantity_summary: str
    price_summary: str


FALLBACK_CONTEXT = MarketContext(
    source_label=f"{DATASET_NAME} - fallback metadata only",
    provenance_note=(
        "The live UCI retrieval was unavailable. The following context is labeled "
        "metadata, not downloaded transaction evidence."
    ),
    transaction_count="approximately 541,909 transactions (published metadata)",
    countries="a UK-based retailer serving multiple countries (published metadata)",
    products="gift and household-product descriptions (published metadata)",
    quantity_summary="Quantity is available for analysis; no fallback statistic was calculated",
    price_summary="UnitPrice is available for analysis; no fallback statistic was calculated",
)


def _find_column(frame: pd.DataFrame, expected: str) -> str | None:
    """Return a column name using case-insensitive, punctuation-insensitive matching."""
    normalized = {"".join(ch for ch in str(c).lower() if ch.isalnum()): c for c in frame.columns}
    return normalized.get("".join(ch for ch in expected.lower() if ch.isalnum()))


def _format_number(value: float) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _extract_frame(dataset: Any) -> pd.DataFrame:
    original = getattr(dataset.data, "original", None)
    if isinstance(original, pd.DataFrame) and not original.empty:
        return original.copy()

    parts = [
        part
        for part in (getattr(dataset.data, "features", None), getattr(dataset.data, "targets", None))
        if isinstance(part, pd.DataFrame) and not part.empty
    ]
    if not parts:
        raise ValueError("UCI response did not contain a usable table")
    return pd.concat(parts, axis=1)


def retrieve_context() -> MarketContext:
    """Retrieve UCI data and calculate a compact, reproducible context summary."""
    try:
        from ucimlrepo import fetch_ucirepo

        frame = _extract_frame(fetch_ucirepo(id=DATASET_ID))
        country_col = _find_column(frame, "Country")
        description_col = _find_column(frame, "Description")
        quantity_col = _find_column(frame, "Quantity")
        price_col = _find_column(frame, "UnitPrice")

        required = {
            "Country": country_col,
            "Description": description_col,
            "Quantity": quantity_col,
            "UnitPrice": price_col,
        }
        missing = [name for name, column in required.items() if column is None]
        if missing:
            raise ValueError(f"missing expected columns: {', '.join(missing)}")

        countries = sorted(frame[country_col].dropna().astype(str).str.strip().unique())
        products = sorted(frame[description_col].dropna().astype(str).str.strip().unique())
        products = [product for product in products if product][:5]
        quantities = pd.to_numeric(frame[quantity_col], errors="coerce").dropna()
        prices = pd.to_numeric(frame[price_col], errors="coerce").dropna()

        if quantities.empty or prices.empty:
            raise ValueError("quantity or price columns contained no numeric values")

        country_preview = ", ".join(countries[:8])
        if len(countries) > 8:
            country_preview += f", and {len(countries) - 8} more"

        return MarketContext(
            source_label=f"{DATASET_NAME} - retrieved via ucimlrepo",
            provenance_note="Context statistics were calculated from the retrieved transaction table.",
            transaction_count=f"{len(frame):,} transaction rows",
            countries=f"{len(countries)} countries/regions ({country_preview})",
            products=", ".join(products),
            quantity_summary=(
                f"median quantity {_format_number(float(quantities.median()))}; "
                f"range {_format_number(float(quantities.min()))} to "
                f"{_format_number(float(quantities.max()))}"
            ),
            price_summary=(
                f"median unit price {_format_number(float(prices.median()))}; "
                f"range {_format_number(float(prices.min()))} to "
                f"{_format_number(float(prices.max()))}"
            ),
        )
    except Exception as exc:  # A network failure must not prevent reproducible prompt generation.
        print(f"UCI retrieval unavailable ({type(exc).__name__}: {exc}).")
        print("Using clearly labeled fallback metadata; no transaction-level claims will be made.")
        return FALLBACK_CONTEXT


CATEGORY_SPECS = {
    "consumer_behavior": {
        "scenario": "Understand repeat-purchase and basket behavior without assuming customer motives.",
        "focus": "consumer behavior",
        "method": "cohort, repeat-purchase, basket-size, and return-rate analysis",
        "comparison": "first-time versus repeat customers",
        "decision": "retention planning",
        "risk": "demographic_assumptions",
    },
    "market_trends": {
        "scenario": "Identify time-based demand patterns while separating seasonality from one-time events.",
        "focus": "market trends",
        "method": "monthly revenue, order-volume, product-mix, and year-over-year trend analysis",
        "comparison": "high-volume versus low-volume periods",
        "decision": "inventory and campaign timing",
        "risk": "historical_data_bias",
    },
    "competitor_analysis": {
        "scenario": "Build an internal benchmark when the dataset contains no direct competitor records.",
        "focus": "competitor analysis",
        "method": "internal category, price-band, assortment, and customer-retention benchmarks",
        "comparison": "product categories using internal performance as a proxy benchmark",
        "decision": "future competitor-research priorities",
        "risk": "product_category_bias",
    },
    "pricing": {
        "scenario": "Evaluate price and quantity relationships without treating correlation as causation.",
        "focus": "pricing",
        "method": "price-band, quantity, revenue, return-rate, and sensitivity analysis",
        "comparison": "lower-price versus higher-price product bands",
        "decision": "responsible pricing tests",
        "risk": "income_economic_assumptions",
    },
    "customer_segmentation": {
        "scenario": "Develop behavior-based segments without inferring protected personal traits.",
        "focus": "customer segmentation",
        "method": "recency, frequency, monetary value, basket size, and return behavior",
        "comparison": "high-frequency versus occasional customers",
        "decision": "segment-specific engagement",
        "risk": "demographic_assumptions",
    },
    "regional_analysis": {
        "scenario": "Compare markets while accounting for the dataset's strong UK representation.",
        "focus": "regional analysis",
        "method": "country-level customer, order, revenue, basket, and return-rate analysis",
        "comparison": "the United Kingdom versus sufficiently sampled non-UK markets",
        "decision": "regional research and expansion",
        "risk": "regional_overrepresentation",
    },
}


def _context_text(context: MarketContext) -> str:
    return (
        f"Dataset context: {context.transaction_count}; {context.countries}; representative "
        f"descriptions include {context.products}; {context.quantity_summary}; {context.price_summary}. "
        f"{context.provenance_note}"
    )


def build_prompts(context: MarketContext) -> list[dict[str, str]]:
    """Build exactly five useful prompt forms for each of six categories."""
    rows: list[dict[str, str]] = []
    prompt_number = 1
    context_text = _context_text(context)

    for category, spec in CATEGORY_SPECS.items():
        forms = [
            (
                "direct_question",
                f"What analyses would reveal {spec['focus']} in the Online Retail data? "
                f"Use {spec['method']}. Distinguish calculated evidence from assumptions.",
            ),
            (
                "analyst_role",
                f"Act as a market research analyst. Create a concise analysis plan to {spec['scenario'].lower()} "
                f"Use {spec['method']}, state data-cleaning steps, and do not invent results.",
            ),
            (
                "comparison",
                f"Design a fair comparison of {spec['comparison']}. Name the metrics, minimum sample checks, "
                "confounders, and limitations that should be reported.",
            ),
            (
                "evidence_focused",
                f"Using only evidence that can be calculated from InvoiceNo, StockCode, Description, Quantity, "
                f"InvoiceDate, UnitPrice, CustomerID, and Country, explain how to study {spec['focus']}. "
                "Separate observations, interpretations, and unknowns.",
            ),
            (
                "decision_support",
                f"Prepare decision support for {spec['decision']}. Recommend analyses and decision thresholds, "
                "identify uncertainty, and list additional evidence needed before action.",
            ),
        ]

        for variation_type, prompt_body in forms:
            rows.append(
                {
                    "prompt_id": f"MR-{prompt_number:03d}",
                    "category": category,
                    "scenario": spec["scenario"],
                    "prompt": f"{context_text}\n\nTask: {prompt_body}",
                    "variation_type": variation_type,
                    "source_dataset": context.source_label,
                    "bias_risk": spec["risk"],
                }
            )
            prompt_number += 1
    return rows


def main() -> None:
    context = retrieve_context()
    rows = build_prompts(context)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False, encoding="utf-8", lineterminator="\n")
    print(f"Created {len(rows)} deterministic prompts at {OUTPUT_PATH}")
    print(f"Categories: {', '.join(CATEGORY_SPECS)}")
    print(f"Source mode: {context.source_label}")


if __name__ == "__main__":
    main()
