#!/usr/bin/env python3
"""Pure classification logic for A-share intraday volume ignition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Thresholds:
    ignition_rs3: float = 2.5
    ignition_return_pct: float = 0.4
    continuation_rs5: float = 1.5
    breakout_buffer_pct: float = 0.15
    healthy_retrace_max: float = 0.50
    pullback_volume_max: float = 0.65
    sector_breadth_min: float = 0.60


def _score_ratio(value: float, low: float, high: float, points: int) -> int:
    if value <= low:
        return 0
    if value >= high:
        return points
    return round(points * (value - low) / (high - low))


def classify_sector(metrics: Dict[str, Any], thresholds: Thresholds | None = None) -> Dict[str, Any]:
    t = thresholds or Thresholds()
    if not metrics or not metrics.get("available"):
        return {
            "available": False,
            "direction_sync": False,
            "breadth_sync": False,
            "turnover_sync": False,
            "role": "unknown",
            "score": 0,
        }

    board_pct = float(metrics.get("change_pct") or 0)
    breadth = float(metrics.get("breadth_ratio") or 0)
    event_returns = metrics.get("event_returns_pct") or []
    event_rs3 = metrics.get("event_rs3") or []
    stock_pct = float(metrics.get("stock_change_pct") or 0)
    median_pct = metrics.get("median_change_pct")
    stock_peak_rs3 = float(metrics.get("stock_peak_rs3") or 0)

    positive_windows = sum(1 for value in event_returns if value > 0)
    direction_sync = board_pct > 0 and (
        not event_returns or positive_windows >= max(1, (len(event_returns) + 1) // 2)
    )
    breadth_sync = breadth >= t.sector_breadth_min
    turnover_sync = any(value >= t.continuation_rs5 for value in event_rs3)

    if direction_sync and breadth_sync and turnover_sync:
        role = "co_ignition"
    elif direction_sync and breadth_sync:
        if (
            median_pct is not None
            and stock_pct <= float(median_pct)
            and stock_peak_rs3 < t.ignition_rs3 * 1.2
            and not turnover_sync
        ):
            role = "sector_following"
        elif stock_peak_rs3 >= t.ignition_rs3:
            role = "independent_stock_ignition_in_strong_sector"
        else:
            role = "strong_sector_environment"
    elif stock_peak_rs3 >= t.ignition_rs3:
        role = "independent_stock_ignition"
    else:
        role = "weak_or_no_sector_sync"

    score = 0
    score += 4 if direction_sync else 0
    score += 4 if breadth_sync else 0
    score += 2 if turnover_sync else 0
    return {
        "available": True,
        "direction_sync": direction_sync,
        "breadth_sync": breadth_sync,
        "turnover_sync": turnover_sync,
        "role": role,
        "score": score,
    }


def classify_signal(metrics: Dict[str, Any], thresholds: Thresholds | None = None) -> Dict[str, Any]:
    """Return one primary state, score, reasons, and failed requirements."""
    t = thresholds or Thresholds()
    reasons: List[str] = []
    failures: List[str] = []

    quality = metrics.get("data_quality") or {}
    if not quality.get("usable", False):
        return {
            "state": "data_insufficient",
            "score": 0,
            "reasons": quality.get("issues") or ["minute history or quote data is insufficient"],
            "failures": [],
        }

    peak_rs3 = float(metrics.get("peak_rs3") or 0)
    peak_return = float(metrics.get("peak_positive_return_pct") or 0)
    peak_negative_return = float(metrics.get("peak_negative_return_pct") or 0)
    cumulative_rvol = float(metrics.get("cumulative_rvol") or 0)
    has_positive_event = bool(metrics.get("positive_events"))
    has_negative_event = bool(metrics.get("negative_events"))
    breakout = bool(metrics.get("breakout"))
    continuation = bool(metrics.get("continuation"))
    latest_above_vwap = bool(metrics.get("latest_above_vwap"))
    failed_structure = bool(metrics.get("failed_structure"))
    high_volume_stall = bool(metrics.get("high_volume_stall"))
    pullback = metrics.get("pullback") or {}
    second_ignition = bool(metrics.get("second_ignition"))
    limit_state = metrics.get("limit_state") or {}
    flow = metrics.get("flow") or {}
    sector = classify_sector(metrics.get("sector") or {}, t)

    score = 0
    score += _score_ratio(peak_rs3, 1.0, 5.0, 25)
    score += _score_ratio(peak_return, 0.0, 1.5, 15)
    score += 20 if breakout else 0
    score += 15 if continuation else 0
    if float(flow.get("main_net") or 0) > 0:
        score += 8
    if float(flow.get("super_large_net") or 0) > 0:
        score += 7
    score += sector["score"]
    score = min(100, score)

    if limit_state.get("reseal_confirmed"):
        reasons.extend(["upper limit opened and later resealed", "price remained locked after the reseal"])
        if flow.get("main_net", 0) > 0:
            reasons.append("main-order flow remained positive")
        return {
            "state": "limit_reseal_confirmed",
            "score": max(score, 80),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    if limit_state.get("locked"):
        reasons.append("price is continuously locked at the exchange upper limit")
        reasons.append("post-lock turnover decay is not treated as momentum decay")
        return {
            "state": "limit_locked",
            "score": max(score, 75 if has_positive_event else 60),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    if has_negative_event and peak_negative_return <= -t.ignition_return_pct:
        reasons.append("abnormal turnover accompanied an accelerating price decline")
        if float(flow.get("main_net") or 0) < 0:
            reasons.append("main-order flow is negative")
        return {
            "state": "sell_acceleration",
            "score": min(score, 45),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    if high_volume_stall:
        reasons.append("turnover was abnormal but upward price response was weak")
        if float(flow.get("main_net") or 0) < 0:
            reasons.append("large-order flow did not confirm accumulation")
        return {
            "state": "high_volume_stall",
            "score": min(score, 55),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    if has_positive_event:
        reasons.append(f"peak three-minute relative turnover reached {peak_rs3:.2f}x")
        reasons.append(f"best qualifying three-minute price response was {peak_return:.2f}%")

        if failed_structure:
            failures.append("price lost the ignition origin, breakout structure, or VWAP")
            return {
                "state": "failed_ignition",
                "score": min(score, 55),
                "reasons": reasons,
                "failures": failures,
                "sector": sector,
            }

        if second_ignition and pullback.get("valid"):
            reasons.append("pullback stayed within the accepted depth")
            if pullback.get("volume_contracted"):
                reasons.append("pullback turnover contracted")
            else:
                reasons.append("pullback was accepted through price and flow despite elevated turnover")
            reasons.append("a second qualifying ignition followed")
            return {
                "state": "retest_confirmed",
                "score": max(score, 75),
                "reasons": reasons,
                "failures": failures,
                "sector": sector,
            }

        if breakout and continuation:
            reasons.extend(["price broke resistance", "turnover and price persisted after breakout"])
            return {
                "state": "direct_confirmed",
                "score": max(score, 72),
                "reasons": reasons,
                "failures": failures,
                "sector": sector,
            }

        if breakout and pullback.get("observed"):
            reasons.append("price broke resistance and is now in a pullback evaluation window")
            if not pullback.get("valid"):
                failures.append("pullback has not met depth, volume, or support requirements")
            return {
                "state": "retest_pending",
                "score": min(max(score, 58), 72),
                "reasons": reasons,
                "failures": failures,
                "sector": sector,
            }

        if breakout:
            reasons.append("resistance was attacked but persistence is not yet established")
            failures.append("continuation or a valid retest is still required")
            return {
                "state": "breakout_pending",
                "score": min(max(score, 55), 70),
                "reasons": reasons,
                "failures": failures,
                "sector": sector,
            }

        failures.append("no effective resistance breakout")
        if not continuation:
            failures.append("five-minute relative turnover did not persist")
        return {
            "state": "ignition_candidate",
            "score": min(max(score, 45), 65),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    if sector.get("role") == "sector_following" or (
        sector.get("direction_sync") and sector.get("breadth_sync") and cumulative_rvol < 1.0
    ):
        reasons.append("the related board was broadly positive")
        failures.extend(["stock-level ignition threshold was not met", "stock cumulative turnover was not abnormal"])
        return {
            "state": "sector_following",
            "score": min(score + 20, 50),
            "reasons": reasons,
            "failures": failures,
            "sector": sector,
        }

    failures.append("no qualifying abnormal-turnover and positive-price-response window")
    if not latest_above_vwap:
        failures.append("latest price is not above VWAP")
    return {
        "state": "no_ignition",
        "score": min(score, 40),
        "reasons": reasons,
        "failures": failures,
        "sector": sector,
    }
