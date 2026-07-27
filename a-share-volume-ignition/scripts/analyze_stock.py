#!/usr/bin/env python3
"""Fetch and analyze A-share minute turnover ignition using Eastmoney web data."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from signal_engine import Thresholds, classify_signal


USER_AGENT = "Mozilla/5.0"
REFERER = "https://quote.eastmoney.com/"


def fetch_json(url: str, retries: int = 6) -> Dict[str, Any]:
    errors: List[str] = []
    for attempt in range(retries):
        separator = "&" if "?" in url else "?"
        cache_buster = f"_={int(time.time() * 1000)}{attempt}"
        request = urllib.request.Request(
            f"{url}{separator}{cache_buster}",
            headers={"User-Agent": USER_AGENT, "Referer": REFERER},
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = json.load(response)
            if payload.get("data") is None:
                raise RuntimeError(f"empty data payload: {payload.get('message') or payload.get('msg')}")
            return payload
        except Exception as exc:  # Public endpoint failures vary by platform.
            errors.append(f"{type(exc).__name__}: {exc}")
            if attempt + 1 < retries:
                time.sleep(0.8 + attempt * 0.7)
    raise RuntimeError("Eastmoney request failed after retries: " + " | ".join(errors[-3:]))


def code_to_secid(code: str) -> str:
    code = code.strip()
    if "." in code and code.split(".", 1)[0] in {"0", "1", "90"}:
        return code
    digits = "".join(ch for ch in code if ch.isdigit())
    if len(digits) != 6:
        raise ValueError(f"cannot infer a six-digit stock code from {code!r}")
    market = "1" if digits.startswith(("5", "6", "9")) else "0"
    return f"{market}.{digits}"


def resolve_symbol(value: str) -> str:
    try:
        return code_to_secid(value)
    except ValueError:
        pass

    query = urllib.parse.quote(value)
    token = "D43BF722C8E33BDC906FB84D85E326E8"
    url = (
        "https://searchapi.eastmoney.com/api/suggest/get"
        f"?input={query}&type=14&token={token}&count=10"
    )
    payload = fetch_json(url)
    table = payload.get("QuotationCodeTable") or {}
    candidates = table.get("Data") or []
    for item in candidates:
        code = str(item.get("Code") or "")
        quote_id = str(item.get("QuoteID") or "")
        name = str(item.get("Name") or "")
        if len(code) == 6 and (name == value or value in name):
            return quote_id or code_to_secid(code)
    raise ValueError(f"could not resolve stock name {value!r}; pass its six-digit code")


def parse_trends(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for raw in data.get("trends") or []:
        parts = raw.split(",")
        if len(parts) < 8:
            continue
        date, clock = parts[0].split()
        rows.append(
            {
                "date": date,
                "time": clock,
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume_lots": int(float(parts[5])),
                "amount": float(parts[6]),
                "vwap": float(parts[7]),
            }
        )
    return rows


def get_quote(secid: str) -> Dict[str, Any]:
    fields = ",".join(
        [
            "f43", "f44", "f45", "f46", "f47", "f48", "f50", "f51", "f52",
            "f57", "f58", "f60", "f71", "f116", "f117", "f127", "f128",
            "f129", "f135", "f136", "f137", "f138", "f139", "f140", "f141",
            "f142", "f143", "f144", "f145", "f146", "f147", "f148", "f149",
            "f168", "f169", "f170",
        ]
    )
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields={fields}"
    return fetch_json(url)["data"]


def get_trends(secid: str, days: int = 5) -> Dict[str, Any]:
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
        f"?secid={secid}"
        "&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
        "&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
        f"&iscr=0&iscca=0&ndays={days}"
    )
    return fetch_json(url)["data"]


def get_flow(secid: str) -> Dict[str, Any]:
    url = (
        "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
        f"?lmt=0&klt=1&secid={secid}"
        "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56"
    )
    return fetch_json(url)["data"]


def parse_flow(data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    for raw in data.get("klines") or []:
        parts = raw.split(",")
        if len(parts) < 6:
            continue
        result[parts[0][-5:]] = {
            "main_net": float(parts[1]),
            "small_net": float(parts[2]),
            "medium_net": float(parts[3]),
            "large_net": float(parts[4]),
            "super_large_net": float(parts[5]),
        }
    return result


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.mean(values) if values else 0.0


def cluster_windows(windows: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    groups: List[List[Dict[str, Any]]] = []
    for window in windows:
        if not groups or window["index"] > groups[-1][-1]["index"] + 2:
            groups.append([window])
        else:
            groups[-1].append(window)
    return groups


def summarize_event(
    group: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
    flow: Dict[str, Dict[str, float]],
) -> Dict[str, Any]:
    first_index = group[0]["index"] - 2
    last_index = group[-1]["index"]
    start_reference_index = max(0, first_index - 1)
    segment = rows[first_index : last_index + 1]
    start_price = rows[start_reference_index]["close"]
    peak_row = max(segment, key=lambda row: row["high"])
    resistance_rows = rows[:first_index]
    resistance = max((row["high"] for row in resistance_rows), default=start_price)
    peak_rs3 = max(window["rs3"] for window in group)
    best_return = max(window["return_pct"] for window in group)
    end_time = rows[last_index]["time"]
    start_time = rows[first_index]["time"]
    flow_start = flow.get(rows[start_reference_index]["time"]) or {}
    flow_end = flow.get(end_time) or {}
    main_delta = float(flow_end.get("main_net") or 0) - float(flow_start.get("main_net") or 0)
    super_delta = float(flow_end.get("super_large_net") or 0) - float(
        flow_start.get("super_large_net") or 0
    )
    return {
        "start_time": start_time,
        "end_time": end_time,
        "start_index": first_index,
        "end_index": last_index,
        "start_price": round(start_price, 4),
        "end_price": round(rows[last_index]["close"], 4),
        "peak_price": round(peak_row["high"], 4),
        "peak_time": peak_row["time"],
        "turnover": round(sum(row["amount"] for row in segment), 2),
        "peak_rs3": round(peak_rs3, 3),
        "best_return_pct": round(best_return, 3),
        "resistance": round(resistance, 4),
        "main_flow_delta": round(main_delta, 2),
        "super_large_flow_delta": round(super_delta, 2),
    }


def calculate_windows(
    current: List[Dict[str, Any]],
    history_by_time: Dict[str, List[float]],
    thresholds: Thresholds,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_windows: List[Dict[str, Any]] = []
    positive: List[Dict[str, Any]] = []
    negative: List[Dict[str, Any]] = []
    for index in range(3, len(current)):
        segment = current[index - 2 : index + 1]
        if segment[-1]["time"] in {"09:30", "15:00"}:
            continue
        baseline_parts = [history_by_time.get(row["time"]) or [] for row in segment]
        if any(not values for values in baseline_parts):
            continue
        current_amount = sum(row["amount"] for row in segment)
        baseline_amount = sum(mean(values) for values in baseline_parts)
        if baseline_amount <= 0:
            continue
        return_pct = (segment[-1]["close"] / current[index - 3]["close"] - 1) * 100
        window = {
            "index": index,
            "start_time": segment[0]["time"],
            "end_time": segment[-1]["time"],
            "rs3": current_amount / baseline_amount,
            "return_pct": return_pct,
            "turnover": current_amount,
            "close": segment[-1]["close"],
            "vwap": segment[-1]["vwap"],
        }
        all_windows.append(window)
        if (
            window["rs3"] >= thresholds.ignition_rs3
            and return_pct >= thresholds.ignition_return_pct
            and window["close"] > window["vwap"]
        ):
            positive.append(window)
        if (
            window["rs3"] >= thresholds.ignition_rs3
            and return_pct <= -thresholds.ignition_return_pct
        ):
            negative.append(window)
    return all_windows, positive, negative


def rolling_rs5(
    current: List[Dict[str, Any]],
    history_by_time: Dict[str, List[float]],
) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for index in range(4, len(current)):
        segment = current[index - 4 : index + 1]
        baseline_parts = [history_by_time.get(row["time"]) or [] for row in segment]
        if any(not values for values in baseline_parts):
            continue
        current_speed = mean(row["amount"] for row in segment)
        baseline_speed = mean(mean(values) for values in baseline_parts)
        result.append(
            {
                "index": index,
                "time": segment[-1]["time"],
                "speed": current_speed,
                "rs5": current_speed / baseline_speed if baseline_speed else 0,
                "close": segment[-1]["close"],
            }
        )
    return result


def analyze_pullback(
    events: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
    thresholds: Thresholds,
) -> Dict[str, Any]:
    if not events:
        return {"observed": False, "valid": False}
    first = events[0]
    next_start = events[1]["start_index"] if len(events) > 1 else len(rows) - 1
    if next_start <= first["end_index"]:
        return {"observed": False, "valid": False}
    segment = rows[first["end_index"] + 1 : next_start + 1]
    if not segment:
        return {"observed": False, "valid": False}
    trough = min(segment, key=lambda row: row["low"])
    impulse = first["peak_price"] - first["start_price"]
    retrace = (
        (first["peak_price"] - trough["low"]) / impulse
        if impulse > 0
        else math.inf
    )
    ignition_rows = rows[first["start_index"] : first["end_index"] + 1]
    ignition_speed = mean(row["amount"] for row in ignition_rows)
    pullback_speed = mean(row["amount"] for row in segment)
    volume_ratio = pullback_speed / ignition_speed if ignition_speed else math.inf
    volume_contracted = volume_ratio <= thresholds.pullback_volume_max
    price_held = trough["low"] >= first["start_price"]
    valid = retrace <= thresholds.healthy_retrace_max and price_held and (
        volume_contracted or len(events) > 1
    )
    return {
        "observed": True,
        "valid": valid,
        "trough_time": trough["time"],
        "trough_price": round(trough["low"], 4),
        "retrace_ratio": round(retrace, 3) if math.isfinite(retrace) else None,
        "volume_ratio": round(volume_ratio, 3) if math.isfinite(volume_ratio) else None,
        "volume_contracted": volume_contracted,
        "price_held": price_held,
    }


def analyze_limit_state(
    rows: List[Dict[str, Any]],
    upper_limit: Optional[float],
) -> Dict[str, Any]:
    if not upper_limit or upper_limit <= 0:
        return {"available": False, "locked": False, "reseal_confirmed": False}
    tolerance = max(0.001, upper_limit * 0.0002)
    touches = [index for index, row in enumerate(rows) if row["high"] >= upper_limit - tolerance]
    if not touches:
        return {
            "available": True,
            "upper_limit": upper_limit,
            "touched": False,
            "locked": False,
            "reseal_confirmed": False,
        }
    first = touches[0]
    opened_after = any(row["low"] < upper_limit - tolerance for row in rows[first + 1 :])
    reseal_index: Optional[int] = None
    if opened_after:
        for index in range(first + 1, len(rows)):
            if rows[index]["close"] >= upper_limit - tolerance and all(
                row["close"] >= upper_limit - tolerance for row in rows[index:]
            ):
                reseal_index = index
                break
    locked = rows[-1]["close"] >= upper_limit - tolerance and all(
        row["close"] >= upper_limit - tolerance for row in rows[-3:]
    )
    return {
        "available": True,
        "upper_limit": upper_limit,
        "touched": True,
        "first_touch_time": rows[first]["time"],
        "opened_after_touch": opened_after,
        "locked": locked,
        "reseal_time": rows[reseal_index]["time"] if reseal_index is not None else None,
        "reseal_confirmed": bool(opened_after and locked and reseal_index is not None),
    }


def board_analysis(
    board: str,
    stock_change_pct: float,
    stock_peak_rs3: float,
    stock_events: List[Dict[str, Any]],
    cutoff: str,
) -> Dict[str, Any]:
    secid = board if board.startswith("90.") else f"90.{board}"
    trends_data = get_trends(secid, 5)
    rows = parse_trends(trends_data)
    by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_date[row["date"]].append(row)
    dates = sorted(by_date)
    if not dates:
        return {"available": False, "issues": ["board minute data is empty"]}
    current_date = dates[-1]
    current = [row for row in by_date[current_date] if row["time"] <= cutoff]
    history = dates[:-1]
    history_by_time: Dict[str, List[float]] = defaultdict(list)
    for date in history:
        for row in by_date[date]:
            history_by_time[row["time"]].append(row["amount"])
    by_clock = {row["time"]: row for row in current}
    event_returns: List[float] = []
    event_rs3: List[float] = []
    for event in stock_events:
        start = by_clock.get(event["start_time"])
        end = by_clock.get(event["end_time"])
        if start and end and start["close"]:
            event_returns.append((end["close"] / start["close"] - 1) * 100)
        end_index = next(
            (index for index, row in enumerate(current) if row["time"] == event["end_time"]),
            None,
        )
        if end_index is not None and end_index >= 2:
            segment = current[end_index - 2 : end_index + 1]
            baseline = sum(mean(history_by_time.get(row["time"]) or []) for row in segment)
            if baseline > 0:
                event_rs3.append(sum(row["amount"] for row in segment) / baseline)

    code = secid.split(".", 1)[1]
    clist_url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        f"?pn=1&pz=500&po=1&np=1&fltt=2&invt=2&fid=f3&fs=b:{code}"
        "&fields=f2,f3,f6,f12,f14"
    )
    constituents = fetch_json(clist_url)["data"].get("diff") or []
    changes = sorted(float(item.get("f3") or 0) for item in constituents)
    positive = sum(1 for value in changes if value > 0)
    preclose = float(trends_data.get("preClose") or 0)
    last_close = current[-1]["close"] if current else 0
    return {
        "available": True,
        "code": code,
        "name": trends_data.get("name"),
        "change_pct": (last_close / preclose - 1) * 100 if preclose else 0,
        "breadth_ratio": positive / len(changes) if changes else 0,
        "up": positive,
        "flat": sum(1 for value in changes if value == 0),
        "down": sum(1 for value in changes if value < 0),
        "total": len(changes),
        "median_change_pct": statistics.median(changes) if changes else None,
        "event_returns_pct": event_returns,
        "event_rs3": event_rs3,
        "stock_change_pct": stock_change_pct,
        "stock_peak_rs3": stock_peak_rs3,
    }


def scaled_price(value: Any) -> Optional[float]:
    if value in (None, "-", 0):
        return None
    return float(value) / 100


def build_analysis(
    secid: str,
    board: Optional[str],
    thresholds: Thresholds,
    throttle: float,
) -> Dict[str, Any]:
    quote = get_quote(secid)
    time.sleep(throttle)
    trends_data = get_trends(secid, 5)
    time.sleep(throttle)
    try:
        flow_data = get_flow(secid)
        flow_rows = parse_flow(flow_data)
        flow_issue = None
    except Exception as exc:
        flow_rows = {}
        flow_issue = str(exc)

    rows = parse_trends(trends_data)
    by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_date[row["date"]].append(row)
    dates = sorted(by_date)
    if not dates:
        raise RuntimeError("minute trend response contained no usable rows")
    current_date = dates[-1]
    current = by_date[current_date]
    history_dates = dates[:-1]
    cutoff = current[-1]["time"]

    history_by_time: Dict[str, List[float]] = defaultdict(list)
    for date in history_dates:
        for row in by_date[date]:
            history_by_time[row["time"]].append(row["amount"])

    all_windows, positive_windows, negative_windows = calculate_windows(
        current, history_by_time, thresholds
    )
    positive_events = [
        summarize_event(group, current, flow_rows)
        for group in cluster_windows(positive_windows)
    ]
    negative_events = [
        summarize_event(group, current, flow_rows)
        for group in cluster_windows(negative_windows)
    ]
    rs5_rows = rolling_rs5(current, history_by_time)

    current_amount = sum(row["amount"] for row in current)
    historical_cumulative = [
        sum(row["amount"] for row in by_date[date] if row["time"] <= cutoff)
        for date in history_dates
    ]
    usable_historical = [value for value in historical_cumulative if value > 0]
    cumulative_rvol = (
        current_amount / mean(usable_historical) if usable_historical else 0
    )
    preclose = float(trends_data.get("preClose") or scaled_price(quote.get("f60")) or 0)
    latest = current[-1]
    stock_change_pct = (latest["close"] / preclose - 1) * 100 if preclose else 0
    peak_any_rs3 = max((window["rs3"] for window in all_windows), default=0)
    peak_positive_rs3 = max((window["rs3"] for window in positive_windows), default=0)
    peak_positive_return = max(
        (window["return_pct"] for window in positive_windows), default=0
    )
    peak_negative_return = min(
        (window["return_pct"] for window in negative_windows), default=0
    )
    recent_rs5 = rs5_rows[-1]["rs5"] if rs5_rows else 0

    pullback = analyze_pullback(positive_events, current, thresholds)
    second_ignition = len(positive_events) >= 2
    breakout = False
    breakout_level = None
    if positive_events:
        event = positive_events[-1]
        breakout_level = event["resistance"]
        breakout = event["peak_price"] >= event["resistance"] * (
            1 + thresholds.breakout_buffer_pct / 100
        )

    continuation = bool(
        positive_events
        and (
            recent_rs5 >= thresholds.continuation_rs5
            or second_ignition
            or latest["close"] >= positive_events[-1]["peak_price"]
        )
        and latest["close"] >= latest["vwap"]
    )
    failed_structure = bool(
        positive_events
        and not second_ignition
        and (
            (
                pullback.get("observed")
                and not pullback.get("price_held", True)
                and latest["close"] < positive_events[-1]["peak_price"]
            )
            or (
                latest["close"] < latest["vwap"]
                and latest["close"] < positive_events[-1]["start_price"]
            )
        )
    )

    strongest_window = max(all_windows, key=lambda item: item["rs3"], default=None)
    high_volume_stall = bool(
        strongest_window
        and strongest_window["rs3"] >= thresholds.ignition_rs3
        and abs(strongest_window["return_pct"]) < thresholds.ignition_return_pct / 2
        and not positive_events
        and not negative_events
    )

    upper_limit = scaled_price(quote.get("f51"))
    limit_state = analyze_limit_state(current, upper_limit)
    latest_flow = flow_rows.get(cutoff) or (next(reversed(flow_rows.values())) if flow_rows else {})

    data_issues: List[str] = []
    if len(history_dates) < 4:
        data_issues.append(f"only {len(history_dates)} completed baseline sessions are available")
    elif len(history_dates) < 20:
        data_issues.append(
            f"public endpoint provides {len(history_dates)} completed baseline sessions, below the preferred 20"
        )
    if flow_issue:
        data_issues.append("minute flow unavailable: " + flow_issue)
    usable = bool(current and usable_historical)

    sector: Dict[str, Any] = {"available": False}
    if board:
        time.sleep(throttle)
        try:
            sector = board_analysis(
                board,
                stock_change_pct,
                peak_positive_rs3,
                positive_events,
                cutoff,
            )
        except Exception as exc:
            sector = {"available": False, "issues": [str(exc)]}

    metrics: Dict[str, Any] = {
        "data_quality": {"usable": usable, "issues": data_issues},
        "peak_rs3": peak_positive_rs3 if positive_events else peak_any_rs3,
        "peak_positive_return_pct": peak_positive_return,
        "peak_negative_return_pct": peak_negative_return,
        "cumulative_rvol": cumulative_rvol,
        "positive_events": positive_events,
        "negative_events": negative_events,
        "breakout": breakout,
        "continuation": continuation,
        "latest_above_vwap": latest["close"] >= latest["vwap"],
        "failed_structure": failed_structure,
        "high_volume_stall": high_volume_stall,
        "pullback": pullback,
        "second_ignition": second_ignition,
        "limit_state": limit_state,
        "flow": {
            "available": bool(latest_flow),
            "main_net": float(latest_flow.get("main_net") or quote.get("f137") or 0),
            "large_net": float(latest_flow.get("large_net") or quote.get("f143") or 0),
            "super_large_net": float(
                latest_flow.get("super_large_net") or quote.get("f140") or 0
            ),
        },
        "sector": sector,
    }
    classification = classify_signal(metrics, thresholds)

    return {
        "symbol": {
            "secid": secid,
            "code": quote.get("f57"),
            "name": quote.get("f58") or trends_data.get("name"),
            "industry": quote.get("f127"),
            "concepts": str(quote.get("f129") or "").split(",") if quote.get("f129") else [],
        },
        "timestamp": f"{current_date} {cutoff}",
        "session_date": current_date,
        "baseline_sessions": history_dates,
        "snapshot": {
            "preclose": preclose,
            "open": current[0]["open"],
            "high": max(row["high"] for row in current),
            "low": min(row["low"] for row in current),
            "last": latest["close"],
            "change_pct": stock_change_pct,
            "vwap": latest["vwap"],
            "turnover_amount": current_amount,
            "cumulative_rvol": cumulative_rvol,
            "turnover_rate_pct": float(quote.get("f168") or 0) / 100,
            "volume_ratio": float(quote.get("f50") or 0) / 100,
            "market_cap": float(quote.get("f116") or 0),
            "upper_limit": upper_limit,
            "lower_limit": scaled_price(quote.get("f52")),
        },
        "flow": metrics["flow"],
        "events": {
            "positive": positive_events,
            "negative": negative_events,
            "peak_rs3": peak_any_rs3,
            "peak_positive_rs3": peak_positive_rs3,
            "recent_rs5": recent_rs5,
            "breakout": breakout,
            "breakout_level": breakout_level,
            "continuation": continuation,
            "pullback": pullback,
            "second_ignition": second_ignition,
            "failed_structure": failed_structure,
            "high_volume_stall": high_volume_stall,
            "limit_state": limit_state,
        },
        "sector": sector,
        "classification": classification,
        "data_quality": metrics["data_quality"],
        "thresholds": thresholds.__dict__,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze A-share intraday volume ignition from Eastmoney minute data."
    )
    parser.add_argument("stock", help="Six-digit code, Eastmoney secid, or exact Chinese name")
    parser.add_argument("--board", help="Related Eastmoney board code, for example BK0473")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    parser.add_argument("--throttle", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--ignition-rs3", type=float, default=2.5)
    parser.add_argument("--ignition-return", type=float, default=0.4)
    parser.add_argument("--continuation-rs5", type=float, default=1.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    thresholds = Thresholds(
        ignition_rs3=args.ignition_rs3,
        ignition_return_pct=args.ignition_return,
        continuation_rs5=args.continuation_rs5,
    )
    try:
        secid = resolve_symbol(args.stock)
        result = build_analysis(secid, args.board, thresholds, max(0.0, args.throttle))
    except Exception as exc:
        error = {
            "classification": {
                "state": "data_insufficient",
                "score": 0,
                "reasons": [str(exc)],
                "failures": [],
            }
        }
        print(json.dumps(error, ensure_ascii=False, indent=2))
        return 2

    text = json.dumps(
        result,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
    )
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
