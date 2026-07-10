# genpark-refund-policy-optimizer-skill

> **GenPark AI Agent Skill** — Analyze refund patterns and optimize e-commerce refund policies for retention, cost, or balance.

## Features

- Refund pattern analysis: top reasons, approval rates, preventable returns
- Policy customer-friendliness scoring (0-100)
- Three optimization goals: `maximize_retention`, `minimize_costs`, `balanced`
- Projected impact on retention, conversion, and costs
- Actionable recommendations

## Quick Start

```python
from client import RefundPolicyClient

client = RefundPolicyClient()
result = client.optimize(
    refund_records=[{"amount": 45.0, "reason": "wrong size", "days_since_purchase": 12, "approved": True}],
    current_policy={"return_window_days": 21, "restocking_fee_pct": 15, "free_returns": False},
    business_goal="balanced",
)
print(f"Policy Score: {result['policy_score']}/100")
print(result["optimized_policy"])
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
