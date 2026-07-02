"""
example_usage.py -- Demonstrates the RefundPolicyClient SDK.
"""
from client import RefundPolicyClient
import random

def generate_sample_refunds(n=150, seed=42):
    random.seed(seed)
    reasons = [
        "Item arrived damaged", "Wrong size, too big", "Changed my mind",
        "Not as described - poor quality", "Wrong item sent", "Package never arrived",
        "Size does not fit as expected", "I do not need this anymore",
        "Defective product, not working", "Late delivery - no longer needed",
    ]
    records = []
    for _ in range(n):
        records.append({
            "amount": round(random.uniform(15, 250), 2),
            "reason": random.choice(reasons),
            "days_since_purchase": random.randint(1, 60),
            "approved": random.random() > 0.15,
        })
    return records

def main():
    client = RefundPolicyClient()
    records = generate_sample_refunds()

    current_policy = {
        "return_window_days": 21,
        "restocking_fee_pct": 15,
        "free_returns": False,
        "exchange_allowed": True,
    }

    # Maximize retention
    print("[1] Policy Optimization -- Maximize Retention")
    result = client.optimize(records, current_policy, business_goal="maximize_retention")
    a = result["analysis"]
    print(f"Refunds Analyzed: {a['total_refunds']} | Approval Rate: {a['approval_rate']*100:.1f}%")
    print(f"Avg Amount: ${a['avg_amount']:.2f} | Preventable: {a['preventable_pct']}%")
    print(f"Top Reasons: {[r['reason'] for r in a['top_reasons'][:3]]}")
    print(f"Current Policy Score: {result['policy_score']}/100")
    print(f"Optimized Policy: {result['optimized_policy']}")
    print(f"Estimated Impact: {result['estimated_impact']}")

    # Minimize costs
    print("\n[2] Policy Optimization -- Minimize Costs")
    result2 = client.optimize(records, current_policy, business_goal="minimize_costs")
    print(f"Policy Score: {result2['policy_score']}/100")
    print(f"Recommendations:")
    for rec in result2["optimized_policy"].get("recommendations", [])[:3]:
        print(f"  - {rec}")

if __name__ == "__main__":
    main()
