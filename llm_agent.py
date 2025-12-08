
import os
import textwrap
import pandas as pd

from openai import OpenAI
from retrieval import retrieve_chunks


# ----------------------------------------------------
# REAL LLM CLIENT
# ----------------------------------------------------
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(prompt: str) -> str:
    """
    Real LLM API call using OpenAI models.
    Uses gpt-4.1-mini for low latency + low hallucination risk.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Environment variable OPENAI_API_KEY is not set.\n"
            "Set it before running the notebook."
        )

    try:
        response = _client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM CALL FAILED: {type(e).__name__}: {e}\n\n--- PROMPT PREVIEW ---\n\n{prompt}"


# ----------------------------------------------------
# CONTEXT BUILDING
# ----------------------------------------------------
def build_context_string(chunks_df: pd.DataFrame) -> str:
    """
    Convert retrieved chunk rows into a formatted string
    that will be inserted into the prompt.
    """
    blocks = []

    for _, row in chunks_df.iterrows():
        header = (
            f"[chunk_id={row['chunk_id']}, "
            f"source={row['source']}, "
            f"doc_type={row['doc_type']}, "
            f"year={row['year']}]"
        )

        text = str(row["text"])
        blocks.append(header + "\n" + text)

    return "\n\n".join(blocks)


# ----------------------------------------------------
# PROMPT BUILDER
# ----------------------------------------------------
def build_prompt(question: str, chunks_df: pd.DataFrame) -> str:
    """
    Produce the final strict RAG prompt.
    """
    context = build_context_string(chunks_df)

    template = f"""
    You are a financial and ESG analyst answering questions about EssilorLuxottica.

    Use ONLY the information provided in the text chunks below.
    If the answer does not appear in the chunks, respond exactly:
    "Based on the provided documents, this information is not available."

    Rules:
    1. Cite chunk_ids like this: [chunk_id=5].
    2. Do NOT introduce information that is not in the chunks.
    3. Keep the answer to 3–5 sentences.
    4. If chunks conflict, choose the one with the most recent year.

    User question:
    {question}

    Retrieved chunks:
    {context}

    Now provide:
    1. A direct answer (3–5 sentences).
    2. A short note on missing or uncertain information.
    3. A list of chunk_ids used.
    """

    return textwrap.dedent(template).strip()


# ----------------------------------------------------
# MAIN ENTRYPOINT FOR RAG Q&A
# ----------------------------------------------------
def answer_question(
    question: str,
    k: int = 6,
    allowed_doc_types: list[str] | None = None,
) -> dict:
    """
    Pipeline:
    1. Retrieve relevant chunks (TF-IDF)
    2. Build the prompt
    3. Call the LLM
    4. Return everything
    """
    # Get relevant chunks
    chunks = retrieve_chunks(
        question,
        k=k,
        allowed_doc_types=allowed_doc_types,
    )

    # Build RAG prompt
    prompt = build_prompt(question, chunks)

    # LLM call
    answer = call_llm(prompt)

    # Return structured output
    return {
        "answer": answer,
        "chunks": chunks,
        "prompt_used": prompt,
    }
