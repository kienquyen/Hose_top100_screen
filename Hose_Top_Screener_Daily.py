import requests
import pandas as pd
import ta
import numpy as np
import os
import time
from datetime import datetime, timedelta, timezone
import pytz
from vnstock_data import Listing, Quote

VN100_SYMBOLS = [
    "AAA", "ACB", "AGG", "ANV", "ASM", "BCG", "BCM", "BID", "BMP", "BVH",
    "BWE", "CII", "CMG", "CRE", "CTD", "CTG", "CTR", "DBC", "DCM", "DGC",
    "DGW", "DHC", "DIG", "DPM", "DXG", "DXS", "EIB", "FPT", "FRT", "FTS",
    "GAS", "GEG", "GEX", "GMD", "GVR", "HCM", "HDB", "HDC", "HDG", "HHV",
    "HPG", "HSG", "HT1", "IMP", "KBC", "KDC", "KDH", "KOS", "LPB", "MBB",
    "MSB", "MSN", "MWG", "NKG", "NLG", "ACV", "NVL", "OCB", "PAN", "PC1",
    "PDR", "PHR", "PLX", "PNJ", "POW", "PPC", "PTB", "PVD", "PVT", "QNS",
    "REE", "SAB", "SAM", "SBT", "SCR", "SCS", "SHB", "SJS", "SSB", "SSI", "STB",
    "SZC", "TCB", "TCH", "TMS", "TPB", "VCB", "VCG", "VCI", "VHC", "VHM",
    "VIB", "VIC", "VIX", "VJC", "VND", "VNM", "VPB", "VPI", "VRE", "VSH",
    "VIX","VSC",
]

# === CONFIGURATION ===
TIMEFRAME = '1D'  # Fixed timeframe for VN Stocks
DAILY_RUN_HOUR = 5  # 🕘 Change this to configure the run time (0–23)
webhook_url = os.getenv("webhook_url")


# === DISCORD NOTIFICATION ===
def send_discord(message, webhook_url):
    max_length = 2000
    parts = [message[i:i + max_length] for i in range(0, len(message), max_length)]

    for idx, part in enumerate(parts):
        payload = {"content": part}
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code not in [200, 204]:
                print(f"❌ Failed to send part {idx + 1}: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Exception while sending part {idx + 1}: {e}")

