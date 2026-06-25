# Chart Display Rules — E-commerce Skills v1.0

> **Shared standard for all visualization across e-commerce skills.**  
> In SKILL.md, reference: `Read: references/display-rules.md`

---

## ⛔ CRITICAL: Prevent Label Overlap (MANDATORY)

**This is the #1 chart quality rule. NEVER allow text to overlap.**

### Method 1: adjustText Library (Recommended)

```python
from adjustText import adjust_text  # pip install adjustText

texts = []
for i, (x, y, label) in enumerate(data_points):
    ax.scatter(x, y, s=size, c=color)
    texts.append(ax.text(x, y, label, fontsize=10))

# Auto-adjust label positions to avoid overlap
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
```

### Method 2: Numbered Labels + Legend

```python
for i, (x, y, label) in enumerate(data_points, 1):
    ax.scatter(x, y, s=size, c=color)
    ax.annotate(str(i), (x, y), fontsize=9, ha='center', va='bottom')

# Add legend outside plot
legend_text = '\n'.join([f'{i}. {label}' for i, label in enumerate(labels, 1)])
ax.text(1.02, 0.5, legend_text, transform=ax.transAxes, fontsize=9,
        verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat'))
```

---

## ⛔ CRITICAL: Prevent Data Point Overlap (Jitter)

When scatter plot points have identical coordinates, add jitter:

```python
from collections import defaultdict
import math

positions = defaultdict(list)
for item in data:
    key = (item['x'], item['y'])
    positions[key].append(item)

JITTER = 0.15  # Adjust based on axis scale

for (base_x, base_y), items in positions.items():
    n = len(items)
    for i, item in enumerate(items):
        if n == 1:
            x, y = base_x, base_y
        elif n == 2:
            # Diagonal offset for 2 points
            offsets = [(-JITTER, JITTER), (JITTER, -JITTER)]
            x = base_x + offsets[i][0]
            y = base_y + offsets[i][1]
        else:
            # Circular distribution for 3+ points
            angle = 2 * math.pi * i / n
            x = base_x + JITTER * math.cos(angle)
            y = base_y + JITTER * math.sin(angle)
        
        ax.scatter(x, y, s=size, c=color)
```

---

## Standard Styling Rules

### Colors

| Purpose | Color | Hex |
|---------|-------|-----|
| Highlight / Good / Opportunity | Green | `#4CAF50` |
| Primary / Neutral | Blue | `#2196F3` |
| Warning / Medium | Yellow/Orange | `#FFC107` / `#FF9800` |
| Danger / Poor | Red | `#EF5350` |
| Muted / Secondary | Gray | `#90A4AE` |
| Background boxes | Light Yellow | `#FFF9C4` |
| Success boxes | Light Green | `#E8F5E9` |
| Error boxes | Light Red | `#FFEBEE` |

**Platform Colors:**
- Amazon: `#FF9900` (orange)
- eBay: `#E53238` (red)
- Walmart: `#0071CE` (blue)

**⚠️ Avoid red-green combinations** — 8% of men are colorblind.

### Typography

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Title | 12pt | 13-14pt |
| Axis labels | 10pt | 11-12pt |
| Tick labels | 8pt | 9-10pt |
| Legend | 9pt | 10pt |
| Data labels | 9pt | 10-11pt |

### Axis Rules

```python
# Bar charts MUST start Y-axis at zero
ax.set_ylim(0, max_value * 1.2)

# Hide unnecessary spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
```

### Label Positioning

```python
# Labels above bars with proper offset
for bar, value in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, 
            bar.get_height() + max(values) * 0.02,  # 2% offset
            f'{value}', ha='center', va='bottom', 
            fontsize=11, fontweight='bold')
```

### Edge Styling

```python
# Clean edges on bars/scatter points
bars = ax.bar(x, y, color=colors, edgecolor='white', linewidth=2)
scatter = ax.scatter(x, y, c=colors, edgecolors='white', linewidth=2)
```

### Title Format (IBCS Standard)

```
[SUBJECT] - [MEASURE with units] - [TIME PERIOD]
```

Examples:
- `PRICE DISTRIBUTION: Cat Bed`
- `BSR TREND: B0XXXXXXXX - 180 Days`
- `MARKET SHARE - Revenue % - Q1 2026`

---

## Export Settings

| Use Case | Format | DPI | Settings |
|----------|--------|-----|----------|
| Discord / WhatsApp | PNG | 150 | `bbox_inches='tight', facecolor='white'` |
| Reports / Docs | PNG | 300 | `bbox_inches='tight', facecolor='white'` |
| Print | PDF/SVG | 300+ | Vector preferred |

### Standard Export Code

```python
plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
```

---

## Chart Selection Logic

### When to Use Charts

| Scenario | Charts | Why |
|----------|--------|-----|
| Quick question | **0** | Text answer suffices |
| Standard analysis | **1-2** | Most impactful only |
| Full report | **2-3** | Don't overdo it |

### When NOT to Use Charts

| Scenario | Do Instead |
|----------|------------|
| Simple numeric answer | Text: "Market is $850M" |
| Consumer quotes/insights | Text quotes are more compelling |
| Fragmented data (no pattern) | Skip - nothing meaningful to show |
| Similar values across categories | Skip - no interesting comparison |

---

## Chart Type Selection

