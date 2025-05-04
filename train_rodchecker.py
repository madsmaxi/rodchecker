import pandas as pd
import sys
import csv
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
)
from datasets import Dataset
import os

# === SETUP ===
csv.field_size_limit(sys.maxsize)

# Load CSV
df = pd.read_csv("CEAS_08.csv", quotechar='"', engine="python")

# Keep only body, label, and urls
df = df[['body', 'label', 'urls']]

# ✅ Inject the URL flag into the text body
df['text'] = df.apply(lambda row: f"URL_FLAG_{row['urls']} {row['body']}", axis=1)

# Drop the original 'body' and 'urls' columns
df = df.drop(columns=['body', 'urls'])

# === Load Tokenizer and Model ===
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2
)

# Convert to Dataset
dataset = Dataset.from_pandas(df)
dataset = dataset.shuffle(seed=42).select(range(5000))  # Sample to speed up

# Tokenize
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Split
split_dataset = tokenized_dataset.train_test_split(test_size=0.2)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Training arguments
training_args = TrainingArguments(
    output_dir="./rodchecker_model",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=split_dataset["train"],
    eval_dataset=split_dataset["test"],
    data_collator=data_collator,
)

# === TRAIN ===
trainer.train()

# === SAVE ===
trainer.save_model("./rodchecker_saved_model")
tokenizer.save_pretrained("./rodchecker_saved_model")
