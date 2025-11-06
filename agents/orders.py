"""Order utilities for autonomous and user-driven agents.

This module encapsulates backend logic for fetching and processing agent
orders. It can be imported directly or invoked as a CLI helper so that other
runtimes (for example the Next.js API layer) can delegate complex workflows to
Python while keeping a clean separation of concerns.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Literal, Optional

OrderType = Literal["analysis", "execution", "simulation"]
ExecutionMode = Literal["autonomous", "guided", "manual"]


@dataclass(slots=True)
class Order:
    """Structured representation of an agent order."""

    order_id: str
    kind: OrderType
    mode: ExecutionMode
    payload: dict
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialise to a dictionary that can be JSON encoded."""

        return {
            "order_id": self.order_id,
            "kind": self.kind,
            "mode": self.mode,
            "payload": self.payload,
            "issued_at": self.issued_at.isoformat(),
        }


def _demo_orders() -> List[Order]:
    """Generate demo orders used when no external broker is configured."""

    return [
        Order(
            order_id="ORD-AUTO-001",
            kind="analysis",
            mode="autonomous",
            payload={
                "symbol": "SOL",
                "timeframe": "1h",
                "objectives": ["volatility_scan", "liquidity_review"],
            },
        ),
        Order(
            order_id="ORD-GUID-101",
            kind="simulation",
            mode="guided",
            payload={
                "symbol": "BTC",
                "benchmark": "hold_strategy",
                "duration_hours": 12,
            },
        ),
        Order(
            order_id="ORD-MAN-900",
            kind="execution",
            mode="manual",
            payload={
                "symbol": "ETH",
                "side": "buy",
                "quantity": 0.5,
                "notes": "User-triggered rebalance",
            },
        ),
    ]


def fetch_orders(mode: Optional[ExecutionMode] = None) -> List[dict]:
    """Fetch orders filtered by execution mode.

    Args:
        mode: Optional execution mode filter (autonomous, guided, manual).

    Returns:
        A list of serialised orders.
    """

    orders = _demo_orders()
    if mode:
        orders = [order for order in orders if order.mode == mode]
    return [order.to_dict() for order in orders]


def process_orders(orders: Iterable[dict]) -> dict:
    """Process orders and produce a lightweight status report.

    The current implementation scores each order based on its type and returns
    summary metrics. It can be replaced with advanced logic once real
    orchestration backends are connected.
    """

    total = 0
    autonomous = 0
    guided = 0
    manual = 0
    score = 0

    for entry in orders:
        total += 1
        mode = entry.get("mode")
        kind = entry.get("kind")

        if mode == "autonomous":
            autonomous += 1
            score += 3
        elif mode == "guided":
            guided += 1
            score += 2
        elif mode == "manual":
            manual += 1
            score += 1

        if kind == "execution":
            score += 1
        elif kind == "analysis":
            score += 2
        elif kind == "simulation":
            score += 1

    return {
        "total": total,
        "autonomous": autonomous,
        "guided": guided,
        "manual": manual,
        "composite_score": score,
    }


def execute_orders(orders: Iterable[dict]) -> dict:
    """Generate an execution recommendation from incoming orders."""

    report = process_orders(orders)
    total = report["total"]

    if total == 0:
        return {
            "decision": "idle",
            "confidence": 0.0,
            "summary": "No orders supplied for execution.",
            "metrics": report,
        }

    # Simple heuristic: reward autonomous and analysis-heavy mixes.
    score = report["composite_score"]
    confidence = min(0.95, 0.4 + 0.05 * report["autonomous"] + 0.03 * report["guided"])
    decision = "approve" if score >= total * 3 else "review"

    return {
        "decision": decision,
        "confidence": round(confidence, 2),
        "summary": f"Processed {total} orders with composite score {score}.",
        "metrics": report,
    }


def audit_orders(mode: Optional[ExecutionMode] = None) -> dict:
    """Inspect queued orders and provide a readiness report."""

    orders = fetch_orders(mode=mode)
    report = process_orders(orders)

    if report["total"] == 0:
        return {
            "decision": "clear",
            "confidence": 0.5,
            "summary": "No orders awaiting review.",
            "metrics": report,
        }

    review_needed = report["manual"] > 0 or report["guided"] > report["autonomous"]
    decision = "attention_required" if review_needed else "healthy"
    confidence = 0.6 + 0.05 * report["autonomous"]

    return {
        "decision": decision,
        "confidence": round(min(confidence, 0.95), 2),
        "summary": (
            f"Audit completed for {report['total']} orders. "
            f"Manual: {report['manual']}, Guided: {report['guided']}, Autonomous: {report['autonomous']}."
        ),
        "metrics": report,
    }


def _cli_fetch(mode: Optional[str]) -> int:
    payload = fetch_orders(mode=mode or None)
    json.dump({"orders": payload}, sys.stdout)
    return 0


def _cli_process(raw_orders: str) -> int:
    try:
        payload = json.loads(raw_orders)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON payload: {exc}", file=sys.stderr)
        return 2

    report = process_orders(payload)
    json.dump({"report": report}, sys.stdout)
    return 0


def _cli_execute(raw_orders: str) -> int:
    try:
        payload = json.loads(raw_orders)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON payload: {exc}", file=sys.stderr)
        return 2

    result = execute_orders(payload)
    json.dump(result, sys.stdout)
    return 0


def _cli_audit(mode: Optional[str]) -> int:
    result = audit_orders(mode=mode or None)
    json.dump(result, sys.stdout)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent order helper")
    parser.add_argument(
        "action",
        choices=["fetch", "process", "execute", "audit"],
        help="Action to perform",
    )
    parser.add_argument("--mode", choices=["autonomous", "guided", "manual"], help="Filter mode")
    parser.add_argument("--orders", help="JSON encoded orders (for process action)")

    args = parser.parse_args(argv)

    if args.action == "fetch":
        return _cli_fetch(args.mode)

    if args.action == "audit":
        return _cli_audit(args.mode)

    if args.orders is None:
        print("--orders is required for process/execute actions", file=sys.stderr)
        return 1

    if args.action == "process":
        return _cli_process(args.orders)

    if args.action == "execute":
        return _cli_execute(args.orders)

    print(f"Unsupported action: {args.action}", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
