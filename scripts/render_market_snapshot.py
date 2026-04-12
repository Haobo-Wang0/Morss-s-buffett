#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

ROOT = Path('/home/pi/.openclaw/workspace')
DATA = ROOT / 'out' / 'daily_market_data.json'
CN_FONT = FontProperties(fname='/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')

items = json.loads(DATA.read_text(encoding='utf-8'))
as_of = max(i['date'] for i in items)
OUT = ROOT / 'out' / f'daily_prices_{as_of}.png'


fig_h = max(6, 2.0 + len(items) * 1.65)
fig, ax = plt.subplots(figsize=(10, fig_h), dpi=180)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
fig.patch.set_facecolor('#0b1220')
ax.set_facecolor('#0b1220')


def fmt_price(v):
    return f'{float(v):.2f}'


def fmt_pct(v):
    if v is None:
        return ''
    return f"{v:+.2f}%"


ax.text(0.05, 0.95, '每日行情更新', fontsize=24, color='white', fontproperties=CN_FONT, va='top')
ax.text(0.05, 0.91, 'DAILY MARKET SNAPSHOT', fontsize=12, color='#94a3b8', va='top')
ax.text(0.95, 0.95, as_of, fontsize=14, color='#cbd5e1', ha='right', va='top')

n = len(items)
top_y = 0.80
bottom_y = 0.14 if n <= 4 else 0.10
step = (top_y - bottom_y) / max(n - 1, 1)
ys = [top_y - i * step for i in range(n)]

for item, y in zip(items, ys):
    ax.text(0.06, y + 0.035, item['name'], fontsize=20, color='#e2e8f0', va='center', fontproperties=CN_FONT)
    ax.text(0.06, y - 0.025, item['en'], fontsize=11, color='#64748b', va='center')
    ax.text(0.74, y, fmt_price(item['price']), fontsize=26, color='white', va='center', ha='right', weight='bold')
    pct = fmt_pct(item['pct'])
    color = '#22c55e' if pct.startswith('+') else ('#ef4444' if pct.startswith('-') else '#94a3b8')
    ax.text(0.93, y, pct, fontsize=16, color=color, va='center', ha='right', weight='bold')
    ax.plot([0.05, 0.95], [y - 0.09, y - 0.09], color='#1e293b', lw=1)

OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, bbox_inches='tight', facecolor=fig.get_facecolor())
print(OUT)
