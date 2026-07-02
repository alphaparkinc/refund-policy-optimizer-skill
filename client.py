"""
refund-policy-optimizer-skill: Client SDK
Analyze refund patterns and optimize e-commerce refund policies.
"""

from __future__ import annotations
from typing import Literal, Optional
from collections import Counter

Goal = Literal["maximize_retention", "minimize_costs", "balanced"]

INDUSTRY_BENCHMARKS = {
    "return_window_days": 30,
    "approval_rate": 0.85,
    "refund_rate": 0.05,
    "avg_processing_days": 5,
}

REASON_CATEGORIES = {
    "defective": ["defective", "broken", "damaged", "not working", "faulty"],
    "wrong_item": ["wrong", "incorrect", "different", "not what"],
    "size_fit": ["size", "fit", "too big", "too small", "measurements"],
    "changed_mind": ["changed mind", "no longer", "dont want", "do not want", "not needed"],
    "late_delivery": ["late", "delayed", "never arrived", "missing"],
    "quality": ["quality", "cheap", "poor", "material", "feels"],
}


class RefundPolicyClient:
    """
    SDK for analyzing refund patterns and optimizing refund policies.

    Analyzes refund records to surface top reasons, approval rates,
    financial impact, and generates tailored policy recommendations.
    """

    def optimize(
        self,
        refund_records: list[dict],
        current_policy: Optional[dict] = None,
        business_goal: Goal = "balanced",
    ) -> dict:
        """
        Analyze refunds and generate policy optimization recommendations.

        Args:
            refund_records: List of dicts with:
                - amount (float)
                - reason (str)
                - days_since_purchase (int)
                - approved (bool)
            current_policy: Dict with:
                - return_window_days (int, default 30)
                - restocking_fee_pct (float, default 0)
                - free_returns (bool, default True)
                - exchange_allowed (bool, default True)
            business_goal: Optimization target.

        Returns:
            dict with analysis, policy_score, optimized_policy, estimated_impact
        """
        policy = {
            "return_window_days": 30,
            "restocking_fee_pct": 0,
            "free_returns": True,
            "exchange_allowed": True,
            **(current_policy or {})
        }

        analysis = self._analyze_records(refund_records)
        policy_score = self._score_policy(policy, analysis)
        optimized = self._optimize_policy(policy, analysis, business_goal)
        impact = self._estimate_impact(policy, optimized, analysis, business_goal)

        return {
            "analysis": analysis,
            "policy_score": policy_score,
            "current_policy": policy,
            "optimized_policy": optimized,
            "estimated_impact": impact,
            "business_goal": business_goal,
        }

    def _analyze_records(self, records: list[dict]) -> dict:
        if not records:
            return {"total_refunds": 0, "approval_rate": 0, "avg_amount": 0, "top_reasons": [], "late_returns_pct": 0}

        total = len(records)
        approved = [r for r in records if r.get("approved", True)]
        amounts = [float(r.get("amount", 0)) for r in records]
        days = [int(r.get("days_since_purchase", 0)) for r in records]

        # Categorize reasons
        reason_cats: Counter = Counter()
        for r in records:
            reason_text = str(r.get("reason", "")).lower()
            matched = False
            for cat, keywords in REASON_CATEGORIES.items():
                if any(kw in reason_text for kw in keywords):
                    reason_cats[cat] += 1
                    matched = True
                    break
            if not matched:
                reason_cats["other"] += 1

        top_reasons = [
            {"reason": cat, "count": count, "pct": round(count / total * 100, 1)}
            for cat, count in reason_cats.most_common(5)
        ]

        late_returns = sum(1 for d in days if d > 30)

        return {
            "total_refunds": total,
            "approval_rate": round(len(approved) / total, 3),
            "total_refund_amount": round(sum(amounts), 2),
            "avg_amount": round(sum(amounts) / total, 2),
            "max_amount": round(max(amounts), 2),
            "top_reasons": top_reasons,
            "avg_days_since_purchase": round(sum(days) / total, 1),
            "late_returns_pct": round(late_returns / total * 100, 1),
            "preventable_pct": round(
                sum(v for k, v in reason_cats.items() if k in ("size_fit", "wrong_item")) / total * 100, 1
            ),
        }

    def _score_policy(self, policy: dict, analysis: dict) -> float:
        score = 50.0
        # Return window
        window = policy.get("return_window_days", 30)
        if window >= 60: score += 20
        elif window >= 30: score += 10
        elif window < 14: score -= 20
        # Restocking fee
        fee = policy.get("restocking_fee_pct", 0)
        if fee == 0: score += 15
        elif fee <= 10: score += 5
        elif fee > 20: score -= 15
        # Free returns
        if policy.get("free_returns", True): score += 15
        else: score -= 10
        # Exchanges
        if policy.get("exchange_allowed", True): score += 5
        # Late returns rate
        if analysis.get("late_returns_pct", 0) > 20: score -= 5
        return round(min(max(score, 0), 100), 1)

    def _optimize_policy(self, current: dict, analysis: dict, goal: Goal) -> dict:
        opt = dict(current)
        preventable = analysis.get("preventable_pct", 0)
        approval_rate = analysis.get("approval_rate", 0.85)

        if goal == "maximize_retention":
            opt["return_window_days"] = max(current.get("return_window_days", 30), 45)
            opt["restocking_fee_pct"] = 0
            opt["free_returns"] = True
            opt["exchange_allowed"] = True
            opt["instant_refund"] = True
        elif goal == "minimize_costs":
            opt["return_window_days"] = min(current.get("return_window_days", 30), 21)
            opt["restocking_fee_pct"] = max(current.get("restocking_fee_pct", 0), 10)
            opt["free_returns"] = False
            opt["require_photos"] = True
            opt["instant_refund"] = False
        else:  # balanced
            opt["return_window_days"] = 30
            opt["restocking_fee_pct"] = 5 if approval_rate > 0.9 else 0
            opt["free_returns"] = True
            opt["exchange_allowed"] = True
            opt["size_guide_required"] = preventable > 20

        # Universal best practices
        opt["recommendations"] = self._generate_recommendations(analysis, goal)
        return opt

    def _estimate_impact(self, current: dict, optimized: dict, analysis: dict, goal: Goal) -> dict:
        window_change = optimized.get("return_window_days", 30) - current.get("return_window_days", 30)
        fee_change = optimized.get("restocking_fee_pct", 0) - current.get("restocking_fee_pct", 0)

        retention_delta = 0.0
        cost_delta = 0.0
        conversion_delta = 0.0

        if window_change > 0:
            retention_delta += window_change * 0.001
            conversion_delta += window_change * 0.0005

        if fee_change < 0:
            retention_delta += 0.02
            conversion_delta += 0.01

        if optimized.get("free_returns") and not current.get("free_returns"):
            retention_delta += 0.03
            conversion_delta += 0.015
            cost_delta -= analysis.get("total_refund_amount", 0) * 0.05

        if optimized.get("instant_refund"):
            retention_delta += 0.02

        return {
            "retention_rate_change": f"{retention_delta:+.1%}",
            "conversion_rate_change": f"{conversion_delta:+.1%}",
            "estimated_cost_change_usd": round(cost_delta, 2),
            "customer_satisfaction_impact": "High" if goal == "maximize_retention" else ("Medium" if goal == "balanced" else "Low"),
        }

    @staticmethod
    def _generate_recommendations(analysis: dict, goal: Goal) -> list[str]:
        recs = []
        if analysis.get("preventable_pct", 0) > 20:
            recs.append("Reduce preventable returns: improve size guides and product descriptions to cut size/fit and wrong-item returns.")
        if analysis.get("late_returns_pct", 0) > 15:
            recs.append("Enforce return window strictly with automated deadline reminders at 7 and 3 days before expiry.")
        if goal in ("maximize_retention", "balanced"):
            recs.append("Offer instant store credit as an alternative to cash refunds — reduces processing costs while improving NPS.")
        if analysis.get("approval_rate", 1) < 0.75:
            recs.append("Low approval rate detected — review rejection criteria to avoid customer frustration and chargebacks.")
        recs.append("Implement pre-return product photos to detect fraud while maintaining legitimate customer experience.")
        return recs
