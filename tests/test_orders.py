import unittest

from agents.orders import audit_orders, execute_orders, fetch_orders, process_orders


class OrdersModuleTests(unittest.TestCase):
    def test_fetch_orders_returns_all(self) -> None:
        orders = fetch_orders()
        self.assertGreaterEqual(len(orders), 1)
        self.assertTrue(all("order_id" in order for order in orders))

    def test_fetch_orders_filters_by_mode(self) -> None:
        orders = fetch_orders(mode="autonomous")
        self.assertTrue(all(order["mode"] == "autonomous" for order in orders))

    def test_process_orders_scores_payload(self) -> None:
        payload = [
            {"mode": "autonomous", "kind": "analysis"},
            {"mode": "manual", "kind": "execution"},
        ]
        report = process_orders(payload)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["autonomous"], 1)
        self.assertEqual(report["manual"], 1)
        self.assertGreater(report["composite_score"], 0)

    def test_process_orders_handles_empty(self) -> None:
        report = process_orders([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["composite_score"], 0)

    def test_execute_orders_generates_decision(self) -> None:
        payload = [
            {"mode": "autonomous", "kind": "analysis"},
            {"mode": "guided", "kind": "execution"},
        ]
        result = execute_orders(payload)
        self.assertIn(result["decision"], {"approve", "review", "idle"})
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_audit_orders_returns_summary(self) -> None:
        result = audit_orders(mode="autonomous")
        self.assertIn("summary", result)
        self.assertIn(result["decision"], {"healthy", "attention_required", "clear"})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
