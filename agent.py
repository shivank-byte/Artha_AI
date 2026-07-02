"""
agent.py
Ties together the forecasting engine (forecasting.py) and the RAG
knowledge base (rag.py) so an LLM can explain a forecast in plain
language, grounded in retrieved RBI policy context.

This file requires an LLM API key and cannot be run in this sandbox
(no internet, no credentials). It's written against Google's Gemini API
since it has a genuinely free tier (1,500 requests/day, no card) --
swap the `call_llm` function for Groq/Anthropic/OpenAI if you prefer;
only that one function needs to change.

DESIGN: no LangChain framework dependency here on purpose. The actual
"agentic" pattern -- run forecast, retrieve context, build a grounded
prompt, call the LLM -- is simple enough to write directly and is
easier to debug this way. Swap in LangChain/LangGraph later once this
manual version works reliably (this mirrors the "learn plain LangChain
before LangGraph" advice from your learning checklist -- here we're
starting even before that, with the plainest possible version).
"""

import os
from data_loader import load_cpi_series, add_pct_change, chronological_split
from forecasting import linear_ar_benchmark
from evaluation import evaluate_all
from rag import build_chunk_index, retrieve as rag_retrieve
from groundedness import check_groundedness


GUARDRAIL_SYSTEM_PROMPT = """You are an economic assistant explaining an India CPI \
inflation forecast to a general audience.

STRICT RULES:
1. Only use numbers given to you in the FORECAST DATA section below. Never invent, \
estimate, or round numbers you were not given.
2. Only make claims about RBI policy that are supported by the RETRIEVED CONTEXT \
section below. If the context doesn't address something, say so explicitly rather \
than guessing.
3. Distinguish clearly between the model's statistical forecast (a projection from \
past patterns) and RBI's own official forecast (a judgment call by policymakers) -- \
never blend them into a single number.
4. If the retrieved context and the model forecast seem to disagree, point that out \
explicitly rather than picking one silently.
5. Keep the explanation to 3-4 sentences. No financial advice, no predictions phrased \
as certainties -- inflation forecasts are estimates, not facts.
"""


def build_grounded_prompt(forecast_summary: str, retrieved_chunks: list, user_question: str) -> str:
    """Assemble the final prompt sent to the LLM, with forecast data and
    retrieved RBI context clearly separated so the model can't blend them."""
    context_block = "\n\n".join(
        f"[Source: {chunk.source}]\n{chunk.text}" for chunk, _score in retrieved_chunks
    )
    return f"""FORECAST DATA:
{forecast_summary}

RETRIEVED CONTEXT (RBI policy documents):
{context_block}

USER QUESTION:
{user_question}

Answer the user's question using only the FORECAST DATA and RETRIEVED CONTEXT above."""


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Calls Google's Gemini API (free tier). Looks for the key in
    Streamlit Cloud secrets first (st.secrets), then falls back to a
    plain environment variable for local/terminal use."""
    import google.generativeai as genai

    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Get a free key at https://aistudio.google.com/apikey "
            "and add it as a Streamlit Cloud Secret (App settings -> Secrets), or set it as "
            "an environment variable for local runs."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
    response = model.generate_content(user_prompt)
    return response.text


def run_advisor(user_question: str):
    """The full pipeline: forecast -> retrieve -> ground -> explain -> verify.
    Returns (answer: str, groundedness_report: GroundednessReport, retrieval_mode: str)."""
    # Step 1: run the forecast (this part IS tested, real, working)
    df = add_pct_change(load_cpi_series())
    series = df["cpi_pct_change"].dropna()
    train, test = chronological_split(series.to_frame("v"), test_months=12)
    train, test = train["v"], test["v"]
    preds, actual, _ = linear_ar_benchmark(train, test)
    metrics = evaluate_all(actual, preds)

    forecast_summary = (
        f"Model: Linear AR benchmark. Forecast vs. actual month-over-month CPI % change "
        f"for the last 12 months. Accuracy: MAE={metrics['MAE']}, RMSE={metrics['RMSE']}. "
        f"Most recent actual month-over-month change: {actual[-1]:+.3f}%. "
        f"Model's forecast for that same month: {preds[-1]:+.3f}%."
    )

    # Step 2: retrieve relevant RBI policy context (this part IS tested, real, working)
    chunks = build_chunk_index()
    retrieved, retrieval_mode = rag_retrieve(user_question, chunks, top_k=3)

    # Step 3: build the grounded prompt (pure string logic, tested implicitly above)
    prompt = build_grounded_prompt(forecast_summary, retrieved, user_question)

    # Step 4: call the LLM (NOT tested here -- needs a real API key)
    answer = call_llm(GUARDRAIL_SYSTEM_PROMPT, prompt)

    # Step 5: verify the answer actually stayed grounded in the sources it
    # was given -- the system prompt ASKS for this, this step CHECKS it.
    all_source_text = forecast_summary + "\n" + "\n".join(c.text for c, _ in retrieved)
    report = check_groundedness(answer, all_source_text)

    return answer, report, retrieval_mode


def run_advisor_debug(user_question: str):
    """Same as run_advisor but stops before the LLM call and returns the
    assembled prompt instead -- lets you verify forecast + retrieval +
    prompt assembly all worked, without needing an API key."""
    df = add_pct_change(load_cpi_series())
    series = df["cpi_pct_change"].dropna()
    train, test = chronological_split(series.to_frame("v"), test_months=12)
    train, test = train["v"], test["v"]
    preds, actual, _ = linear_ar_benchmark(train, test)
    metrics = evaluate_all(actual, preds)

    forecast_summary = (
        f"Model: Linear AR benchmark. Forecast vs. actual month-over-month CPI % change "
        f"for the last 12 months. Accuracy: MAE={metrics['MAE']}, RMSE={metrics['RMSE']}. "
        f"Most recent actual month-over-month change: {actual[-1]:+.3f}%. "
        f"Model's forecast for that same month: {preds[-1]:+.3f}%."
    )
    chunks = build_chunk_index()
    retrieved, retrieval_mode = rag_retrieve(user_question, chunks, top_k=3)
    prompt = build_grounded_prompt(forecast_summary, retrieved, user_question)
    return prompt


if __name__ == "__main__":
    question = "Why might inflation be rising, and what is the RBI's official forecast?"

    print("=" * 70)
    print("TESTED PORTION: forecast + retrieval + prompt assembly")
    print("=" * 70)
    prompt = run_advisor_debug(question)
    print(prompt)

    print("\n" + "=" * 70)
    print("UNTESTED PORTION: the actual LLM call + groundedness check")
    print("=" * 70)
    try:
        answer, report, retrieval_mode = run_advisor(question)
        print(f"(retrieval mode used: {retrieval_mode})")
        print("ANSWER:", answer)
        print("\nGROUNDEDNESS REPORT:", report)
    except (RuntimeError, ModuleNotFoundError, ImportError) as e:
        print(f"Could not call LLM: {e}")
        print("\nExpected in this sandbox (no internet, no API key). "
              "Everything above the LLM call is real, working code, confirmed "
              "on your real data. Install google-generativeai and set "
              "GEMINI_API_KEY to run this part on your machine.")
    
