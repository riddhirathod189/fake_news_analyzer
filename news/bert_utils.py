# news/bert_utils.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class BertFakeNewsClassifier:
    def __init__(self, model_name="mrm8488/bert-tiny-finetuned-fake-news-detection"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ["REAL", "FAKE"]
        self.model.eval()

    def predict(self, text):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1).detach().numpy()[0]
            pred_idx = probs.argmax()
            return {
                "label": self.labels[pred_idx].lower(),
                "confidence": float(probs[pred_idx]) * 100
            }

# Optional: initialize on startup to avoid reloading model
bert_classifier = BertFakeNewsClassifier()
