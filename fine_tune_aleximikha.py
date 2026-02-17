from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# ========================= CONFIG (RTX 3060 Optimized) =========================
MODEL_NAME = "unsloth/llama-3.1-8b-bnb-4bit"
MAX_SEQ_LENGTH = 2048
DATASET_PATH = "dataset_aleximikha.jsonl"
OUTPUT_DIR = "aleximikha-nezmorph-final"

print("Loading model for RTX 3060...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=torch.bfloat16,           # Best for RTX 30 series
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=64,                           # Higher rank = stronger personality
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# Load dataset
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

def formatting_prompts_func(example):
    return {
        "text": f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{example['instruction']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{example['output']}<|eot_id|>"""
    }

dataset = dataset.map(formatting_prompts_func)

print(f"Starting training on {len(dataset)} examples...")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=4,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=6,      # Good for 12GB VRAM
        gradient_accumulation_steps=4,
        warmup_steps=20,
        max_steps=600,                      # ~1 epoch on your 43k dataset
        learning_rate=2e-4,
        fp16=False,
        bf16=True,                          # Enabled for RTX 3060
        logging_steps=20,
        output_dir=OUTPUT_DIR,
        optim="adamw_8bit",
        seed=3407,
        report_to="none",
    ),
)

print("Training started... This will take 2.5–5 hours.")
trainer.train()

# Save the model
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Training Complete! Model saved in: {OUTPUT_DIR}")