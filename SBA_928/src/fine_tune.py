"""Run a deliberately tiny, CPU-compatible LoRA fine-tuning demonstration."""

from __future__ import annotations

import json
from pathlib import Path

from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    set_seed,
)


MODEL_NAME = "sshleifer/tiny-gpt2"
SEED = 928
MAX_SEQUENCE_LENGTH = 128
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "fine_tuning_data.jsonl"
ADAPTER_PATH = PROJECT_DIR / "models" / "market-research-lora"
CHECKPOINT_PATH = PROJECT_DIR / "models" / "training-checkpoints"


def load_records() -> list[dict[str, str]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}. Run prepare_finetuning.py first.")
    with DATA_PATH.open(encoding="utf-8") as input_file:
        records = [json.loads(line) for line in input_file if line.strip()]
    if not records or any(not isinstance(record.get("text"), str) for record in records):
        raise ValueError("Fine-tuning data must contain non-empty JSONL records with a text field")
    return records


def main() -> None:
    set_seed(SEED)
    records = load_records()
    print(f"Model used: {MODEL_NAME}")
    print(f"Number of training records: {len(records)}")
    print(
        "Training configuration: "
        f"seed={SEED}, epochs=1, batch_size=4, max_sequence_length={MAX_SEQUENCE_LENGTH}, "
        "learning_rate=0.0005, LoRA r=4, alpha=8"
    )
    print("Limitation: this tiny CPU run demonstrates the workflow; it is not expected to produce a high-quality model.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    dataset = Dataset.from_list(records)

    def tokenize(batch: dict[str, list[str]]) -> dict[str, list[list[int]]]:
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=MAX_SEQUENCE_LENGTH,
            padding=False,
        )

    tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=4,
        lora_alpha=8,
        lora_dropout=0.05,
        target_modules=["c_attn"],
        fan_in_fan_out=True,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    trainable, total = model.get_nb_trainable_parameters()
    print(f"Trainable parameters: {trainable:,} of {total:,} ({100 * trainable / total:.2f}%)")

    training_args = TrainingArguments(
        output_dir=str(CHECKPOINT_PATH),
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        learning_rate=5e-4,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
        use_cpu=True,
        dataloader_num_workers=0,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    trainer.train()

    ADAPTER_PATH.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(ADAPTER_PATH)
    tokenizer.save_pretrained(ADAPTER_PATH)
    print("Fine-tuning completed successfully.")
    print(f"Adapter path: {ADAPTER_PATH}")


if __name__ == "__main__":
    main()
