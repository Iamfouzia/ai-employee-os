"""
Phase 1: Intent Classification + Structured Extraction
--------------------------------------------------------
Step 1 -> Zero-shot classification (local, CPU-friendly) decides WHICH
          AI Employee category the command belongs to.
Step 2 -> An instruction-following model (via HF Inference API) extracts
          structured details (customer, date, time, quantity, action).

Result -> validated into the ParsedIntent Pydantic model.
"""

import os
import json
import re
from transformers import pipeline, AutoTokenizer
from dotenv import load_dotenv

from app.nlu.schemas import ParsedIntent, IntentCategory

load_dotenv()

EXTRACTION_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"  # small enough for CPU; swap for a bigger model if you have GPU

# ---- Step 1: Zero-shot classifier (loads once, runs locally on CPU) ----
_zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

CATEGORIES = [c.value for c in IntentCategory]

# ---- Step 2: Local instruction model for structured extraction ----
# Runs fully on your machine - no remote Inference Provider, so no more
# "model not supported by provider X" errors.
_extractor = pipeline("text-generation", model=EXTRACTION_MODEL, device_map="auto")
_tokenizer = AutoTokenizer.from_pretrained(EXTRACTION_MODEL)
# the model's default generation_config sets temperature/top_p/top_k, which only
# apply when do_sample=True; since we always use greedy decoding (do_sample=False),
# clear them here to silence the harmless "generation flags not valid" warning.
_extractor.model.generation_config.temperature = None
_extractor.model.generation_config.top_p = None
_extractor.model.generation_config.top_k = None

EXTRACTION_SYSTEM_PROMPT = """You are an information extraction engine. Extract structured
fields from the business command given by the user. Return ONLY valid JSON, no explanation,
no markdown formatting. Use null for any field that is not mentioned.

Fields: action (short verb phrase, e.g. "schedule_meeting", "send_quotation"),
customer_name, date, time, quantity (integer or null)."""


def classify_category(text: str) -> tuple[str, float]:
    """Step 1: which AI Employee category does this command belong to."""
    result = _zero_shot(text, CATEGORIES)
    top_label = result["labels"][0]
    top_score = result["scores"][0]
    return top_label, top_score


def extract_details(text: str) -> dict:
    """Step 2: pull structured fields out of the raw command using a local LLM."""
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f'Command: "{text}"\n\nJSON:'},
    ]
    prompt = _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    output = _extractor(prompt, max_new_tokens=200, do_sample=False,
                         pad_token_id=_tokenizer.eos_token_id)
    generated = output[0]["generated_text"][len(prompt):]

    # Models sometimes wrap JSON in extra text/markdown - pull out the {...} block
    match = re.search(r"\{.*\}", generated, re.DOTALL)
    if not match:
        return {"action": None, "customer_name": None, "date": None,
                "time": None, "quantity": None}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"action": None, "customer_name": None, "date": None,
                "time": None, "quantity": None}


def parse_command(text: str) -> ParsedIntent:
    """Full Phase 1 pipeline: raw text -> validated ParsedIntent object."""
    category, confidence = classify_category(text)
    details = extract_details(text)

    return ParsedIntent(
        category=category,
        action=details.get("action") or "unknown",
        customer_name=details.get("customer_name"),
        date=details.get("date"),
        time=details.get("time"),
        quantity=details.get("quantity"),
        raw_input=text,
        confidence=round(confidence, 3),
    )


if __name__ == "__main__":
    # quick manual check
    sample = "Schedule a meeting with John Friday at 3 PM"
    intent = parse_command(sample)
    print(intent.model_dump_json(indent=2))