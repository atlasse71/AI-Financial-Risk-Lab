import json
from pathlib import Path
from app import answer_question  # we'll build this in Step 5

DATA_PATH = Path(__file__).parent / "data" / "test_questions.json"


def load_questions() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def topic_matches(expected: str, actual: str) -> bool:
    """Fuzzy match: normalize and check overlap."""
    exp = expected.lower().replace("/", " ").split()
    act = actual.lower().replace("/", " ").split()
    return any(token in act for token in exp if len(token) > 3)


def evaluate() -> None:
    questions = load_questions()
    results = []
    for item in questions:
        q = item["question"]
        expected = item["expected_topic"]
        try:
            answer = answer_question(q)
            match = topic_matches(expected, answer.topic)
            results.append({
                "question": q,
                "expected_topic": expected,
                "actual_topic": answer.topic,
                "topic_match": match,
                "confidence": answer.confidence,
            })
            status = "PASS" if match else "FAIL"
            print(f"[{status}] {q} | expected={expected} | got={answer.topic} | conf={answer.confidence}")
        except Exception as e:
            results.append({"question": q, "error": str(e)})
            print(f"[ERROR] {q} | {e}")

    passed = sum(1 for r in results if r.get("topic_match"))
    print(f"\nTopic-match accuracy: {passed}/{len(questions)}")

    out_path = Path(__file__).parent / "data" / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote results to {out_path}")


if __name__ == "__main__":
    evaluate()