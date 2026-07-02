from typing import List, Dict, Any, Tuple, Optional
import os
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


class TextMessageAgent:
    def __init__(self, model_name: Optional[str] = None):
        """Text sentiment agent.

        If ``model_name`` is not provided, this will try to load the
        offline model directory that lives next to this file::

            MENTAL_HEALTH_MODEL/text_model/offline_model/

        Using a path relative to ``__file__`` makes the agent robust
        to the current working directory (e.g. when called from
        api_server.py at the project root).
        """

        # Default to the offline model directory next to this file
        if model_name is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_name = os.path.join(base_dir, "offline_model")

        # Fallback to HuggingFace if offline model is missing
        if not os.path.exists(model_name):
            print(f"[WARNING] Local model not found at {model_name}. Fallback to HuggingFace...")
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

        print(f"[INIT] Loading text sentiment model from: {model_name} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipe = pipeline(
            "text-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=True,   # get scores for all labels
            truncation=True,
            max_length=256,
        )

        self.negative_labels = {"negative", "NEGATIVE"}
        self.positive_labels = {"positive", "POSITIVE"}
        self.neutral_labels = {"neutral", "NEUTRAL"}

    def _message_negativity(self, text: str) -> float:
        """
        Return negativity score in [0, 1] for a single message.
        Higher = more negative.
        """
        if not text.strip():
            return 0.0

        outputs = self.pipe(text)[0]  # list of {label, score}
        negativity = 0.0
        total_weight = 0.0

        for out in outputs:
            label = out["label"]
            score = float(out["score"])

            if label in self.negative_labels:
                weight = 1.0
            elif label in self.neutral_labels:
                weight = 0.5
            elif label in self.positive_labels:
                weight = 0.0
            else:
                weight = 0.5  # unknown label, treat as neutral-ish

            negativity += weight * score
            total_weight += score

        if total_weight == 0:
            return 0.0

        return float(negativity / total_weight)

    def _risk_from_neg_score(self, text_neg_score: float) -> Tuple[str, List[str]]:
        """
        Map daily negativity score to discrete risk level + explanation.
        """
        if text_neg_score >= 0.7:
            return "high", ["Strong negative emotional sentiment detected in daily messages"]
        elif text_neg_score >= 0.4:
            return "medium", ["Mixed or mildly negative emotional sentiment detected in daily messages"]
        else:
            return "low", ["Overall neutral or positive sentiment in daily messages"]

    def analyze_messages(self, messages: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of messages and compute a daily negativity score + risk level.
        """
        if not messages:
            # No messages -> assume no evidence of negative mood
            risk_level, reasons = self._risk_from_neg_score(0.0)
            return {
                "text_neg_score": 0.0,
                "risk_level": risk_level,
                "reasons": reasons,
                "num_messages": 0,
                "per_message": [],
            }

        neg_scores = []
        per_message = []
        for msg in messages:
            neg = self._message_negativity(msg)
            neg_scores.append(neg)
            per_message.append({"message": msg, "negativity": neg})

        daily_neg = float(np.mean(neg_scores))

        # Convert daily_neg into discrete risk + reasons
        risk_level, reasons = self._risk_from_neg_score(daily_neg)

        return {
            "text_neg_score": daily_neg,
            "risk_level": risk_level,
            "reasons": reasons,
            "num_messages": len(messages),
            "per_message": per_message,
        }


if __name__ == "__main__":
    print("[MAIN] Starting demo run for TextMessageAgent...")

    agent = TextMessageAgent()

    example_messages = [
        "I feel very lonely today. No one visited me.",
        "My legs are hurting a lot since morning.",
        "Today was okay, I watched TV with my neighbor.",
        "I am really sad that my children are busy and never call.",
    ]

    result = agent.analyze_messages(example_messages)

    print("\nDaily text analysis result:")
    print(f"  Num messages: {result['num_messages']}")
    print(f"  Daily text_neg_score: {result['text_neg_score']:.3f}")
    print("  Risk level:", result["risk_level"])
    print("  Reasons:", "; ".join(result["reasons"]))
    print("  Per-message negativity:")
    for r in result["per_message"]:
        print(f"   - {r['message']} -> {r['negativity']:.3f}")
  