| Data Type | Recommended Chart |
|-----------|-------------------|
| Trend over time | Line Chart |
| Category comparison | Horizontal Bar Chart |
| Part of whole (≤5 items) | Pie/Donut Chart |
| Part of whole (>5 items) | Horizontal Bar Chart |
| Two variables relationship | Scatter Plot |
| Multi-dimension comparison | Radar Chart |
| Distribution | Histogram or Bar Chart |

---

## Emoji Standards (for text output)

| Trend | Emoji |
|-------|-------|
| Rising (>10%) | 📈 |
| Stable (±10%) | ➡️ |
| Declining (<-10%) | 📉 |

| Competition/Risk | Emoji |
|------------------|-------|
| Low | 🟢 |
| Medium | 🟡 |
| High | 🔴 |

| Signal Strength | Emoji |
|-----------------|-------|
| Very strong | 🔥🔥🔥 |
| Strong | 🔥🔥 |
| Moderate | 🔥 |
| Weak | ⚠️ |

---

## Platform-Specific Formatting

### Plain-Text Output for Non-Markdown Channels

Some chat surfaces display raw Markdown characters instead of rendering them. Nexscope Webchat and similar embedded webchat environments must be treated as non-Markdown unless rendering is confirmed.

When CHANNEL_RENDERS_MARKDOWN is false or undefined, or when the current channel is an unknown webchat surface:

- Do not use Markdown syntax in the final answer.
- Avoid Markdown tables, headings, fenced code blocks, inline code, bold, italic, links, checkboxes, or Markdown bullet markers such as asterisk, hyphen, hash, or backtick.
- Do not interpret "bullet list" as Markdown bullets. Use plain lines with labels, numbers, spacing, and indentation only.
- Use manually aligned plain text for structured data.
- Keep chart/image exports unchanged; this rule applies to the text response around them.

Plain-text list example:

Summary
  Item 1: Demand is rising.
  Item 2: Competition is moderate.
  Item 3: Margin needs validation.

Plain-text nested list example:

Action Plan
  Step 1: Validate demand
    Check search trend
    Check BSR stability
  Step 2: Review competition
    Compare price bands
    Identify weak listings

Plain-text table example:

Metric          Current       Interpretation
=============   ==========    ==================
Search trend    Rising        Positive demand
Competition     Medium        Manageable
Margin          Unknown       Needs cost input

If a platform supports code blocks but not tables, a preformatted plain-text block is acceptable. If code block markers are displayed literally, remove the markers and send the aligned text directly.

### Structured Data Display in Plain Text

Plain text does not mean loose prose. In non-Markdown channels, keep every data-heavy answer structured with predictable blocks, spacing, labels, and aligned rows.

Use these formats by data type:

KPI / metric summary:

Market Snapshot
  Search volume      18,400 / month
  Average price      USD 24.99
  Review median      860
  Opportunity score  78 / 100

Ranking:

Top Opportunities
  1. Portable blender      Score 86    Demand high      Competition medium
  2. Mini food chopper     Score 79    Demand medium    Competition low
  3. Travel smoothie cup   Score 74    Demand medium    Competition medium

Comparison:

Competitor       Price      Rating      Reviews      Weakness
==============   =======    ========    =========    ==================
Brand A          24.99      4.6         1,240        Weak accessories
Brand B          21.99      4.4         860          Thin packaging
Brand C          29.99      4.7         2,100        High price

Score breakdown:

Score Breakdown
  Demand strength       28 / 35
  Competition gap       18 / 25
  Margin potential      16 / 20
  Differentiation       14 / 20
  Total                 76 / 100

Recommendation block:

Recommendation
  Priority      High
  Decision      Continue validation
  Reason        Demand is strong, but review count is high.
  Next step     Verify landed cost and margin before sourcing.

Formatting rules for plain-text data:

- Use section titles on their own line.
- Keep tables to 4 or 5 columns maximum.
- Put units in the label or header, not buried in prose.
- Align repeated rows with spaces.
- Use short cell values so rows do not wrap badly on narrow screens.
- If a table would be too wide, split it into multiple smaller blocks.
- Put the key interpretation immediately before or after the data block.
- Use N/A for missing values instead of leaving blank cells.
- Do not output raw JSON unless the user asks for raw machine-readable data.

### Discord / WhatsApp
- ❌ No markdown tables (won't render)
- ✅ Use code blocks or bullet lists only when they render correctly
- ✅ If Markdown list markers render as raw characters, switch to manually indented plain text
- ✅ Wrap multiple links in `<>` to suppress embeds

### Nexscope Webchat / Unknown Webchat
- ❌ Do not assume Markdown renders
- ❌ Do not use Markdown tables, Markdown bullets, headings, bold, inline code, or fenced code blocks unless rendering has been confirmed
- ✅ Use plain-text labels, indentation, spacing, and manually aligned rows
- ✅ Treat CHANNEL_RENDERS_MARKDOWN=false or undefined as plain-text mode

### Telegram / Slack
- ✅ Tables render correctly
- ✅ Standard markdown works

---

## Validation Checklist

Before sending any chart:

- [ ] Labels do not overlap with data points or each other
- [ ] Data points with same coordinates are jittered
- [ ] Bar charts start Y-axis at zero
- [ ] All axes labeled with units
- [ ] Legend does not overlap data area
- [ ] Colorblind-safe palette used
- [ ] Font sizes ≥ minimum requirements
- [ ] Title follows IBCS format
- [ ] Export at 150+ DPI for messaging platforms
- [ ] `bbox_inches='tight'` used to avoid cutoff
