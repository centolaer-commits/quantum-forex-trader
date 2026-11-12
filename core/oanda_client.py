import os
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("OandaClient")


class OandaClient:
    """
    Robust REST client for OANDA v20 API.
    Supports both live practice/demo accounts and local mock simulation.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        account_id: Optional[str] = None,
        environment: str = "practice",
    ):
        self.access_token = access_token or os.getenv("OANDA_ACCESS_TOKEN", "")
        self.account_id = account_id or os.getenv("OANDA_ACCOUNT_ID", "")
        self.environment = environment or os.getenv("OANDA_ENVIRONMENT", "practice")

        domain = "api-fxpractice.oanda.com" if self.environment == "practice" else "api-fxtrade.oanda.com"
        self.base_url = f"https://{domain}/v3"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "RFC3339",
        }
        self.is_configured = bool(self.access_token and self.account_id and "your_" not in self.access_token)

    def get_account_summary(self) -> Dict[str, Any]:
        """Fetch account balance, NAV, margin used, and open position count."""
        if not self.is_configured:
            return {
                "balance": 10000.0,
                "nav": 10000.0,
                "unrealized_pl": 0.0,
                "margin_used": 0.0,
                "open_trade_count": 0,
                "mode": "mock_paper_trading",
            }
        url = f"{self.base_url}/accounts/{self.account_id}/summary"
        resp = requests.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        acc = data.get("account", {})
        return {
            "balance": float(acc.get("balance", 0.0)),
            "nav": float(acc.get("NAV", 0.0)),
            "unrealized_pl": float(acc.get("unrealizedPL", 0.0)),
            "margin_used": float(acc.get("marginUsed", 0.0)),
            "open_trade_count": int(acc.get("openTradeCount", 0)),
            "mode": "live_oanda_practice",
        }

    def get_candles(
        self, instrument: str = "EUR_USD", granularity: str = "M15", count: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch OHLCV candlestick data."""
        if not self.is_configured:
            # Fallback mock price generator if offline
            return []
        url = f"{self.base_url}/instruments/{instrument}/candles"
        params = {"price": "M", "granularity": granularity, "count": count}
        resp = requests.get(url, headers=self.headers, params=params, timeout=10)
        resp.raise_for_status()
        candles_raw = resp.json().get("candles", [])
        clean = []
        for c in candles_raw:
            if not c.get("complete", False):
                continue
            mid = c.get("mid", {})
            clean.append({
                "time": c.get("time"),
                "open": float(mid.get("o", 0.0)),
                "high": float(mid.get("h", 0.0)),
                "low": float(mid.get("l", 0.0)),
                "close": float(mid.get("c", 0.0)),
                "volume": int(c.get("volume", 0)),
            })
        return clean

    def create_market_order(
        self,
        instrument: str,
        units: int,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a market order with stop loss and take profit protection."""
        if not self.is_configured:
            logger.info(f"[MOCK ORDER] {units} units of {instrument} | SL={stop_loss_price} | TP={take_profit_price}")
            return {
                "order_id": "MOCK-12345",
                "instrument": instrument,
                "units": units,
                "status": "filled",
                "mode": "mock",
            }
        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        order_spec: Dict[str, Any] = {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(units),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
        }
        if stop_loss_price:
            order_spec["stopLossOnFill"] = {"price": f"{stop_loss_price:.5f}", "timeInForce": "GTC"}
        if take_profit_price:
            order_spec["takeProfitOnFill"] = {"price": f"{take_profit_price:.5f}", "timeInForce": "GTC"}

        payload = {"order": order_spec}
        resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
