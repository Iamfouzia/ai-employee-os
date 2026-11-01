"""
Phase 5b: AI Routing Layer
------------------------------
Decides WHICH model handles a given generation request:

- Simple / high-volume tasks (single-step actions, short questions) -> local
  Qwen model (free, fast, already loaded - no API cost).
- Complex tasks (legal review, multi-clause contracts, financial analysis,
  long knowledge questions) -> a stronger hosted model (Claude/GPT/Gemini),
  IF a key is configured.

If no key is configured for the chosen remote provider, this automatically
falls back to the local model instead of crashing - so the whole project
keeps working even with zero API keys set up (as it has through Phases 1-7).

This directly covers the PDF's "AI Integration" requirement: OpenAI GPT,
Claude, Gemini, Prompt Engineering, AI Routing.
"""

from app.core.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY
from app.nlu.intent_classifier import _extractor, _tokenizer
from app.nlu.schemas import IntentCategory

# Categories whose work tends to be higher-stakes / needs stronger reasoning -
# these prefer a hosted model when available (contracts, financial figures,
# compliance wording benefit from a larger model's judgment).
COMPLEX_CATEGORIES = {IntentCategory.LEGAL, IntentCategory.ACCOUNTING, IntentCategory.CEO}

LONG_PROMPT_THRESHOLD = 600  # characters - long questions/context lean "complex"


def classify_complexity(text: str, category: IntentCategory | None = None) -> str:
    """Return 'simple' or 'complex' for a given request."""
    if category in COMPLEX_CATEGORIES:
        return "complex"
    if len(text) > LONG_PROMPT_THRESHOLD:
        return "complex"
    return "simple"


def _call_local(system_prompt: str, user_prompt: str, max_new_tokens: int = 300) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    prompt = _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output = _extractor(prompt, max_new_tokens=max_new_tokens, do_sample=False,
                         pad_token_id=_tokenizer.eos_token_id)
    return output[0]["generated_text"][len(prompt):].strip()


def _call_openai(system_prompt: str, user_prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text.strip()


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
    response = model.generate_content(user_prompt)
    return response.text.strip()


# provider name -> (call function, key required)
PROVIDER_CALLS = {
    "openai": (_call_openai, OPENAI_API_KEY),
    "anthropic": (_call_anthropic, ANTHROPIC_API_KEY),
    "gemini": (_call_gemini, GEMINI_API_KEY),
}

# preference order for "complex" tasks - first one with a key configured wins
COMPLEX_PROVIDER_PREFERENCE = ["anthropic", "openai", "gemini"]


def route_and_generate(system_prompt: str, user_prompt: str,
                        text_for_complexity: str, category: IntentCategory | None = None) -> dict:
    """Main entry point: classify complexity, pick a provider, generate, and
    report back which provider actually handled it (for logging/debugging)."""
    complexity = classify_complexity(text_for_complexity, category)

    if complexity == "complex":
        for provider_name in COMPLEX_PROVIDER_PREFERENCE:
            call_fn, key = PROVIDER_CALLS[provider_name]
            if key:  # only try providers that actually have a key configured
                try:
                    result = call_fn(system_prompt, user_prompt)
                    return {"text": result, "provider": provider_name, "complexity": complexity}
                except Exception as e:
                    # provider call failed (bad key, rate limit, network) - try the next one
                    print(f"[llm_router] {provider_name} call failed ({e}), trying next provider")
                    continue

    # simple task, OR no remote provider available/succeeded -> local model
    result = _call_local(system_prompt, user_prompt)
    return {"text": result, "provider": "local", "complexity": complexity}


if __name__ == "__main__":
    from app.core.config import available_providers
    print("Available providers:", available_providers())

    simple = route_and_generate(
        "You are a helpful assistant.", "Summarize: quotation sent to John.",
        text_for_complexity="Summarize: quotation sent to John.",
    )
    print(f"\n[simple task] routed to: {simple['provider']}\n-> {simple['text']}")

    complex_case = route_and_generate(
        "You are a legal assistant.", "What should I check before signing a vendor contract?",
        text_for_complexity="What should I check before signing a vendor contract?",
        category=IntentCategory.LEGAL,
    )
    print(f"\n[complex/legal task] routed to: {complex_case['provider']}\n-> {complex_case['text']}")