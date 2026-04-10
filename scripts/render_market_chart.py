#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

ROOT = Path('/home/pi/.openclaw/workspace')
DATA = ROOT / 'out' / 'daily_market_data.json'
OUT = ROOT / 'out' / 'daily_market_chart.png'
CN_FONT = FontProperties(fname='/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')

items = json.loads(DATA.read_text(encoding='utf-8'))
as_of = max(i['date'] for i in items)
series = [
    ('药明康德', '#ef4444'),
    ('黄金', '#eab308'),
    ('布伦特原油', '#22c55e'),
]
name_lookup = {
    '药明康德': '药明康德',
    '黄金': '黄金(Au99.99)',
    '布伦特原油': '布伦特原油连续',
}
item_map = {i['name']: i for i in items}

plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(13, 8), dpi=180, facecolor='#0b1220')
ax = fig.add_axes([0.07, 0.26, 0.88, 0.56])
ax.set_facecolor('#111827')
for spine in ax.spines.values():
    spine.set_color('#334155')
ax.tick_params(colors='#94a3b8', labelsize=10)
ax.grid(True, color='#1f2937', linestyle='--', linewidth=0.8, alpha=0.8)

x = list(range(5))
labels = ['D-4', 'D-3', 'D-2', 'D-1', 'Today']
ax.set_xticks(x)
ax.set_xticklabels(labels, color='#94a3b8')

all_vals = []
for label, color in series:
    item = item_map[name_lookup[label]]
    vals = [float(v) for v in item['history_prices']]
    all_vals.extend(vals)
    ax.plot(x[:len(vals)], vals, color=color, linewidth=3, marker='o', markersize=5, label=label)

if all_vals:
    ymin = min(all_vals)
    ymax = max(all_vals)
    pad = (ymax - ymin) * 0.12 if ymax > ymin else max(1, ymax * 0.05)
    ax.set_ylim(ymin - pad, ymax + pad)

legend = ax.legend(loc='upper left', frameon=False, prop=CN_FONT)
for text in legend.get_texts():
    text.set_color('#e5e7eb')
    text.set_fontproperties(CN_FONT)

fig.text(0.07, 0.92, '每日市场图', fontsize=26, color='white', fontproperties=CN_FONT)
fig.text(0.07, 0.875, 'DAILY MARKET CHART · 5D TREND', fontsize=12, color='#94a3b8')
fig.text(0.95, 0.92, as_of, fontsize=14, color='#cbd5e1', ha='right')

cards_y = [0.17, 0.11, 0.05]
for (label, color), y in zip(series, cards_y):
    item = item_map[name_lookup[label]]
    pct = item.get('pct')
    pct_text = '' if pct is None else f'{pct:+.2f}%'
    trend3 = item.get('trend_3d_pct')
    trend5 = item.get('trend_5d_pct')
    trend3_text = 'NA' if trend3 is None else f'{trend3:+.2f}%'
    trend5_text = 'NA' if trend5 is None else f'{trend5:+.2f}%'
    fig.text(0.08, y, '●', color=color, fontsize=18)
    fig.text(0.097, y, f' {label}', color='#e5e7eb', fontsize=14, fontproperties=CN_FONT)
    fig.text(0.44, y, f"Price {float(item['price']):.2f}", color='white', fontsize=14)
    fig.text(0.60, y, f"Day {pct_text}", color='#cbd5e1', fontsize=12)
    fig.text(0.74, y, f"3D {trend3_text}", color='#93c5fd', fontsize=12)
    fig.text(0.86, y, f"5D {trend5_text}", color='#fca5a5', fontsize=12)

OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, bbox_inches='tight', facecolor=fig.get_facecolor())
print(OUT)
