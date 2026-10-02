"""Compare deterministic continuations from tiny-gpt2 and its LoRA adapter."""

from __future__ import annotations

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed


MODEL_NAME = "sshleifer/tiny-gpt2"
SEED = 928
PROJECT_DIR = Path(__file__).resolve().parents[1]
ADAPTER_PATH = PROJECT_DIR / "models" / "market-research-lora"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "model_comparison.md"

EVALUATION_PROMPTS = [
    ("consumer_behavior", "Describe a reproducible method for analyzing repeat-purchase behavior."),
    ("market_trends", "Explain how to assess monthly demand trends without inventing results."),
    ("competitor_analysis", "Plan competitor analysis when only internal retail data is available."),
    ("pricing", "Outline a careful analysis of price and purchase quantity."),
    ("customer_segmentation", "Propose fair behavior-based customer segments."),
    ("regional_analysis", "Compare UK and non-UK markets while addressing unequal sample sizes."),
]

CATEGORY_TERMS = {
    "consumer_behavior": {"customer", "purchase", "repeat", "basket", "cohort", "return"},
    "market_trends": {"trend", "monthly", "season", "revenue", "volume", "time"},
    "competitor_analysis": {"competitor", "benchmark", "category", "external", "assortment"},
    "pricing": {"price", "quantity", "revenue", "product", "band", "causal"},
    "customer_segmentation": {"segment", "recency", "frequency", "customer", "behavior"},
    "regional_analysis": {"country", "regional", "market", "sample", "UK", "order"},
}


def generate(model: AutoModelForCausalLM, tokenizer: AutoTokenizer, prompt: str) -> str:
    encoded = tokenizer(prompt, return_tensors="pt")
    input_length = encoded["input_ids"].shape[1]
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            max_new_tokens=50,
            do_sample=False,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )
    continuation = tokenizer.decode(generated[0, input_length:], skip_special_tokens=True).strip()
    return continuation or "(The model produced no text continuation.)"


def observed_comparison(category: str, baseline: str, tuned: str) -> str:
    terms = CATEGORY_TERMS[category]
    base_hits = sorted(term for term in terms if term.lower() in baseline.lower())
    tuned_hits = sorted(term for term in terms if term.lower() in tuned.lower())
    return (
        f"The baseline continuation has {len(baseline.split())} words and uses {len(base_hits)} tracked "
        f"category terms ({', '.join(base_hits) or 'none'}). The fine-tuned continuation has "
        f"{len(tuned.split())} words and uses {len(tuned_hits)} ({', '.join(tuned_hits) or 'none'}). "
        "These observable surface features indicate task alignment only; they do not establish factual "
        "accuracy or statistical quality."
    )


def main() -> None:
    if not ADAPTER_PATH.exists():
        raise FileNotFoundError(f"Missing adapter at {ADAPTER_PATH}. Run fine_tune.py first.")

    set_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    baseline_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    baseline_model.eval()
    tuned_base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    tuned_model = PeftModel.from_pretrained(tuned_base, ADAPTER_PATH)
    tuned_model.eval()

    sections = [
        "# Original and Fine-Tuned Model Comparison",
        "",
        f"Both models use `{MODEL_NAME}` and identical deterministic decoding settings: greedy decoding, "
        "50 maximum new tokens, and repetition penalty 1.1. The comparison is qualitative and does not "
        "claim statistical accuracy.",
    ]

    for index, (category, prompt) in enumerate(EVALUATION_PROMPTS, start=1):
        full_prompt = f"Instruction: {prompt}\n\nResponse:"
        baseline = generate(baseline_model, tokenizer, full_prompt)
        tuned = generate(tuned_model, tokenizer, full_prompt)
        sections.extend(
            [
                "",
                f"## {index}. {category.replace('_', ' ').title()}",
                "",
                f"**Evaluation prompt:** {prompt}",
                "",
                "**Baseline output:**",
                "",
                "```text",
                baseline,
                "```",
                "",
                "**Fine-tuned output:**",
                "",
                "```text",
                tuned,
                "```",
                "",
                f"**Qualitative comparison:** {observed_comparison(category, baseline, tuned)}",
            ]
        )

    sections.extend(
        [
            "",
            "## Overall Discussion",
            "",
            "`tiny-gpt2` is intentionally very small, and this project uses only a few training steps on a "
            "small educational dataset. Its continuations may be repetitive, incoherent, or only weakly "
            "related to market research. The LoRA run demonstrates a reproducible parameter-efficient "
            "fine-tuning workflow; it should not be treated as a production model or a reliable analyst. "
            "Human review and calculations against the source data remain necessary.",
            "",
        ]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Compared {len(EVALUATION_PROMPTS)} evaluation prompts.")
    print(f"Comparison report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
