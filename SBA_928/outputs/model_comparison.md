# Original and Fine-Tuned Model Comparison

Both models use `sshleifer/tiny-gpt2` and identical deterministic decoding settings: greedy decoding, 50 maximum new tokens, and repetition penalty 1.1. The comparison is qualitative and does not claim statistical accuracy.

## 1. Consumer Behavior

**Evaluation prompt:** Describe a reproducible method for analyzing repeat-purchase behavior.

**Baseline output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Fine-tuned output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## 2. Market Trends

**Evaluation prompt:** Explain how to assess monthly demand trends without inventing results.

**Baseline output:**

```text
factors mutual deflect Television boils factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors
```

**Fine-tuned output:**

```text
factors mutual deflect Television boils factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors factors
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## 3. Competitor Analysis

**Evaluation prompt:** Plan competitor analysis when only internal retail data is available.

**Baseline output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Fine-tuned output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## 4. Pricing

**Evaluation prompt:** Outline a careful analysis of price and purchase quantity.

**Baseline output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Fine-tuned output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## 5. Customer Segmentation

**Evaluation prompt:** Propose fair behavior-based customer segments.

**Baseline output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Fine-tuned output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## 6. Regional Analysis

**Evaluation prompt:** Compare UK and non-UK markets while addressing unequal sample sizes.

**Baseline output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Fine-tuned output:**

```text
stairs vendors stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs stairs
```

**Qualitative comparison:** The baseline continuation has 50 words and uses 0 tracked category terms (none). The fine-tuned continuation has 50 words and uses 0 (none). These observable surface features indicate task alignment only; they do not establish factual accuracy or statistical quality.

## Overall Discussion

`tiny-gpt2` is intentionally very small, and this project uses only a few training steps on a small educational dataset. Its continuations may be repetitive, incoherent, or only weakly related to market research. The LoRA run demonstrates a reproducible parameter-efficient fine-tuning workflow; it should not be treated as a production model or a reliable analyst. Human review and calculations against the source data remain necessary.
