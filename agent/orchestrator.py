"""
Thin dispatcher. This is the one place that knows there's more than
one provider -- everything else (tools.py, main.py, eval.py) just calls
run_investigation() without caring which model answers.

Set MODEL_PROVIDER to one of: anthropic (default), gemini, baseline.
"baseline" is a rule-based scorer with no LLM -- free, offline, and the
number your LLM agents need to beat.
"""
import os
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env; anything already set in your shell still wins


def run_investigation(account_id: str, txn_id: str, merchant: str, amount: float, verbose: bool = True) -> dict:
    provider = os.environ.get("MODEL_PROVIDER", "anthropic").lower()

    if provider == "anthropic":
        from adapters.anthropic_adapter import run_investigation as run
    elif provider == "gemini":
        from adapters.gemini_adapter import run_investigation as run
    elif provider == "baseline":
        from adapters.baseline_adapter import run_investigation as run
    else:
        raise ValueError(
            f"Unknown MODEL_PROVIDER: {provider!r} (expected 'anthropic', 'gemini', or 'baseline')"
        )

    return run(account_id, txn_id, merchant, amount, verbose=verbose)
