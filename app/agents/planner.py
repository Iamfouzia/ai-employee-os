"""
Phase 2: Multi-Step Task Planner
----------------------------------
Takes a raw command that may contain SEVERAL actions chained together, e.g.

    "Send a quotation to John for 25 laptops, schedule a meeting Friday at
    3 PM, and remind me if he doesn't reply within three days"

...and breaks it into an ordered TaskPlan (list of TaskStep) that the
Executive Assistant graph can execute one by one.

Reuses the same local instruction model from Phase 1 (app/nlu/intent_classifier.py)
so you don't need a second model download.
"""

import json
import re
import difflib
from app.nlu.intent_classifier import _extractor, _tokenizer, classify_category
from app.nlu.schemas import TaskPlan, TaskStep, IntentCategory

# Deterministic action -> category mapping. This is checked FIRST because it's far
# more reliable than semantic zero-shot classification on short phrases like
# "send quotation" - zero-shot only kicks in for actions not listed here.
ACTION_CATEGORY_MAP: dict[str, IntentCategory] = {
    # CEO Assistant
    "approve_request": IntentCategory.CEO,
    "review_report": IntentCategory.CEO,
    "escalate_issue": IntentCategory.CEO,
    # Sales Manager
    "send_quotation": IntentCategory.SALES,
    "follow_up": IntentCategory.SALES,
    "send_reminder": IntentCategory.SALES,
    "close_deal": IntentCategory.SALES,
    "schedule_meeting": IntentCategory.SALES,  # generic meetings default to Sales
    # Customer Support Agent
    "respond_to_ticket": IntentCategory.SUPPORT,
    "resolve_complaint": IntentCategory.SUPPORT,
    "escalate_ticket": IntentCategory.SUPPORT,
    # HR Assistant
    "onboard_employee": IntentCategory.HR,
    "update_policy": IntentCategory.HR,
    "manage_leave_request": IntentCategory.HR,
    # Recruiter
    "post_job": IntentCategory.RECRUITMENT,
    "schedule_interview": IntentCategory.RECRUITMENT,
    "send_offer_letter": IntentCategory.RECRUITMENT,
    # Finance Assistant
    "generate_invoice": IntentCategory.FINANCE,
    "process_payment": IntentCategory.FINANCE,
    "track_expense": IntentCategory.FINANCE,
    # Accountant
    "reconcile_accounts": IntentCategory.ACCOUNTING,
    "generate_report": IntentCategory.ACCOUNTING,
    "file_tax": IntentCategory.ACCOUNTING,
    # Marketing Assistant
    "launch_campaign": IntentCategory.MARKETING,
    "post_social_update": IntentCategory.MARKETING,
    "analyze_campaign": IntentCategory.MARKETING,
    # Content Writer
    "write_blog_post": IntentCategory.CONTENT,
    "write_product_description": IntentCategory.CONTENT,
    "write_ad_copy": IntentCategory.CONTENT,
    # Legal Assistant
    "review_contract": IntentCategory.LEGAL,
    "draft_agreement": IntentCategory.LEGAL,
    "check_compliance": IntentCategory.LEGAL,
    # Inventory Manager
    "update_stock": IntentCategory.INVENTORY,
    "check_inventory": IntentCategory.INVENTORY,
    "reorder_stock": IntentCategory.INVENTORY,
    # Procurement Assistant
    "create_purchase_order": IntentCategory.PROCUREMENT,
    "negotiate_vendor": IntentCategory.PROCUREMENT,
    "track_delivery": IntentCategory.PROCUREMENT,
}


# Common paraphrases the local model tends to produce, checked BEFORE fuzzy
# matching (difflib can pick the wrong close match for short, similar action names).
ACTION_ALIASES: dict[str, str] = {
    "onboard_new_employee": "onboard_employee",
    "post_job_opening": "post_job",
    "create_campaign": "launch_campaign",
    "start_campaign": "launch_campaign",
    "review_performance_report": "review_report",
    "reorder_laptops": "reorder_stock",
    "send_invoice": "generate_invoice",
    "create_invoice": "generate_invoice",
}


def normalize_action(action: str) -> str:
    """Snap a possibly-paraphrased action name (e.g. 'onboard_new_employee' from the
    LLM) to the closest canonical action in ACTION_CATEGORY_MAP. Small local models
    don't always reproduce the exact vocabulary given in the prompt, so this is a
    safety net rather than relying on the prompt alone."""
    if action in ACTION_CATEGORY_MAP:
        return action
    if action in ACTION_ALIASES:
        return ACTION_ALIASES[action]
    matches = difflib.get_close_matches(action, ACTION_CATEGORY_MAP.keys(), n=1, cutoff=0.5)
    return matches[0] if matches else action


def resolve_category(action: str, customer_name: str | None) -> IntentCategory:
    """Map an action to its AI Employee category - rule-based first, zero-shot fallback."""
    mapped = ACTION_CATEGORY_MAP.get(action)
    if mapped is not None:
        return mapped

    action_text = action.replace("_", " ")
    step_context = f"{action_text} for {customer_name or 'a customer'}"
    category, _ = classify_category(step_context)
    return category

ALLOWED_ACTIONS = sorted(ACTION_CATEGORY_MAP.keys())

