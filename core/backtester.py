import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from core.strategy_hybrid import HybridTradingStrategy
from core.risk_manager import RiskManager


class Backtester:
    """
    Historical event-driven backtesting engine.
    Simulates execution on historical M15 candlestick CSV data.
    """

    def __init__(
        self,
        initial_balance: float = 10000.0,
        risk_per_trade_pct: float = 1.0,
        rr_ratio: float = 2.0,
    ):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_manager = RiskManager(max_risk_per_trade_pct=risk_per_trade_pct, rr_ratio=rr_ratio)
        self.strategy = HybridTradingStrategy()
        self.trades: List[Dict[str, Any]] = []

    def run_backtest(self, csv_path: str) -> Dict[str, Any]:
        """Runs the simulation across a CSV file."""
        df = pd.read_csv(csv_path)

        # Standardize column names
        df.columns = [c.lower() for c in df.columns]
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values("time").reset_index(drop=True)

        df = self.strategy.calculate_indicators(df)
        warmup = self.strategy.trend_ema + 5

        active_trade: Dict[str, Any] = None

        for i in range(warmup, len(df)):
            row = df.iloc[i]
            prev_slice = df.iloc[: i + 1]

            # Check if active trade hit SL or TP
            if active_trade:
                high = row["high"]
                low = row["low"]
                direction = active_trade["direction"]
                sl = active_trade["stop_loss"]
                tp = active_trade["take_profit"]

                closed = False
                pnl = 0.0

                if direction == "BUY":
                    if low <= sl:
                        closed = True
                        pnl = (sl - active_trade["entry_price"]) * active_trade["units"]
                        active_trade["exit_reason"] = "STOP_LOSS"
                    elif high >= tp:
                        closed = True
                        pnl = (tp - active_trade["entry_price"]) * active_trade["units"]
                        active_trade["exit_reason"] = "TAKE_PROFIT"
                else:  # SELL
                    if high >= sl:
                        closed = True
                        pnl = (active_trade["entry_price"] - sl) * active_trade["units"]
                        active_trade["exit_reason"] = "STOP_LOSS"
                    elif low <= tp:
                        closed = True
                        pnl = (active_trade["entry_price"] - tp) * active_trade["units"]
                        active_trade["exit_reason"] = "TAKE_PROFIT"

                if closed:
                    active_trade["pnl"] = round(pnl, 2)
                    self.balance += pnl
                    active_trade["exit_price"] = tp if "PROFIT" in active_trade["exit_reason"] else sl
                    active_trade["balance_after"] = round(self.balance, 2)
                    self.trades.append(active_trade)
                    active_trade = None

            # If no active trade, evaluate new signal
            if not active_trade:
                signal = self.strategy.evaluate_signal(prev_slice)
                if signal:
                    levels = self.risk_manager.calculate_atr_stop_and_target(
                        entry_price=row["close"],
                        direction=signal["action"],
                        atr_value=row["atr"],
                    )
                    units = self.risk_manager.calculate_position_size(
                        account_balance=self.balance,
                        entry_price=levels["entry_price"],
                        stop_loss_price=levels["stop_loss"],
                    )
                    active_trade = {
                        "entry_time": row.get("time", str(i)),
                        "direction": signal["action"],
                        "entry_price": levels["entry_price"],
                        "stop_loss": levels["stop_loss"],
                        "take_profit": levels["take_profit"],
                        "units": units,
                    }

        return self.compute_metrics()

    def compute_metrics(self) -> Dict[str, Any]:
        """Calculates win rate, profit factor, max drawdown, and total return."""
        total_trades = len(self.trades)
        if total_trades == 0:
            return {"total_trades": 0, "final_balance": self.balance, "total_return_pct": 0.0}

        wins = [t for t in self.trades if t["pnl"] > 0]
        losses = [t for t in self.trades if t["pnl"] < 0]

        total_gain = sum(t["pnl"] for t in wins)
        total_loss = abs(sum(t["pnl"] for t in losses))

        win_rate = (len(wins) / total_trades) * 100.0 if total_trades > 0 else 0.0
        profit_factor = (total_gain / total_loss) if total_loss > 0 else 999.0
        net_profit = self.balance - self.initial_balance
        return_pct = (net_profit / self.initial_balance) * 100.0

        return {
            "initial_balance": self.initial_balance,
            "final_balance": round(self.balance, 2),
            "net_profit": round(net_profit, 2),
            "total_return_pct": round(return_pct, 2),
            "total_trades": total_trades,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
        }
