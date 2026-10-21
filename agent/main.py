import json
from seed_db import seed
from orchestrator import run_investigation


if __name__ == "__main__":
    seed()

    cases = [
        {"account_id": "acc_001", "txn_id": "t4", "merchant": "QuickGoldExchange", "amount": 1980.00},
        {"account_id": "acc_002", "txn_id": "t7", "merchant": "Carrefour", "amount": 310.00},
    ]

    for case in cases:
        print(f"\n{'='*60}\nInvestigating {case['txn_id']} ({case['account_id']})\n{'='*60}")
        result = run_investigation(**case)
        print("\nFinal verdict:")
        print(json.dumps(result["verdict"], indent=2))
