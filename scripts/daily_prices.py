#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

ROOT = Path('/home/pi/.openclaw/workspace')
DATA = ROOT / 'out' / 'daily_market_data.json'


def fmt_price(v):
    return f"{float(v):.2f}"


def fmt_pct(v):
    if v is None:
        return 'NA'
    return f"{float(v):+.2f}%"


def fmt_delta(v):
    if v is None:
        return 'NA'
    return f"{float(v):+.2f}"


def stance(item):
    p = item.get('pct') or 0
    t3 = item.get('trend_3d_pct') or 0
    t5 = item.get('trend_5d_pct') or 0
    score = p * 0.4 + t3 * 0.8 + t5 * 1.0
    if score >= 3:
        return '一句话结论：偏多，趋势占优，但别追高。'
    if score <= -3:
        return '一句话结论：偏空，先看止跌，不急着上仓位。'
    return '一句话结论：先观望，等更明确的方向。'


def advice(item):
    p = item.get('pct')
    t5 = item.get('trend_5d_pct')
    name = item['name']

    if name.startswith('药明康德'):
        if (t5 or 0) > 3 and (p or 0) >= 0:
            return '建议：中短线偏强，已有仓位可继续拿，但不建议在单日冲高时重仓追入。'
        if (t5 or 0) < -3:
            return '建议：整体仍偏弱，先看企稳再考虑加仓，控制回撤更重要。'
        return '建议：区间震荡看待，重点看成交量和医药板块情绪是否继续修复。'

    if name.startswith('黄金'):
        if (t5 or 0) > 2:
            return '建议：趋势仍强，更适合配置型持有；短线不宜在连续拉升后激进加码。'
        if (p or 0) < -1:
            return '建议：若只是回调，可等支撑确认后分批处理。'
        return '建议：维持偏强震荡思路，以仓位管理优先。'

    if (t5 or 0) > 3:
        return '建议：油价阶段偏强，关注能源链机会，同时警惕高位波动放大。'
    if (t5 or 0) < -3:
        return '建议：油价走弱，先观察需求和库存预期是否继续恶化。'
    return '建议：短线震荡，等待更明确的宏观驱动再动作。'


def main():
    items = json.loads(DATA.read_text(encoding='utf-8'))
    as_of = max(i['date'] for i in items)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [f"每日价格追踪（数据日期 {as_of}｜生成时间 {now}）"]
    for item in items:
        lines.append(
            f"\n【{item['name']}】\n"
            f"- 最新价：{fmt_price(item['price'])}\n"
            f"- 日变动：{fmt_delta(item.get('change'))}\n"
            f"- 当日涨跌幅：{fmt_pct(item.get('pct'))}\n"
            f"- 开/高/低：{fmt_price(item['open'])} / {fmt_price(item['high'])} / {fmt_price(item['low'])}\n"
            f"- 3日趋势：{item.get('trend_3d_label', '数据不足')}（{fmt_pct(item.get('trend_3d_pct'))}）\n"
            f"- 5日趋势：{item.get('trend_5d_label', '数据不足')}（{fmt_pct(item.get('trend_5d_pct'))}）\n"
            f"- {stance(item)}\n"
            f"- 数据口径：{item['source_note']}\n"
            f"- {advice(item)}"
        )
    lines.append('\n附：会同步生成一张 5 日趋势图。以上为观察性建议，不构成投资建议。')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
