import argparse
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from core.oanda_client import OandaClient
from core.risk_manager import RiskManager
from core.strategy_hybrid import HybridTradingStrategy
from core.backtester import Backtester

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("QuantumForexTrader")


def run_backtest_mode(csv_path: str):
    logger.info(f"Running historical backtest simulation using: {csv_path}")
    bt = Backtester(initial_balance=10000.0, risk_per_trade_pct=1.0, rr_ratio=2.0)
    results = bt.run_backtest(csv_path)

    print("\n" + "=" * 60)
    print("  📊 QUANTUM FOREX TRADER — BACKTEST RESULTS")
    print("=" * 60)
    print(f"  Initial Balance : ${results['initial_balance']:,.2f}")
    print(f"  Final Balance   : ${results['final_balance']:,.2f}")
    print(f"  Net Profit      : ${results['net_profit']:,.2f} ({results['total_return_pct']:+.2f}%)")
    print(f"  Total Trades    : {results['total_trades']}")
    print(f"  Win Rate        : {results['win_rate_pct']:.2f}% ({results['winning_trades']}W / {results['losing_trades']}L)")
    print(f"  Profit Factor   : {results['profit_factor']:.2f}")
    print("=" * 60 + "\n")


def run_live_demo_mode():
    logger.info("Initializing Live Practice / Demo mode connected to OANDA v20...")
    client = OandaClient()
    acc = client.get_account_summary()
    print("\n" + "=" * 60)
    print("  🚀 QUANTUM FOREX TRADER — OANDA CONNECTION")
    print("=" * 60)
    print(f"  Mode            : {acc['mode']}")
    print(f"  Account Balance : ${acc['balance']:,.2f}")
    print(f"  Net Asset Value : ${acc['nav']:,.2f}")
    print(f"  Unrealized P&L  : ${acc['unrealized_pl']:,.2f}")
    print(f"  Open Trades     : {acc['open_trade_count']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantum Forex Algorithmic Trading Framework")
    parser.add_argument(
        "--mode",
        choices=["backtest", "live-demo"],
        default="backtest",
        help="Operating mode: 'backtest' for offline historical simulation or 'live-demo' for OANDA practice execution",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="data/backtest_data_EUR_USD_M15.csv",
        help="Path to historical candlestick CSV dataset for backtesting",
    )
    args = parser.parse_args()

    if args.mode == "backtest":
        target_csv = Path(args.csv)
        if not target_csv.exists():
            target_csv = Path(__file__).parent / args.csv
        if not target_csv.exists():
            logger.error(f"Backtest dataset not found at: {args.csv}")
            sys.exit(1)
        run_backtest_mode(str(target_csv))
    else:
        run_live_demo_mode()
