import json
from pathlib import Path
from app import answer_question  # we'll build this in Step 5

DATA_PATH = Path(__file__).parent / "data" / "test_questions.json"


def load_questions() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Synonym map: maps a token in the EXPECTED topic to a set of tokens
# that would count as a match in the ACTUAL topic returned by the LLM.
TOPIC_SYNONYMS: dict[str, set[str]] = {
    "banking": {"bank", "sponsor", "fintech", "payments", "deposit"},
    "fintech": {"bank", "sponsor", "payments"},
    "model":   {"challenger", "validation", "governance", "sr", "mrm"},
    "credit":  {"default", "ead", "pd", "lgd", "concentration", "borrower"},
    "counterparty": {"netting", "exposure", "cva", "derivative"},
    "cecl":    {"loss", "forecasting", "expected", "allowance"},
    "loss":    {"cecl", "lgd", "forecasting"},
}


def _tokens(text: str) -> set[str]:
    """Lowercase, split on '/' and whitespace, keep tokens > 2 chars."""
    return {t for t in text.lower().replace("/", " ").split() if len(t) > 2}


def topic_matches(expected: str, actual: str) -> bool:
    """
    Return True if the LLM's topic label matches the expected topic.

    Matching rules (any one is sufficient):
      1. Exact token overlap after normalization.
      2. Substring match: an expected token appears inside an actual token.
      3. Synonym expansion: an expected token maps to a token present in actual.
    """
    exp_tokens = _tokens(expected)
    act_tokens = _tokens(actual)

    # Rule 1: direct overlap
    if exp_tokens & act_tokens:
        return True

    # Rule 2: substring match (e.g., 'bank' in 'banking')
    for e in exp_tokens:
        for a in act_tokens:
            if e in a or a in e:
                return True

    # Rule 3: synonym expansion
    for e in exp_tokens:
        expanded = TOPIC_SYNONYMS.get(e, set())
        if expanded & act_tokens:
            return True

    return False

def quality_check(answer) -> dict:
    """
    Heuristic content-quality gates.

    Returns {'ok': bool, 'issues': list[str]}.
    These are NOT correctness checks — they catch obvious stubs,
    truncated outputs, and under-specified answers.
    """
    issues: list[str] = []

    # Definition should be substantive
    if len(answer.definition.split()) < 25:
        issues.append(f"definition too short ({len(answer.definition.split())} words)")

    # Why-it-matters should explain business/regulatory relevance
    if len(answer.why_it_matters.split()) < 15:
        issues.append("why_it_matters too short")

    # At least 4 key components
    if len(answer.key_components) < 4:
        issues.append(f"only {len(answer.key_components)} key components (want >=4)")

    # Example should be concrete, not one-liner
    if len(answer.financial_services_example.split()) < 20:
        issues.append("financial_services_example too short")

    # At least 3 risks/limitations
    if len(answer.risks_and_limitations) < 3:
        issues.append(f"only {len(answer.risks_and_limitations)} risks/limitations (want >=3)")

    # Practical application should be actionable
    if len(answer.practical_application.split()) < 15:
        issues.append("practical_application too short")

    # No empty list items
    for field in ("key_components", "risks_and_limitations"):
        items = getattr(answer, field)
        if any(not item.strip() for item in items):
            issues.append(f"empty item in {field}")

    return {"ok": not issues, "issues": issues}

def evaluate() -> None:
    questions = load_questions()
    results = []
    for item in questions:
        q = item["question"]
        expected = item["expected_topic"]
        try:
            answer = answer_question(q)
            match = topic_matches(expected, answer.topic)
            qc = quality_check(answer)
            results.append({
                "question": q,
                "expected_topic": expected,
                "actual_topic": answer.topic,
                "topic_match": match,
                "confidence": answer.confidence,
                "quality_ok": qc["ok"],
                "quality_issues": qc["issues"],
            })
            status = "PASS" if match else "FAIL"
            qc_flag = "OK" if qc["ok"] else "ISSUES"
            print(f"[{status}] {q} | expected={expected} | got={answer.topic} | conf={answer.confidence} | quality={qc_flag}")
            if qc["issues"]:
                for issue in qc["issues"]:
                    print(f"         - {issue}")
            
        except Exception as e:
            results.append({"question": q, "error": str(e)})
            print(f"[ERROR] {q} | {e}")

    passed = sum(1 for r in results if r.get("topic_match"))
    quality_passed = sum(1 for r in results if r.get("quality_ok"))
    print(f"\nTopic-match accuracy: {passed}/{len(questions)}")
    print(f"Content-quality pass: {quality_passed}/{len(questions)}")

    # Failures summary
    failed = [r for r in results if not r.get("topic_match")]
    if failed:
        print("\nTopic-match failures:")
        for r in failed:
            print(f"  - {r['question']} | expected={r['expected_topic']} | got={r.get('actual_topic')}")

    quality_failed = [r for r in results if not r.get("quality_ok")]
    if quality_failed:
        print("\nQuality-issue questions:")
        for r in quality_failed:
            print(f"  - {r['question']} | issues={r['quality_issues']}")

    out_path = Path(__file__).parent / "data" / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote results to {out_path}")


if __name__ == "__main__":
    evaluate()