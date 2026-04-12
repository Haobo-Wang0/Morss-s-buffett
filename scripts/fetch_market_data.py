#!/usr/bin/env python3
import json
import time
from pathlib import Path

import akshare as ak

ROOT = Path('/home/pi/.openclaw/workspace')
OUT = ROOT / 'out' / 'daily_market_data.json'


def to_float(v):
    return float(v)


def safe_pct(new, old):
    if old in (None, 0):
        return None
    return (new / old - 1) * 100


def trend_label(series):
    if len(series) < 2:
        return '数据不足'
    first = float(series[0])
    last = float(series[-1])
    change = safe_pct(last, first)
    if change is None:
        return '数据不足'
    if change >= 3:
        return '明显上行'
    if change >= 1:
        return '偏强上行'
    if change <= -3:
        return '明显走弱'
    if change <= -1:
        return '偏弱回落'
    return '震荡'


def with_retry(fetcher, label, retries=3, sleep_seconds=2):
    last_err = None
    for i in range(retries):
        try:
            return fetcher()
        except Exception as e:
            last_err = e
            if i < retries - 1:
                time.sleep(sleep_seconds)
    raise RuntimeError(f'{label} 获取失败: {last_err}')


def get_a_share_stock(symbol, name, en):
    def _fetch():
        df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')
        last5 = df.tail(5).reset_index(drop=True)
        row = last5.iloc[-1]
        prev = last5.iloc[-2] if len(last5) >= 2 else None
        close = to_float(row['收盘'])
        prev_close = to_float(prev['收盘']) if prev is not None else None
        return {
            'name': name,
            'en': en,
            'symbol': symbol,
            'date': str(row['日期'])[:10],
            'price': close,
            'change': close - prev_close if prev_close is not None else None,
            'pct': to_float(row['涨跌幅']),
            'open': to_float(row['开盘']),
            'high': to_float(row['最高']),
            'low': to_float(row['最低']),
            'history_dates': [str(x)[:10] for x in last5['日期'].tolist()],
            'history_prices': [to_float(x) for x in last5['收盘'].tolist()],
            'trend_3d_pct': safe_pct(to_float(last5.iloc[-1]['收盘']), to_float(last5.iloc[-3]['收盘'])) if len(last5) >= 3 else None,
            'trend_5d_pct': safe_pct(to_float(last5.iloc[-1]['收盘']), to_float(last5.iloc[0]['收盘'])) if len(last5) >= 5 else None,
            'trend_3d_label': trend_label(last5.tail(3)['收盘'].tolist()) if len(last5) >= 3 else '数据不足',
            'trend_5d_label': trend_label(last5['收盘'].tolist()),
            'source_note': 'A股前复权日线',
        }
    return with_retry(_fetch, name)


def get_wuxi():
    return get_a_share_stock('603259', '药明康德', 'WUXI APPTEC')


def get_deye():
    return get_a_share_stock('605117', '德业股份', 'DEYE')


def get_gold():
    def _fetch():
        df = ak.spot_hist_sge(symbol='Au99.99')
        last5 = df.tail(5).reset_index(drop=True)
        row = last5.iloc[-1]
        prev = last5.iloc[-2] if len(last5) >= 2 else None
        close = to_float(row['close'])
        prev_close = to_float(prev['close']) if prev is not None else None
        return {
            'name': '黄金(Au99.99)',
            'en': 'SPOT GOLD',
            'date': str(row['date'])[:10],
            'price': close,
            'change': close - prev_close if prev_close is not None else None,
            'pct': safe_pct(close, prev_close),
            'open': to_float(row['open']) if 'open' in row else close,
            'high': to_float(row['high']) if 'high' in row else close,
            'low': to_float(row['low']) if 'low' in row else close,
            'history_dates': [str(x)[:10] for x in last5['date'].tolist()],
            'history_prices': [to_float(x) for x in last5['close'].tolist()],
            'trend_3d_pct': safe_pct(to_float(last5.iloc[-1]['close']), to_float(last5.iloc[-3]['close'])) if len(last5) >= 3 else None,
            'trend_5d_pct': safe_pct(to_float(last5.iloc[-1]['close']), to_float(last5.iloc[0]['close'])) if len(last5) >= 5 else None,
            'trend_3d_label': trend_label(last5.tail(3)['close'].tolist()) if len(last5) >= 3 else '数据不足',
            'trend_5d_label': trend_label(last5['close'].tolist()),
            'source_note': '上金所现货',
        }
    return with_retry(_fetch, '黄金')


def get_brent():
    def _fetch():
        df = ak.futures_foreign_hist(symbol='OIL')
        last5 = df.tail(5).reset_index(drop=True)
        row = last5.iloc[-1]
        prev = last5.iloc[-2] if len(last5) >= 2 else None
        close = to_float(row['close'])
        prev_close = to_float(prev['close']) if prev is not None else None
        return {
            'name': '布伦特原油连续',
            'en': 'BRENT OIL',
            'date': str(row['date'])[:10],
            'price': close,
            'change': close - prev_close if prev_close is not None else None,
            'pct': safe_pct(close, prev_close),
            'open': to_float(row['open']) if 'open' in row else close,
            'high': to_float(row['high']) if 'high' in row else close,
            'low': to_float(row['low']) if 'low' in row else close,
            'history_dates': [str(x)[:10] for x in last5['date'].tolist()],
            'history_prices': [to_float(x) for x in last5['close'].tolist()],
            'trend_3d_pct': safe_pct(to_float(last5.iloc[-1]['close']), to_float(last5.iloc[-3]['close'])) if len(last5) >= 3 else None,
            'trend_5d_pct': safe_pct(to_float(last5.iloc[-1]['close']), to_float(last5.iloc[0]['close'])) if len(last5) >= 5 else None,
            'trend_3d_label': trend_label(last5.tail(3)['close'].tolist()) if len(last5) >= 3 else '数据不足',
            'trend_5d_label': trend_label(last5['close'].tolist()),
            'source_note': '海外期货连续',
        }
    return with_retry(_fetch, '布伦特原油')


def main():
    items = [get_wuxi(), get_deye(), get_gold(), get_brent()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    print(OUT)


if __name__ == '__main__':
    main()
