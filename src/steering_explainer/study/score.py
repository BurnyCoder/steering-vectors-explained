"""score.py — primary metric: P(positive) of each completion from the SiEBERT sentiment classifier.

Global context: SiEBERT (`siebert/sentiment-roberta-large-english`, Hartmann et al. 2023) is a
RoBERTa-large binary sentiment model fine-tuned on 15 diverse datasets, chosen because completions
are web-like text, not one domain. It is independent of GPT-2-XL and of the steering vector.
Docs: transformers text-classification pipeline, `top_k=None` returns all label scores
(https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.TextClassificationPipeline).
"""

from transformers import pipeline


class SentimentScorer:
    """Callable: list of texts -> list of P(POSITIVE)."""

    def __init__(self, model_name: str, device: str):
        self.pipe = pipeline("text-classification", model=model_name, device=0 if device == "cuda" else -1,
                             top_k=None, truncation=True)  # top_k=None: scores for both labels

    def __call__(self, texts: list[str]) -> list[float]:
        texts = [t if t.strip() else "." for t in texts]  # classifier needs non-empty input; "." is neutral filler
        outs = self.pipe(texts, batch_size=32)
        return [next(d["score"] for d in o if d["label"].upper() == "POSITIVE") for o in outs]