#DICORD SEND IMAGE
def send_chart_to_discord(image_path, webhook_url, message="📊 Signal Chart"):
    try:
        with open(image_path, 'rb') as f:
            file_data = {'file': (os.path.basename(image_path), f, 'image/png')}
            payload = {
                'content': message,
                'username': 'SignalBot'
            }

            response = requests.post(webhook_url, data=payload, files=file_data)

            if response.status_code in [200, 204]:
                print("✅ Image sent to Discord successfully.")
            else:
                print(f"❌ Discord upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception while sending image to Discord: {e}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
            print("🗑️ Deleted temporary file.")

# FORMAT TABLE RESULT
def format_signal_table_for_discord(results):
    if not results:
        return "🔍 Không có tín hiệu BUY1, BUY2, BUY3 trong ngày này."

    df = pd.DataFrame(results)
    df = df[['symbol', 'exchange', 'entry_price', 'rsi', 'rsi2', 'mfi', 'ema9', 'signal_type']]
    df = df.sort_values(by='signal_type')

    msg = "📊 **Tín hiệu mua trong ngày**:\n```\n"
    msg += f"{'Symbol':<8} {'Exch':<6} {'Price':<8} {'RSI':<6} {'RSI2':<6} {'MFI':<6} {'EMA9':<6} {'Signal':<6}\n"
    msg += "-" * 60 + "\n"
    for _, row in df.iterrows():
        msg += f"{row['symbol']:<8} {row['exchange']:<6} {row['entry_price']:<8.2f} {row['rsi']:<6.1f} {row['rsi2']:<6.1f} {row['mfi']:<6.1f} {row['ema9']:<6.1f} {row['signal_type']:<6}\n"
    msg += "```"
    return msg
#===GET TOP 100 HOSE
def fetch_top_vn100_data():
    listing = Listing()
    df_listing = listing.all_symbols()

    df_listing = df_listing[df_listing['symbol'].isin(VN100_SYMBOLS)]

    data = []
    for _, row in df_listing.iterrows():
        symbol = row['symbol']
        exchange = 'HOSE'  # cố định vì chỉ lấy từ VN100 HOSE

        try:
            quote = Quote(symbol=symbol, source='VCI')
            df = quote.intraday(page_size=1)
            if not df.empty:
                volume = df['volume'].iloc[-1]
                data.append({'symbol': symbol, 'volume': volume, 'exchange': exchange})
            time.sleep(0.1)
        except Exception:
            continue

    df_volume = pd.DataFrame(data)
    df_top = df_volume.sort_values(by='volume', ascending=False).head(100)

    symbol_data = {}
    for _, row in df_top.iterrows():
        symbol = row['symbol']
        exchange = row['exchange']
        try:
            quote = Quote(symbol=symbol, source='VCI')
            df_hist = quote.history(start='2024-01-01', interval='1D')
            if not df_hist.empty:
                symbol_data[symbol] = {
                    'df': df_hist,
                    'exchange': exchange
                }
            time.sleep(0.1)
        except Exception:
            continue

    return symbol_data


# === FETCH VNINDEX PRICE ===
def get_vnindex_latest():
    try:
        quote = Quote(symbol='VNINDEX', source='VCI')
        df = quote.history(start='2025-01-01', interval='1D')
        return df['close'].iloc[-1]
    except:
        return None
    
vnindex_close = get_vnindex_latest()
print(f"Latest VNINDEX close: {vnindex_close}")

# === COMPUTE HEIKIN-ASHI TREND ===
def apply_custom_ma(series, ma_type='EMA', length=9, alma_offset=0.85, alma_sigma=6):
    if ma_type == 'EMA':
        return ta.trend.ema_indicator(series, window=length)
    elif ma_type == 'SMA':
        return ta.trend.sma_indicator(series, window=length)
    elif ma_type == 'WMA':
        return ta.trend.wma_indicator(series, window=length)
    elif ma_type == 'VWMA':
        return (series * series).rolling(length).sum() / series.rolling(length).sum()
    elif ma_type == 'ZLEMA':
        lag = int((length - 1) / 2)
        zlema_input = series + (series - series.shift(lag))
        return ta.trend.ema_indicator(zlema_input, window=length)
    elif ma_type == 'HMA':
        half = int(length / 2)
        sqrt = int(np.sqrt(length))
        wma1 = ta.trend.wma_indicator(series, window=half)
        wma2 = ta.trend.wma_indicator(series, window=length)
        diff = 2 * wma1 - wma2
        return ta.trend.wma_indicator(diff, window=sqrt)
    elif ma_type == 'ALMA':
        weights = np.exp(-((np.arange(length) - alma_offset * (length - 1)) ** 2) / (2 * alma_sigma ** 2))
        weights /= weights.sum()
        return series.rolling(length).apply(lambda x: np.dot(x, weights), raw=True)
    elif ma_type == 'SWMA':
        return series.rolling(length).mean()
    else:
        return ta.trend.ema_indicator(series, window=length)

def compute_trend(df, ma_type='EMA', ma_period=9, alma_offset=0.85, alma_sigma=6):
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = df['close'].shift(1)
    ha_high = df[['high', 'open', 'close']].max(axis=1)
    ha_low = df[['low', 'open', 'close']].min(axis=1)

    ma_ha_close = apply_custom_ma(ha_close, ma_type, ma_period, alma_offset, alma_sigma)
    ma_ha_open = apply_custom_ma(ha_open, ma_type, ma_period, alma_offset, alma_sigma)
    ma_ha_high = apply_custom_ma(ha_high, ma_type, ma_period, alma_offset, alma_sigma)
    ma_ha_low = apply_custom_ma(ha_low, ma_type, ma_period, alma_offset, alma_sigma)

    trend = 100 * (ma_ha_close - ma_ha_open) / (ma_ha_high - ma_ha_low).replace(0, np.nan)
    return trend
#DETECT FATIGUE TREND
def detect_trend_fatigue(df, ema_length=9, lookback=30, flat_threshold_pct=0.4):
    """
    Adds an 'is_fatigue' column to df that marks True if the trend shows fatigue
    based on mean deviation of EMA.

    Parameters:
        df: pd.DataFrame - must contain a 'close' column.
        ema_length: int - the EMA length to use (default: 9)
        lookback: int - the lookback period to compare deviation
        flat_threshold_pct: float - mean deviation threshold (%) for fatigue
    """
    if 'close' not in df.columns:
        raise ValueError("DataFrame must contain 'close' column.")

    df['ema9'] = ta.trend.ema_indicator(df['close'], window=ema_length)

    # Initialize fatigue column
    df['is_fatigue'] = False

    for i in range(lookback, len(df)):
        ema_check = df.iloc[i - lookback]['ema9']
        ema_window = df.iloc[i - lookback + 1:i + 1]['ema9']
        diff_pct = (ema_window - ema_check).abs() / ema_check * 100
        mean_diff_pct = diff_pct.mean()

        df.at[i, 'is_fatigue'] = mean_diff_pct < flat_threshold_pct

    return df

# === SIGNALS ===
def is_buy1_signal(df: pd.DataFrame) -> bool:
    if df.shape[0] < 60:
        return False
    df = df.iloc[:-1].copy()
    #EMA
    df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['ema26'] = ta.trend.ema_indicator(df['close'], window=26)

    # RSI 
    LOOKBACK = 14  # or adjust to your desired value

    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['average_close'] = df['close'].rolling(window=LOOKBACK).mean()
    df['average_rsi'] = df['rsi'].rolling(window=LOOKBACK).mean()
    df['rsi_bull_divergence'] = (df['close'] <= df['average_close']) & (df['rsi'] > df['average_rsi'])
    df['rsi_bear_divergence'] = (df['close'] >= df['average_close']) & (df['rsi'] < df['average_rsi'])

    df['rsi_superoverbought'] = df['rsi'].rolling(18).max() >= 85

    #Money Flow index
    
    df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'], window=14)
    df['average_mfi'] = df['mfi'].rolling(window=LOOKBACK).mean()
    df['mfi_bull_divergence'] = (df['close'] <= df['average_close']) & (df['mfi'] > df['average_mfi'])
    df['mfi_bear_divergence'] = (df['close'] >= df['average_close']) & (df['mfi'] < df['average_mfi'])

    #Heikin Ashi Trend 
    df['trend'] = compute_trend(df)
    df['trend_prev'] = df['trend'].shift(1)
    df['trend_prev2'] = df['trend'].shift(2)
    
    #ADX
    df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    
    #Ichimoku
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    tenkan = (high_9 + low_9) / 2
    kijun = (high_26 + low_26) / 2
    df['kumo_a'] = ((tenkan + kijun) / 2).shift(25)
    
    #Supertrend
    atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=10)
    basic_upperband = (df['high'] + df['low']) / 2 + 3 * atr
    basic_lowerband = (df['high'] + df['low']) / 2 - 3 * atr
    supertrend_direction = np.where(df['close'] > basic_lowerband, 1, -1)
    df['supertrend_dir'] = pd.Series(supertrend_direction).astype(int)
    df['supertrend_change'] = df['supertrend_dir'].diff()
    last_bearish_switch_index = df[df['supertrend_change'] == 2].index.max()
    bearish_switch_not_recent = (df.index[-1] - last_bearish_switch_index) > 9 if last_bearish_switch_index is not None else True
    #Fatigue trend
    df = detect_trend_fatigue(df)
    #Remove not yet closed bar
    latest = df.iloc[-1]
    prev1 = df.iloc[-2]
    prev2 = df.iloc[-3]
    #KQ rule
    kqrsimf = (latest['rsi'] > latest['mfi']) and latest['mfi'] < 55

    return (
        latest['close'] >= latest['ema9'] and
        latest['trend'] > 0 and
        prev1['trend'] > 0 and
        prev2['trend'] <= 0 and
        latest['close'] > latest['kumo_a'] and
        latest['adx'] > 13 and
        latest['mfi'] <85 and
        latest['rsi'] <= 70 and
        bearish_switch_not_recent and
        not latest['rsi_bear_divergence'] and
        not latest['mfi_bear_divergence'] and
        not latest['rsi_superoverbought'] and
        not latest['is_fatigue'] and 
        not kqrsimf
    )

