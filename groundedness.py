"""
groundedness.py
Checks whether an LLM's answer is actually supported by the sources it was
given (the forecast summary + retrieved RBI chunks), instead of just
trusting the system prompt's "don't make things up" instruction to have
worked. A prompt asking a model to stay grounded is not a guarantee that
it did -- this module verifies it after the fact.

Two checks, combined into one report:

1. Numeric grounding -- every number mentioned in the answer should trace
   back to a number that appeared in the source material. Numbers are the
   easiest thing for an LLM to subtly invent (e.g. rounding 5.1% into a
   suspiciously precise "5.14%" that was never actually stated), and the
   easiest to verify mechanically.

2. Semantic groundedness -- how much the answer's wording actually
   overlaps with the source material, via TF-IDF cosine similarity
   (sklearn only, no embeddings needed). Low overlap suggests the model
   may be answering from its own general knowledge rather than the
   specific documents it was given.

Neither check is a perfect hallucination detector -- a model could
invent a plausible-sounding number that happens to already exist in the
source for an unrelated reason, or paraphrase so heavily that semantic
overlap looks lower than it should. Treat this as a useful signal to
flag for human review, not a guaranteed pass/fail.
"""

import re
from dataclasses import dataclass


@dataclass
class GroundednessReport:
    numbers_in_answer: list
    numbers_in_sources: list
    ungrounded_numbers: list
    numeric_grounding_ok: bool
    semantic_overlap_score: float
    semantic_grounding_ok: bool
    overall_flag: str  # "grounded", "review", "ungrounded"


def extract_numbers(text: str) -> list:
    """Pull out numeric values (including %, decimals, negatives) from text.
    e.g. "5.1%" -> 5.1, "-0.26" -> -0.26, "5.25 percent" -> 5.25
    Excludes numbers glued to letters (e.g. "FY27", "Q3") which aren't
    economic figures -- these are stripped out entirely first, since a
    lookbehind alone only blocks the match start and still lets trailing
    digits (e.g. the "7" in "FY27") leak through as a false number."""
    cleaned = re.sub(r"\b[A-Za-z]+\d+\b", "", text)
    matches = re.findall(r"-?\d+\.?\d*", cleaned)
    return [float(m) for m in matches if m not in ("", "-", ".")]


def check_numeric_grounding(answer: str, source_text: str, tolerance: float = 0.015) -> tuple:
    """Every number in the answer should appear (within a small tolerance,
    to allow for rounding/formatting differences like "5.10" vs "5.1") in
    the source text. Tolerance is intentionally tight -- 0.015 catches
    genuine float-formatting noise without letting a distinct real number
    (e.g. 4.75 vs 4.7, which differ by a meaningful 0.05 in a percentage
    context) slip through as if it matched."""
    answer_numbers = extract_numbers(answer)
    source_numbers = extract_numbers(source_text)

    ungrounded = []
    for num in answer_numbers:
        found = any(abs(num - src) <= tolerance for src in source_numbers)
        if not found:
            ungrounded.append(num)

    return answer_numbers, source_numbers, ungrounded


def semantic_overlap(answer: str, source_text: str) -> float:
    """TF-IDF cosine similarity between the answer and the source material.
    Returns 0.0-1.0; higher means the answer's wording draws more heavily
    on the actual source vocabulary rather than generic phrasing."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        vectors = vectorizer.fit_transform([answer, source_text])
    except ValueError:
        # happens if answer/source share zero vocabulary after stopword removal
        return 0.0
    return float(cosine_similarity(vectors[0], vectors[1])[0][0])


def check_groundedness(
    answer: str,
    source_text: str,
    numeric_tolerance: float = 0.015,
    semantic_threshold: float = 0.15,
) -> GroundednessReport:
    """Run both checks and combine into one report with an overall flag.

    semantic_threshold=0.15 is a deliberately loose default -- TF-IDF
    overlap is a coarse signal, and plain-language explanations naturally
    reword source material rather than echo it. This catches answers that
    are wildly off-topic, not ones that are merely well-paraphrased.
    """
    answer_nums, source_nums, ungrounded = check_numeric_grounding(answer, source_text, numeric_tolerance)
    numeric_ok = len(ungrounded) == 0

    overlap = semantic_overlap(answer, source_text)
    semantic_ok = overlap >= semantic_threshold

    if numeric_ok and semantic_ok:
        flag = "grounded"
    elif not numeric_ok:
        flag = "ungrounded"  # invented numbers is the more serious failure
    else:
        flag = "review"  # numbers check out, but wording seems disconnected from sources

    return GroundednessReport(
        numbers_in_answer=answer_nums,
        numbers_in_sources=source_nums,
        ungrounded_numbers=ungrounded,
        numeric_grounding_ok=numeric_ok,
        semantic_overlap_score=round(overlap, 4),
        semantic_grounding_ok=semantic_ok,
        overall_flag=flag,
    )


if __name__ == "__main__":
    source = (
        "The RBI raised its FY27 CPI inflation forecast to 5.1%, up from 4.6% "
        "in the April review. Core inflation was revised up to 4.7% from 4.4%. "
        "The repo rate was kept unchanged at 5.25%."
    )

    print("=" * 70)
    print("TEST 1: A well-grounded answer (numbers match the source)")
    print("=" * 70)
    good_answer = (
        "The RBI revised its inflation forecast up to 5.1% for FY27, from "
        "4.6% previously, while keeping the repo rate steady at 5.25%."
    )
    report = check_groundedness(good_answer, source)
    print(report)
    assert report.overall_flag == "grounded", "Expected this answer to pass"

    print("\n" + "=" * 70)
    print("TEST 2: An answer with an invented number (should be flagged)")
    print("=" * 70)
    bad_answer = (
        "The RBI revised its inflation forecast up to 6.8% for FY27, and "
        "cut the repo rate to 4.75% to support growth."
    )
    report = check_groundedness(bad_answer, source)
    print(report)
    assert report.overall_flag == "ungrounded", "Expected invented numbers to be caught"
    assert 6.8 in report.ungrounded_numbers
    assert 4.75 in report.ungrounded_numbers

    print("\n" + "=" * 70)
    print("TEST 3: An answer that's off-topic (numbers happen to match, wording doesn't)")
    print("=" * 70)
    offtopic_answer = (
        "Gold prices often rise about 5.1 percent during festival season, "
        "and interest in FDs at 5.25% remains steady among retirees."
    )
    report = check_groundedness(offtopic_answer, source)
    print(report)

    print("\nAll assertions passed -- groundedness checks are working correctly.")