PLANNER_SYSTEM_PROMPT = f"""You are a task planning engine for a business AI assistant.
Break the user's command into an ordered list of steps. Each step is one atomic action.

You MUST choose each step's "action" ONLY from this exact list (use the exact spelling,
do not invent new action names):
{", ".join(ALLOWED_ACTIONS)}

Return ONLY a valid JSON array, no explanation, no markdown. Each item must have:
- step_id (integer, starting at 1)
- action (MUST be one of the allowed actions listed above)
- customer_name, date, time, quantity (use null if not mentioned)
- depends_on (step_id of a step this step must wait for - use null unless the command
  EXPLICITLY says this step only happens after/depends on another, e.g. "remind me IF
  he doesn't reply". Do NOT set this just because steps appear in the same sentence.)
- condition (the natural-language condition, only when depends_on is set; otherwise null)

Example output:
[
  {{"step_id": 1, "action": "send_quotation", "customer_name": "John", "date": null, "time": null, "quantity": 25, "depends_on": null, "condition": null}},
  {{"step_id": 2, "action": "schedule_meeting", "customer_name": "John", "date": "Friday", "time": "3 PM", "quantity": null, "depends_on": null, "condition": null}},
  {{"step_id": 3, "action": "send_reminder", "customer_name": "John", "date": null, "time": null, "quantity": null, "depends_on": 1, "condition": "if he doesn't reply within three days"}}
]"""


def _estimate_max_steps(text: str) -> int:
    """Rough upper bound on how many distinct actions a command should produce,
    based on conjunctions/commas. Used to catch the small model hallucinating
    extra unrelated steps beyond what the command actually asked for."""
    # count " and " plus commas as separators between clauses
    separators = text.lower().count(" and ") + text.count(",")
    return max(1, separators + 1) + 1  # +1 slack for borderline phrasing


def _step_is_grounded(step_dict: dict, raw_text: str) -> bool:
    """Reject steps whose ACTION doesn't relate to anything in the actual command -
    a cheap guard against the model hallucinating unrelated actions (e.g. inserting
    a 'manage_leave_request' step into a purchase-order command). Deliberately does
    NOT check customer_name: generic actions (e.g. 'launch a campaign', 'review this
    month's report') often have no real named entity, and the model filling in a
    filler/generic name there shouldn't disqualify an otherwise-correct step."""
    text_lower = raw_text.lower()

    action_words = [w for w in (step_dict.get("action") or "").split("_") if len(w) > 3]
    if action_words and not any(w in text_lower for w in action_words):
        return False  # action's core verb/noun isn't grounded in the command text

    return True


def _run_local_model(system_prompt: str, user_prompt: str, max_new_tokens: int = 400) -> str:
    """Shared helper: same local pipeline used in Phase 1, different prompt."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    prompt = _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output = _extractor(prompt, max_new_tokens=max_new_tokens, do_sample=False,
                         pad_token_id=_tokenizer.eos_token_id)
    return output[0]["generated_text"][len(prompt):]


def _parse_steps_json(generated: str) -> list[dict]:
    """Parse the model's JSON array output, repairing truncated output if the
    model ran out of tokens mid-array (common with small models on long prompts) -
    trims back to the last complete {...} object and closes the array there."""
    match = re.search(r"\[.*", generated, re.DOTALL)
    if not match:
        return []
    raw = match.group(0)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # repair attempt: cut back to the last complete object and close the array
    last_close = raw.rfind("}")
    if last_close == -1:
        return []
    repaired = raw[:last_close + 1] + "]"
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        return []


QUESTION_STARTERS = ("what", "how", "when", "where", "why", "who", "is", "are",
                     "can", "does", "do", "will", "should")


def is_knowledge_question(text: str) -> bool:
    """Fast-path detector: is this a company-knowledge question rather than an
    action command? Simple heuristic (question mark or question-word start) -
    far more reliable than asking the small planner model to pick 'answer_question'
    out of 38 possible actions."""
    stripped = text.strip().lower()
    return stripped.endswith("?") or stripped.startswith(QUESTION_STARTERS)


def build_task_plan(text: str) -> TaskPlan:
    """Break a raw command into an ordered TaskPlan."""
    if is_knowledge_question(text):
        # skip the LLM planner entirely - single-step plan straight to the knowledge base
        step = TaskStep(step_id=1, category=IntentCategory.GENERAL, action="answer_question",
                         question_text=text)
        return TaskPlan(raw_input=text, steps=[step])

    generated = _run_local_model(PLANNER_SYSTEM_PROMPT, f'Command: "{text}"\n\nJSON:',
                                  max_new_tokens=600)

    steps_raw = _parse_steps_json(generated)

    # Guard against the model hallucinating extra/unrelated steps: drop anything
    # not grounded in the actual command text, then cap to a sane step count.
    steps_raw = [s for s in steps_raw if _step_is_grounded(s, text)]
    steps_raw = steps_raw[:_estimate_max_steps(text)]

    # Renumber step_ids after filtering, and drop depends_on/condition for any
    # step that pointed at something we just removed.
    old_to_new_id = {s.get("step_id"): i + 1 for i, s in enumerate(steps_raw)}
    for i, s in enumerate(steps_raw):
        s["step_id"] = i + 1
        if s.get("depends_on") not in old_to_new_id:
            s["depends_on"] = None
            s["condition"] = None
        else:
            s["depends_on"] = old_to_new_id[s["depends_on"]]

    steps = []
    for raw in steps_raw:
        action = normalize_action(raw.get("action") or "unknown")
        category = resolve_category(action, raw.get("customer_name"))
        steps.append(TaskStep(
            step_id=raw.get("step_id"),
            category=category,
            action=action,
            customer_name=raw.get("customer_name"),
            date=raw.get("date"),
            time=raw.get("time"),
            quantity=raw.get("quantity"),
            depends_on=raw.get("depends_on"),
            condition=raw.get("condition"),
        ))

    return TaskPlan(raw_input=text, steps=steps)


if __name__ == "__main__":
    sample = ("Send a quotation to John for 25 laptops, schedule a meeting "
              "Friday at 3 PM, and remind me if he doesn't reply within three days")
    plan = build_task_plan(sample)
    print(plan.model_dump_json(indent=2))