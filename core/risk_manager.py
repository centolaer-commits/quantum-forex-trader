import logging
from typing import Dict, Any

logger = logging.getLogger("RiskManager")


class RiskManager:
    """
    Capital preservation and mathematical position sizing engine.
    Calculates dynamic lot sizing based on account equity, ATR volatility,
    and enforces maximum daily drawdown circuit breakers.
    """

    def __init__(
        self,
        max_risk_per_trade_pct: float = 1.0,
        max_daily_drawdown_pct: float = 3.0,
        rr_ratio: float = 2.0,
    ):
        self.max_risk_pct = max_risk_per_trade_pct
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.rr_ratio = rr_ratio
        self.starting_daily_balance: float = 0.0

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        pip_value_per_unit: float = 0.0001,
    ) -> int:
        """
        Calculate units to trade such that potential loss <= max_risk_pct * balance.
        """
        risk_capital = account_balance * (self.max_risk_pct / 100.0)
        risk_distance = abs(entry_price - stop_loss_price)

        if risk_distance <= 0:
            return 1000

        # Position size in units
        units = int(risk_capital / risk_distance)
        # Cap to minimum sensible lot size
        return max(1000, min(units, 100_000))

    def evaluate_circuit_breaker(self, current_balance: float, current_equity: float) -> Dict[str, Any]:
        """
        Check if daily drawdown limit has been reached.
        """
        if self.starting_daily_balance <= 0:
            self.starting_daily_balance = current_balance

        drawdown_pct = ((self.starting_daily_balance - current_equity) / self.starting_daily_balance) * 100.0
        circuit_tripped = drawdown_pct >= self.max_daily_drawdown_pct

        if circuit_tripped:
            logger.warning(
                f"[CIRCUIT BREAKER TRIGGERED] Drawdown {drawdown_pct:.2f}% exceeded limit {self.max_daily_drawdown_pct}%"
            )

        return {
            "circuit_tripped": circuit_tripped,
            "current_drawdown_pct": round(drawdown_pct, 2),
            "max_allowed_drawdown_pct": self.max_daily_drawdown_pct,
            "status": "HALT_TRADING" if circuit_tripped else "NORMAL",
        }

    def calculate_atr_stop_and_target(
        self, entry_price: float, direction: str, atr_value: float, atr_multiplier: float = 1.5
    ) -> Dict[str, float]:
        """
        Compute dynamic Stop Loss and Take Profit levels based on Average True Range.
        """
        stop_distance = atr_value * atr_multiplier
        target_distance = stop_distance * self.rr_ratio

        if direction.upper() in ["BUY", "LONG"]:
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + target_distance
        else:
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - target_distance

        return {
            "entry_price": round(entry_price, 5),
            "stop_loss": round(stop_loss, 5),
            "take_profit": round(take_profit, 5),
            "risk_reward_ratio": self.rr_ratio,
        }
