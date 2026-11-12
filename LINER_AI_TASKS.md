# Roadmap de Tarefas para a IA da Liner ($60 a $100/hora)

Copie e cole qualquer uma das tarefas abaixo no prompt do agente de IA da Liner para ele trabalhar no repositório com você:

---

### Tarefa 1: Otimização de Stop Móvel ATR (Trailing Stop)
> *"In `core/risk_manager.py` and `core/strategy_hybrid.py`, implement an adaptive ATR Trailing Stop that moves the stop-loss to breakeven once price reaches 1.0x ATR profit, and then trails behind price at 1.5x ATR. Update `core/backtester.py` to evaluate this on `data/backtest_data_EUR_USD_M15.csv` and report the change in profit factor and maximum drawdown."*

---

### Tarefa 2: Adicionar Indicador SuperTrend
> *"Create a new modular indicator method in `core/strategy_hybrid.py` implementing the SuperTrend indicator (period=10, multiplier=3.0). Combine its trend direction with the existing EMA ribbon to filter out false breakout signals during consolidation phases. Add unit tests in `tests/test_strategy.py`."*

---

### Tarefa 3: Simulação de Monte Carlo para Risco
> *"Implement a Monte Carlo drawdown and risk simulation module in `core/backtester.py`. It should shuffle the historical trade outcomes over 1,000 iterations to calculate the 95th and 99th percentile maximum drawdown, risk of ruin, and probability of achieving 10% account growth."*

---

### Tarefa 4: Cobertura Completa de Testes Unitários (`pytest`)
> *"Expand the test suite in `tests/test_strategy.py` to achieve >90% code coverage across `core/risk_manager.py` and `core/backtester.py`. Include parameterized tests for extreme slippage, gap openings, edge cases in lot sizing, and circuit breaker trip scenarios."*

---

### Tarefa 5: Confirmação Multi-Timeframe (H1 + M15)
> *"Refactor `core/strategy_hybrid.py` to support multi-timeframe analysis. The macro trend direction must be verified on an H1 timeframe (200 EMA + 50 EMA) before permitting Sniper execution entries on the M15 timeframe."*

---

### Tarefa 6: Visualização Gráfica Interativa com Plotly
> *"Create a new visualization script `visualize_backtest.py` that takes the output trades from `core/backtester.py` and generates an interactive HTML dashboard using Plotly. Include candlestick charts, buy/sell markers, equity curve vs. buy-and-hold, and underwater drawdown plots."*