def is_buy2_signal(df, lookback=26):
    if df.shape[0] < lookback + 1:
        return False
    df = df.iloc[:-1].copy()
    df['rsi2'] = ta.momentum.rsi(df['close'], window=2)
    df['rsi14'] = ta.momentum.rsi(df['close'], window=14)
    df['lowest_close'] = df['close'].rolling(window=lookback).min()
    df['lowest_rsi14'] = df['rsi14'].rolling(window=lookback).min()
    if df[['rsi2', 'rsi14', 'lowest_close', 'lowest_rsi14']].iloc[-1].isnull().any():
        return False
    latest = df.iloc[-1]
    return (
        latest['close'] <= latest['lowest_close'] and
        latest['rsi14'] > latest['lowest_rsi14'] and
        latest['lowest_rsi14'] <= 30 and
        latest['rsi2'] < 20 and
        latest['rsi14'] < 33
    )

def is_buy3_signal(df: pd.DataFrame) -> bool:
    if df.shape[0] < 15:
        return False
    df = df.iloc[:-1].copy()
    df['rsi2'] = ta.momentum.rsi(df['close'], window=2)
    df['rsi14'] = ta.momentum.rsi(df['close'], window=14)
    df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'], window=14)
    if df[['rsi2', 'rsi14', 'mfi']].iloc[-1].isnull().any():
        return False
    latest = df.iloc[-1]
    return (
        latest['rsi2'] <= 4 and
        latest['rsi14'] < 25 and
        latest['mfi'] < 20
    )

