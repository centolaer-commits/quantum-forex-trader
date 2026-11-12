import pytest
import pandas as pd
import numpy as np
from core.strategy_hybrid import HybridTradingStrategy
from core.risk_manager import RiskManager
from core.oanda_client import OandaClient


@pytest.fixture
def sample_ohlcv_data():
    """Generates synthetic trending OHLCV data for testing."""
    np.random.seed(42)
    n = 250
    close = np.linspace(1.0800, 1.1000, n) + np.random.normal(0, 0.0005, n)
    high = close + np.random.uniform(0.0002, 0.0008, n)
    low = close - np.random.uniform(0.0002, 0.0008, n)
    open_p = close + np.random.normal(0, 0.0003, n)
    volume = np.random.randint(100, 5000, n)

    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })
    return df


def test_indicator_calculation(sample_ohlcv_data):
    strategy = HybridTradingStrategy()
    df_calc = strategy.calculate_indicators(sample_ohlcv_data)

    assert "ema_fast" in df_calc.columns
    assert "ema_medium" in df_calc.columns
    assert "ema_slow" in df_calc.columns
    assert "ema_trend" in df_calc.columns
    assert "rsi" in df_calc.columns
    assert "atr" in df_calc.columns
    assert not df_calc["ema_trend"].iloc[-1] == 0


def test_risk_manager_position_sizing():
    rm = RiskManager(max_risk_per_trade_pct=1.0)
    # $10,000 balance, risk 1% = $100. Entry: 1.1000, SL: 1.0950 (50 pips = 0.0050)
    units = rm.calculate_position_size(
        account_balance=10000.0,
        entry_price=1.1000,
        stop_loss_price=1.0950,
    )
    # 100 / 0.0050 = 20,000 units
    assert units == 20000


def test_circuit_breaker():
    rm = RiskManager(max_daily_drawdown_pct=3.0)
    # Normal operation
    check1 = rm.evaluate_circuit_breaker(current_balance=10000.0, current_equity=9900.0)
    assert not check1["circuit_tripped"]

    # 4% drawdown -> should trip
    check2 = rm.evaluate_circuit_breaker(current_balance=10000.0, current_equity=9550.0)
    assert check2["circuit_tripped"]
    assert check2["status"] == "HALT_TRADING"


def test_oanda_mock_fallback():
    client = OandaClient(access_token="mock_token", account_id="mock_acc")
    summary = client.get_account_summary()
    assert summary["balance"] == 10000.0
    assert summary["mode"] == "mock_paper_trading"
