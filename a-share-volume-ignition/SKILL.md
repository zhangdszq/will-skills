---
name: a-share-volume-ignition
description: Analyze whether an A-share stock is experiencing intraday volume ignition, breakout confirmation, pullback validation, second ignition, limit-up locking or resealing, sector resonance, failed ignition, high-volume stalling, or sell acceleration. Use this skill whenever the user asks whether a Chinese stock has “点火”, “启动”, “放量”, “量速”, “量价共振”, “回踩确认”, “二次点火”, “板块共振”, “封板/炸板/回封”, whether a rise is independent or sector-following, or asks to inspect intraday capital-flow and minute-turnover behavior. Also use it for comparing several A-share ignition candidates. Do not use it for long-term fundamental valuation alone.
compatibility: Requires Python 3 and network access for Eastmoney public web quote endpoints. No API token is required. Supports offline interpretation when the user supplies minute or summary data.
---

# A-Share Volume Ignition

Use minute turnover, same-clock historical baselines, price response, large-order flow,
pullback structure, limit-price state, and sector breadth to classify an intraday move.
Treat the result as a description of observed market behavior, not a promise of future returns.

## Workflow

1. Resolve the stock to a six-digit code. Confirm the name returned by the data source.
2. Record the exact data timestamp and whether the session is still trading.
3. Run the bundled analyzer when live data is available:

```powershell
python scripts/analyze_stock.py 300059 --board BK0473 --pretty
```

`--board` is optional. Pass the most relevant industry or concept board when known.
Use an Eastmoney board code such as `BK0473`, with or without the `90.` prefix.

4. Read `references/signal-rules.md` before interpreting the result. It defines the
state machine, thresholds, pullback logic, limit-up exceptions, and failure cases.
5. Read `references/api-fields.md` only when an endpoint or field needs verification,
the script cannot resolve a symbol, or a public endpoint is rate-limited.
6. Cross-check the computed state against the raw event list. A label is evidence
compression, not a substitute for inspecting price and turnover together.
7. Report one primary state and, where useful, one qualifier:

- `no_ignition`: no abnormal turnover-price event
- `sector_following`: price rose mainly with a strong board, without stock-level ignition
- `ignition_candidate`: initial ignition occurred, continuation is unconfirmed
- `breakout_pending`: resistance was attacked but persistence is not yet proven
- `direct_confirmed`: breakout held without requiring a material pullback
- `retest_pending`: breakout occurred and a pullback is still being evaluated
- `retest_confirmed`: valid pullback followed by a second ignition
- `limit_locked`: ignition reached and remained at the exchange upper limit
- `limit_reseal_confirmed`: upper limit opened, held support, then resealed
- `failed_ignition`: the move lost its ignition origin, VWAP, or breakout structure
- `high_volume_stall`: abnormal turnover produced little upward price response
- `sell_acceleration`: abnormal turnover accompanied accelerating price decline
- `data_insufficient`: history, timestamp, quote, or baseline is inadequate

## Data Discipline

- Prefer turnover amount in yuan over share volume. It compares activity more fairly.
- Compare each minute with the same clock minute on prior sessions. Intraday volume
has a natural U-shape, so a raw opening bar is not automatically ignition.
- Prefer 20 valid historical sessions. The public trends endpoint commonly exposes
only four completed comparison sessions; state that limitation and reduce confidence.
- Ignore or separately label opening auction, lunch reopen, and closing auction effects.
- Use the exchange-provided upper and lower limit fields when available. Do not infer
all price limits from the stock-code prefix.
- Treat Eastmoney “main”, “large”, and “super-large” flow as vendor classifications,
not verified institutional identities.
- Never infer why funds traded, who traded, or that undisclosed information exists.
- If live endpoints fail after bounded retries, report the missing evidence. Do not
fill gaps with invented numbers or stale figures presented as current.

## Required Interpretation

Distinguish these dimensions instead of collapsing them into one “共振” claim:

1. Stock turnover ignition
2. Stock price response
3. Breakout and persistence
4. Pullback quality
5. Large-order participation
6. Sector direction
7. Sector breadth
8. Same-time sector turnover ignition

A board can have strong direction and breadth while the stock alone has abnormal
turnover. Call that “strong board environment with independent stock ignition”, not
“the whole board ignited”. A stock can also rise with a board while its own relative
turnover remains below one; call that `sector_following`.

## Limit-Up Handling

Once a stock is continuously locked at its upper limit, falling minute turnover does
not mean momentum decay. Trading can become scarce because sell liquidity disappears.
Switch from ordinary continuation logic to:

- first limit-touch time
- whether the board opened
- open-board pullback depth
- flow deterioration while open
- reseal turnover and time
- whether the price remained locked afterward
- queue size, when reliable order-book data is available

A one-price limit-up with little trading can be strong, but volume-speed analysis alone
cannot establish its sealing quality. Label the missing queue evidence.

## Report Format

Lead with a direct conclusion and timestamp:

```text
结论：截至 YYYY-MM-DD HH:MM，[股票]处于[主状态]。
它是[个股主动点火 / 板块跟涨 / 板块与个股共同点火]，[已/未]完成启动确认。
```

Then provide:

1. Snapshot table: price, change, high/low, VWAP, turnover, cumulative RVOL,
   turnover rate, main flow, super-large flow, and board breadth.
2. Event timeline: ignition windows, RS3/RS5, price response, turnover amount,
   breakout, pullback, second ignition, and limit events.
3. Sector decomposition: direction, breadth, same-time price sync, and turnover sync.
4. State reasoning: which required conditions passed or failed.
5. Key levels: resistance, ignition origin, VWAP, pullback support, and invalidation.
6. Data caveats: baseline count, missing order book, delayed quote, or API limitations.

Keep raw facts separate from inference. Use phrases such as “数据显示” for API values
and “据此判断” for the classification.

## Comparison Mode

When comparing multiple stocks, run the analyzer separately and rank only after
normalizing each stock to its own same-time history. Do not rank by raw turnover.
Show:

- primary state
- score
- peak RS3
- cumulative RVOL
- price response
- flow confirmation
- sector role
- invalidation status

Prefer a confirmed but orderly second ignition over a single extreme turnover spike.

## Bundled Resources

- `scripts/analyze_stock.py`: fetches and normalizes quote, minute, flow, and optional
  board data; emits structured JSON.
- `scripts/signal_engine.py`: pure state classification and scoring logic.
- `scripts/test_signal_engine.py`: deterministic edge-case tests.
- `references/signal-rules.md`: formulas, state transitions, thresholds, and exceptions.
- `references/api-fields.md`: Eastmoney endpoint and field mapping notes.
- `evals/evals.json`: realistic evaluation prompts covering divergent cases.
