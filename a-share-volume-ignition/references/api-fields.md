# Eastmoney Web Endpoint Notes

These are public web-frontend endpoints, not a contracted data service. They can be
rate-limited, disconnected, delayed, or changed without notice.

## Minute Trends

```text
https://push2his.eastmoney.com/api/qt/stock/trends2/get
```

Typical parameters:

```text
secid=0.300059
ndays=5
fields1=f1,...,f13
fields2=f51,f52,f53,f54,f55,f56,f57,f58
```

Trend row mapping:

```text
timestamp, minute open, minute close, minute high, minute low,
volume in lots, turnover amount in yuan, cumulative VWAP
```

The `ndays=5` response normally includes the current session and four completed sessions.

## Quote Snapshot

```text
https://push2.eastmoney.com/api/qt/stock/get
```

Common fields:

```text
f43 latest price (usually scaled by 100)
f44 high
f45 low
f46 open
f47 cumulative volume
f48 cumulative turnover amount in yuan
f50 volume ratio (usually scaled by 100)
f51 upper limit price
f52 lower limit price
f57 code
f58 name
f60 previous close
f71 VWAP
f116 total market capitalization
f117 float market capitalization
f127 industry label
f129 concept labels
f135 main inflow
f136 main outflow
f137 main net flow
f138 super-large inflow
f139 super-large outflow
f140 super-large net flow
f141 large inflow
f142 large outflow
f143 large net flow
f144 medium inflow
f145 medium outflow
f146 medium net flow
f147 small inflow
f148 small outflow
f149 small net flow
f168 turnover rate (usually scaled by 100)
f169 absolute price change
f170 percentage change (usually scaled by 100)
```

Validate scaling against visible prices. Do not assume every endpoint uses identical scaling.

## Minute Capital Flow

```text
https://push2.eastmoney.com/api/qt/stock/fflow/kline/get
```

Typical parameters:

```text
klt=1
secid=0.300059
fields2=f51,f52,f53,f54,f55,f56
```

Row mapping:

```text
timestamp, cumulative main net, cumulative small net, cumulative medium net,
cumulative large net, cumulative super-large net
```

Main net is generally large plus super-large net. All size buckets net to approximately
zero because every trade has a buyer and seller.

## Board Constituents

```text
https://push2.eastmoney.com/api/qt/clist/get
```

Use:

```text
fs=b:BK0473
fields=f2,f3,f6,f12,f14
```

Fields:

```text
f2 latest price
f3 percentage change
f6 turnover amount
f12 code
f14 name
```

Compute breadth as positive constituents divided by total constituents. Median return is
usually more robust than turnover-weighted return when one constituent has an exceptional move.

## Symbol and Board IDs

Common stock IDs:

```text
0.300059  Shenzhen/ChiNext style
1.600030  Shanghai style
90.BK0473 Eastmoney board style
```

When the user supplies only a name, use Eastmoney suggestion search or another reliable
symbol directory, then confirm the returned name before analysis.

## Failure Handling

- Retry a bounded number of times with a short increasing delay.
- Split quote, trend, flow, and board calls when rate-limited.
- If minute flow fails, continue with turnover and price but lower confidence.
- If minute trends fail, do not infer ignition from a daily quote alone.
- Always expose the latest successful timestamp.
