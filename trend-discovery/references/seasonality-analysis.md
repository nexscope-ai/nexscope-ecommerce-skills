# Seasonality Analysis — Trend Discovery v2.0

## Seasonality Index Calculation

```python
def calculate_seasonality(monthly_volumes):
    peak = max(monthly_volumes)
    trough = min(monthly_volumes)
    if trough == 0:
        return float('inf')
    return peak / trough
```

## Classification

| Index | Level | Meaning |
|-------|-------|---------|
| > 3.0 | 🔴 Extreme | Very seasonal (e.g., Halloween) |
| 2.0 - 3.0 | 🟠 Strong | Significant peaks (e.g., outdoor) |
| 1.5 - 2.0 | 🟡 Moderate | Some seasonality |
| < 1.5 | 🟢 Weak | Year-round demand |

## Peak Detection

```python
def detect_peak_months(monthly_volumes):
    avg = sum(monthly_volumes) / len(monthly_volumes)
    peaks = []
    for i, vol in enumerate(monthly_volumes):
        if vol > avg * 1.5:
            month = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'][i]
            peaks.append(month)
    return peaks
```

## Output Format

```markdown
### Seasonality
- Index: 2.3x (🟠 Strong)
- Peak months: Nov, Dec
- Trough: Feb
- Strategy: Stock up in Oct for Q4
```
