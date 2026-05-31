# NPC-Policy-Backtest

# CNH Policy Reaction Backtest

### Project Overview
An algorithmic backtesting framework designed to quantify market sensitivity to fiscal and liquidity announcements from the National People's Congress (NPC) and the PBoC. The tool maps policy "surprises" against CNH volatility and yield curve steepening to anticipate regime shifts.

### The Macro Context
Market participants often struggle to interpret the nuances of Chinese fiscal policy announcements. By isolating the delta between "market-priced expectations" and "actual policy delivery," this framework identifies tradeable dislocations in the CNH forward curve and offshore renminbi liquidity.

### Methodology
* **Core Logic:** Event-study analysis comparing pre-announcement volatility expectations (implied vol) to realized post-announcement price action.
* **Quant Approach:** Multivariate regression analyzing the transmission mechanism of fiscal impulse announcements on CNH/USD and onshore/offshore yield spreads.
* **Tech Stack:** Python | Pandas | Scikit-learn (XGBoost) | Yahoo Finance

### Key Signal
[INSERT SCREENSHOT OF YOUR BACKTEST RESULTS HERE—e.g., A chart showing 'Policy Surprise' vs. 'CNH Volatility' post-NPC]

### Investment Application
* **Alpha Generation:** Identifying mispriced CNH volatility prior to major policy windows.
* **Risk Management:** Quantifying the potential for 'policy-driven' liquidity shocks in the offshore market.
* **Relative Value:** Mapping the impact of fiscal deficit targets on yield curve steepening/flattening.