def generate_signal_table(results):
    """
    Print a table with signal data: symbol, exchange, rsi, rsi2, mfi, ema9.
    """
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        print("\n📋 Buy Signal Table:")
        print(df_results.to_string(index=False))
    else:
        print("No BUY signals detected for the given date range.")


# === MAIN SCANNER ===
def run_screener_latest():
    today = pd.Timestamp.today().normalize()
    selected_date = today
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    print(f"📈 Running screener for {selected_date_str}")

    vnindex_price = get_vnindex_latest()
    if vnindex_price:
        print(f"📈 VNINDEX Latest Close: {vnindex_price:,.2f} VND")
    else:
        print("⚠️ Failed to fetch VNINDEX price.")

    symbol_data_map = fetch_top_vn100_data()

    print(f"\n🗕️ Screener for {selected_date_str}")
    found_signal = False
    results = []

    for symbol, data in symbol_data_map.items():
        try:
            df = data['df']
            exchange = data['exchange'].upper()

            df['time'] = pd.to_datetime(df['time'])
            df_filtered = df[df['time'] <= selected_date].copy()

            if df_filtered.shape[0] < 60:
                continue

            df_filtered = df_filtered.reset_index(drop=True)

 # Compute indicators before accessing
            df_filtered['ema9'] = ta.trend.ema_indicator(df_filtered['close'], window=9)
            df_filtered['rsi'] = ta.momentum.rsi(df_filtered['close'], window=14)
            df_filtered['rsi2'] = ta.momentum.rsi(df_filtered['close'], window=2)
            df_filtered['mfi'] = ta.volume.money_flow_index(
                df_filtered['high'],
                df_filtered['low'],
                df_filtered['close'],
                df_filtered['volume'],
                window=14
            )

            latest = df_filtered.iloc[-1]
            entry_price = df_filtered.iloc[-2]['close'] if df_filtered.shape[0] >= 2 else None

            buy1 = is_buy1_signal(df_filtered)
            buy2 = is_buy2_signal(df_filtered)
            buy3 = is_buy3_signal(df_filtered)

            if buy1:
                print(f"✅ BUY1 | {symbol} ({exchange}) | Entry: {entry_price:,.2f} VND")
                results.append({
                    "symbol": symbol,
                    "exchange": exchange,
                    "rsi": round(latest['rsi'], 1),
                    "rsi2": round(latest['rsi2'], 1),
                    "mfi": round(latest['mfi'], 1),
                    "ema9": round(latest['ema9'], 1),
                    "entry_price": round(entry_price, 1),
                    "signal_type": "BUY1"
                })
                found_signal = True

            if buy2:
                print(f"✅ BUY2 | {symbol} ({exchange}) | Entry: {entry_price:,.2f} VND")
                results.append({
                    "symbol": symbol,
                    "exchange": exchange,
                    "rsi": round(latest['rsi'], 1),
                    "rsi2": round(latest['rsi2'], 1),
                    "mfi": round(latest['mfi'], 1),
                    "ema9": round(latest['ema9'], 1),
                    "entry_price": round(entry_price, 1),
                    "signal_type": "BUY2"
                })
                found_signal = True

            if buy3:
                print(f"✅ BUY3 | {symbol} ({exchange}) | Entry: {entry_price:,.2f} VND")
                results.append({
                    "symbol": symbol,
                    "exchange": exchange,
                    "rsi": round(latest['rsi'], 1),
                    "rsi2": round(latest['rsi2'], 1),
                    "mfi": round(latest['mfi'], 1),
                    "ema9": round(latest['ema9'], 1),
                    "entry_price": round(entry_price, 1),
                    "signal_type": "BUY3"
                })
                found_signal = True

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")

    if not found_signal:
        print("🔍 Không có tín hiệu BUY1, BUY2, BUY3 trong ngày này.")

    generate_signal_table(results)
    if results:
        header = f"📅 Signal Date: {selected_date_str}"
        discord_msg = f"{header}\n\n{format_signal_table_for_discord(results)}"
    else:
        discord_msg = f"📅 {selected_date_str}: Không có tín hiệu BUY1, BUY2, BUY3."

    send_discord(discord_msg, webhook_url)

# Ensure this helper is available in your script
# def generate_signal_table(results): ... (from earlier step)
# === DAILY SCHEDULER ===
# === DAILY SCHEDULER ===
def wait_until_next_run(hour=DAILY_RUN_HOUR):
    vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(vietnam_tz)

    next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)

    wait_seconds = (next_run - now).total_seconds()
    print(f"⏳ Waiting {int(wait_seconds)} seconds until {hour}:00 Vietnam Time...")
    return wait_seconds

# === MAIN LOOP ===
while True:
    time.sleep(wait_until_next_run())
    run_screener_latest()
