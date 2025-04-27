import pandas as pd
import numpy as np
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
import csv
import sys

# Increase field size
csv.field_size_limit(sys.maxsize)

# ====== LOAD MODEL + TOKENIZER ======
model = DistilBertForSequenceClassification.from_pretrained("./rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("./rodchecker_saved_model")

# ====== LOAD DATASET ======
df = pd.read_csv('CEAS_08.csv', quotechar='"', engine='python')
df = df[['body', 'label']]
df = df.rename(columns={'body': 'text'})

dataset = Dataset.from_pandas(df)

# OPTIONAL: if you trained only on a small subset (like 5000 emails)
dataset = dataset.shuffle(seed=42).select(range(5000))

# ====== TOKENIZE DATA ======
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# ====== SPLIT INTO TRAIN/TEST ======
split_dataset = tokenized_dataset.train_test_split(test_size=0.2)

# ====== PREPARE DATA COLLATOR ======
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# ====== DEFINE METRICS FUNCTION ======
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
    }

# ====== TRAINING ARGUMENTS (Only for evaluation) ======
training_args = TrainingArguments(
    output_dir="./eval_check",
    per_device_eval_batch_size=16
)

# ====== SETUP TRAINER ======
trainer = Trainer(
    model=model,
    args=training_args,
    eval_dataset=split_dataset['test'],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# ====== EVALUATE ======
metrics = trainer.evaluate()
print(metrics)
