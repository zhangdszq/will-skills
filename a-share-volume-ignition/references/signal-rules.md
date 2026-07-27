# Signal Rules

## 1. Definitions

Let `C(t)` be cumulative turnover amount in yuan.

```text
Minute speed S(t) = C(t) - C(t-1)
Acceleration K(t) = EMA(S, short) - EMA(S, long)
RS3(t) = current three-minute turnover / historical same-clock three-minute mean
RS5(t) = current five-minute turnover speed / historical same-clock five-minute mean
Cumulative RVOL = current cumulative turnover / historical same-clock cumulative mean
```

Minute turnover is already an interval approximation of the derivative of cumulative
turnover. Taking a slope of smoothed minute turnover approximates activity acceleration.

## 2. Default Thresholds

Use these as initial defaults, not universal constants:

```text
Positive ignition: RS3 >= 2.5, three-minute return >= 0.4%, close > VWAP
Negative ignition: RS3 >= 2.5, three-minute return <= -0.4%
Continuation: RS5 >= 1.5 with price holding above breakout/VWAP
Breakout buffer: 0.15%-0.30% above resistance
Healthy retrace: no more than 50% of the preceding impulse
Strong retrace: no more than 33%
Pullback turnover: no more than 65% of ignition speed
Sector breadth: at least 60% of constituents advancing
Confirmation window: normally 5-15 minutes after the trigger
```

Adapt price-response thresholds to volatility and liquidity:

- Mega-cap, low-volatility stocks may use 0.25%-0.40%.
- Small or volatile stocks should generally require 0.50%-0.80%.
- Do not lower the turnover threshold merely because the price move looks exciting.

## 3. State Machine

```text
normal
  -> ignition_candidate
  -> breakout_pending
  -> direct_confirmed

breakout_pending
  -> retest_pending
  -> retest_confirmed after second ignition

any positive state
  -> failed_ignition when origin/VWAP/structure is lost

abnormal turnover + little price response
  -> high_volume_stall

abnormal turnover + falling price
  -> sell_acceleration
```

For limit-up stocks:

```text
ignition -> first limit touch -> locked
                         \-> board opens -> pullback -> reseal -> limit_reseal_confirmed
```

## 4. Breakout

Define resistance before evaluating the trigger. Prefer, in order:

1. User-specified structural resistance
2. Prior day high or multi-day platform high
3. Intraday high established before ignition

A touch is not a breakout. Require a close above resistance with a small buffer or
several consecutive closes above it. If only minute data is available, use either:

- one five-minute close above resistance plus buffer, or
- three consecutive one-minute closes above resistance.

## 5. Pullback Validation

For ignition origin `P0`, impulse high `PH`, and pullback low `PL`:

```text
Retrace = (PH - PL) / (PH - P0)
```

Interpretation:

- `<= 0.33`: strong
- `0.33-0.50`: healthy
- `> 0.50`: weakened
- price below `P0`: normally failed

Volume contraction:

```text
Pullback volume ratio =
average pullback turnover speed / average ignition turnover speed
```

- `<= 0.65`: healthy contraction
- `0.65-0.85`: material disagreement
- `> 0.85`: elevated distribution risk

Do not require contraction mechanically when an upper-limit board opens. In that case,
accept a pullback only if price holds, main flow does not materially reverse, and a
strong reseal follows.

## 6. Second Ignition

Require:

- a new RS3 of at least 1.5-2.0 after the pullback
- acceleration turns positive again
- price breaks the pullback swing high or reseals the upper limit
- large-order flow improves or at least does not reverse

A second orderly ignition is generally more reliable than one isolated extreme spike.

## 7. Sector Resonance

Score four separate concepts:

1. Direction: board return is positive during stock ignition.
2. Breadth: advancing constituents / total constituents.
3. Timing: board price rises in the same event windows.
4. Turnover: board RS3 or RS5 is also abnormal.

Classifications:

- Strong direction and breadth, stock RS below threshold: `sector_following`
- Strong direction and breadth, stock RS abnormal, board RS normal:
  independent stock ignition in a strong sector
- Stock and board turnover abnormal at the same time: `co_ignition`
- Stock abnormal while board weak: independent stock ignition

An industry label and a concept label may differ. State which board was used and why.

## 8. Special Cases

### Opening auction and first minutes

Opening activity is naturally high. Compare 09:31 with historical 09:31, not with
10:30. A gap-up without abnormal same-clock turnover is not volume ignition.

### Lunch reopen

13:01 often has a local turnover jump. Compare only with historical 13:01.

### Closing auction

15:00 can contain auction volume. Do not treat it as ordinary continuous-trading ignition.

### Locked upper limit

After a continuous lock, low turnover can mean scarce sellers. Do not downgrade the
signal using ordinary RS5 decay. Evaluate first touch, open-board events, reseal,
locked duration, and queue data.

### One-price upper limit

Volume-speed evidence may be weak because little stock traded. Label the limit state
and state that queue/order-book evidence is required.

### STAR, ChiNext, Beijing, ST, and new listings

Use quote-provided upper/lower limit prices. Price-limit percentages vary by board,
risk-warning status, and listing stage.

### Illiquid small caps

A small absolute order can create a huge RS value. Require turnover amount, spread,
turnover rate, and price efficiency checks; avoid ranking only by RS.

### High-volume stalling

If RS is high but price cannot advance, inspect location:

- low position and no decline: possible absorption
- prior high or upper resistance: possible distribution
- repeated failed highs with negative large-order flow: elevated failure risk

Do not label absorption or distribution definitively without order-flow support.

### Sell acceleration and panic exhaustion

High RS with falling price is sell acceleration. It becomes possible panic exhaustion
only after sell acceleration turns down, price stops making lows, and support appears.

### Corporate actions and abnormal reference prices

Ex-right dates, restructurings, resumptions, and new listings can invalidate ordinary
return and limit calculations. Report the event or mark data insufficient.

### Public endpoint baseline

The Eastmoney trends endpoint commonly supplies the current day plus four completed
sessions. This is enough for a provisional same-clock comparison but not a robust
20-session baseline. Explicitly lower confidence.

## 9. Invalidation

State an invalidation level, not a prediction. Use:

- ignition origin
- breakout level
- VWAP
- pullback low
- exchange lower limit when relevant

Typical invalidation:

```text
price falls below ignition origin and VWAP
AND turnover accelerates on the decline
AND large-order flow deteriorates
```

## 10. Confidence

Use:

- High: at least 20 baseline sessions, complete quote/flow/board data
- Medium: four or more baseline sessions and complete current data
- Low: fewer than four sessions, missing flow, missing board, stale timestamp, or
  ambiguous price-limit status

Never hide low confidence behind a precise score.
