import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class HybridTradingStrategy:
    """
    Quantum Hybrid Strategy (Sniper M15 + Momentum Filter).
    Uses Exponential Moving Average (EMA) Ribbons, Relative Strength Index (RSI),
    and Average True Range (ATR) to identify institutional order-flow continuation.
    """

    def __init__(
        self,
        fast_ema: int = 9,
        medium_ema: int = 21,
        slow_ema: int = 50,
        trend_ema: int = 200,
        rsi_period: int = 14,
        atr_period: int = 14,
    ):
        self.fast_ema = fast_ema
        self.medium_ema = medium_ema
        self.slow_ema = slow_ema
        self.trend_ema = trend_ema
        self.rsi_period = rsi_period
        self.atr_period = atr_period

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes technical indicators across the OHLCV dataset."""
        df = df.copy()

        # Moving Averages
        df["ema_fast"] = df["close"].ewm(span=self.fast_ema, adjust=False).mean()
        df["ema_medium"] = df["close"].ewm(span=self.medium_ema, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow_ema, adjust=False).mean()
        df["ema_trend"] = df["close"].ewm(span=self.trend_ema, adjust=False).mean()

        # Relative Strength Index (RSI)
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df["rsi"] = 100 - (100 / (1 + rs))

        # Average True Range (ATR)
        high_low = df["high"] - df["low"]
        high_prev_close = (df["high"] - df["close"].shift(1)).abs()
        low_prev_close = (df["low"] - df["close"].shift(1)).abs()
        tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
        df["atr"] = tr.rolling(window=self.atr_period).mean()

        return df

    def evaluate_signal(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Evaluate the latest completed candlestick for trade setups.
        Returns a signal dictionary if conditions are satisfied, else None.
        """
        if len(df) < self.trend_ema:
            return None

        df_calc = self.calculate_indicators(df)
        curr = df_calc.iloc[-1]
        prev = df_calc.iloc[-2]

        close = curr["close"]
        ema_fast = curr["ema_fast"]
        ema_med = curr["ema_medium"]
        ema_trend = curr["ema_trend"]
        rsi = curr["rsi"]
        atr = curr["atr"]

        # Bullish Sniper Alignment
        bullish_trend = close > ema_trend and ema_fast > ema_med
        bullish_crossover = prev["ema_fast"] <= prev["ema_medium"] and ema_fast > ema_med
        bullish_rsi = 48 <= rsi <= 68

        if bullish_trend and (bullish_crossover or (close > ema_fast and 50 <= rsi <= 65)):
            return {
                "action": "BUY",
                "instrument": "EUR_USD",
                "price": close,
                "atr": atr,
                "rsi": rsi,
                "trend": "BULLISH",
                "strategy": "Sniper_M15_TrendContinuation",
            }

        # Bearish Sniper Alignment
        bearish_trend = close < ema_trend and ema_fast < ema_med
        bearish_crossover = prev["ema_fast"] >= prev["ema_medium"] and ema_fast < ema_med
        bearish_rsi = 32 <= rsi <= 52

        if bearish_trend and (bearish_crossover or (close < ema_fast and 35 <= rsi <= 50)):
            return {
                "action": "SELL",
                "instrument": "EUR_USD",
                "price": close,
                "atr": atr,
                "rsi": rsi,
                "trend": "BEARISH",
                "strategy": "Sniper_M15_TrendContinuation",
            }

        return None
