#!/usr/bin/env python3
"""Deterministic edge-case tests for the signal classifier."""

from __future__ import annotations

import unittest

from signal_engine import classify_signal


def base_metrics():
    return {
        "data_quality": {"usable": True, "issues": []},
        "peak_rs3": 0.8,
        "peak_positive_return_pct": 0.0,
        "peak_negative_return_pct": 0.0,
        "cumulative_rvol": 0.9,
        "positive_events": [],
        "negative_events": [],
        "breakout": False,
        "continuation": False,
        "latest_above_vwap": True,
        "failed_structure": False,
        "high_volume_stall": False,
        "pullback": {"observed": False, "valid": False},
        "second_ignition": False,
        "limit_state": {},
        "flow": {"main_net": 0, "super_large_net": 0},
        "sector": {"available": False},
    }


class SignalEngineTests(unittest.TestCase):
    def test_no_ignition(self):
        self.assertEqual(classify_signal(base_metrics())["state"], "no_ignition")

    def test_sector_following(self):
        metrics = base_metrics()
        metrics["sector"] = {
            "available": True,
            "change_pct": 4.0,
            "breadth_ratio": 0.9,
            "event_returns_pct": [],
            "event_rs3": [],
            "stock_change_pct": 3.0,
            "median_change_pct": 4.2,
            "stock_peak_rs3": 0.8,
        }
        self.assertEqual(classify_signal(metrics)["state"], "sector_following")

    def test_ignition_candidate(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 3.2,
                "peak_positive_return_pct": 0.7,
                "positive_events": [{"start_time": "10:00"}],
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "ignition_candidate")

    def test_direct_confirmation(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 3.5,
                "peak_positive_return_pct": 0.9,
                "positive_events": [{"start_time": "10:00"}],
                "breakout": True,
                "continuation": True,
                "flow": {"main_net": 10_000_000, "super_large_net": 6_000_000},
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "direct_confirmed")

    def test_retest_confirmation(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 5.0,
                "peak_positive_return_pct": 1.2,
                "positive_events": [{"start_time": "10:00"}, {"start_time": "10:20"}],
                "breakout": True,
                "second_ignition": True,
                "pullback": {
                    "observed": True,
                    "valid": True,
                    "volume_contracted": True,
                },
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "retest_confirmed")

    def test_failed_ignition(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 3.0,
                "peak_positive_return_pct": 0.6,
                "positive_events": [{"start_time": "10:00"}],
                "failed_structure": True,
                "latest_above_vwap": False,
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "failed_ignition")

    def test_failed_weak_ignition_can_still_be_sector_following(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 2.54,
                "peak_positive_return_pct": 0.56,
                "positive_events": [{"start_time": "10:23"}],
                "failed_structure": True,
                "sector": {
                    "available": True,
                    "change_pct": 4.6,
                    "breadth_ratio": 1.0,
                    "event_returns_pct": [0.23],
                    "event_rs3": [0.99],
                    "stock_change_pct": 3.8,
                    "median_change_pct": 4.4,
                    "stock_peak_rs3": 2.54,
                },
            }
        )
        result = classify_signal(metrics)
        self.assertEqual(result["state"], "failed_ignition")
        self.assertEqual(result["sector"]["role"], "sector_following")

    def test_limit_lock_ignores_turnover_decay(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 8.0,
                "peak_positive_return_pct": 2.0,
                "positive_events": [{"start_time": "10:00"}],
                "limit_state": {"locked": True, "reseal_confirmed": False},
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "limit_locked")

    def test_limit_reseal(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 10.0,
                "peak_positive_return_pct": 2.0,
                "positive_events": [{"start_time": "10:00"}],
                "limit_state": {"locked": True, "reseal_confirmed": True},
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "limit_reseal_confirmed")

    def test_high_volume_stall(self):
        metrics = base_metrics()
        metrics.update({"peak_rs3": 4.0, "high_volume_stall": True})
        self.assertEqual(classify_signal(metrics)["state"], "high_volume_stall")

    def test_sell_acceleration(self):
        metrics = base_metrics()
        metrics.update(
            {
                "peak_rs3": 4.0,
                "peak_negative_return_pct": -1.0,
                "negative_events": [{"start_time": "10:00"}],
                "flow": {"main_net": -10_000_000, "super_large_net": -5_000_000},
            }
        )
        self.assertEqual(classify_signal(metrics)["state"], "sell_acceleration")

    def test_insufficient_data(self):
        metrics = base_metrics()
        metrics["data_quality"] = {"usable": False, "issues": ["no baseline"]}
        self.assertEqual(classify_signal(metrics)["state"], "data_insufficient")


if __name__ == "__main__":
    unittest.main()
