"""
Run this after setting HF_TOKEN in your .env file:
    python tests/test_phase1.py

Tries several sample commands and prints the parsed structured output
so you can visually check accuracy before wiring into FastAPI.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.nlu.intent_classifier import parse_command

SAMPLE_COMMANDS = [
    "Send a quotation to John for 25 laptops",
    "Schedule a meeting with the sales team Friday at 3 PM",
    "Onboard a new employee named Sara starting Monday",
    "Generate this month's revenue report",
    "Follow up with a customer who hasn't paid the invoice",
    "Write a product description for our new laptop",
]

if __name__ == "__main__":
    for cmd in SAMPLE_COMMANDS:
        print(f"\nInput: {cmd}")
        result = parse_command(cmd)
        print(result.model_dump_json(indent=2))