# Bollinger Bands Strategy

## Overview/Motivation

A Python backtesting framework for evaluating a Bollinger Bands mean-reversion trading strategy against a buy-and-hold control, with train/test validation to check performance on unseen data.

Built as a companion to a prior trend-following (moving-average crossover) project, to explore how a fundamentally different strategy type, betting on price reverting toward its average rather than continuing a trend, performs across the same assets and evaluation framework. It demonstrates applied financial analysis skills using metrics such as Sharpe ratio and maximum drawdown, for quant-focused roles.

## Methodology

A middle band is calculated as a 20-day rolling mean of closing price. Upper and lower bands sit two standard deviations above and below it. When price closes below the lower band, this is treated as a statistically extreme move, one that has moved unusually far from its recent average. The assumption is that such moves tend to correct, so this triggers a long entry, betting on a pullback back toward the mean. The exit is triggered when price reverts back up to the middle band.

Unlike in the moving average crossover strategy, `np.where()` wasn't enough here, because it only checks today's price against today's bands. In the MA strategy, that was fine since we only needed to know if we were in or out on any given day. In the Bollinger Bands strategy, we need to remember whether we're already in a position, since entry and exit are two separate conditions rather than one ongoing comparison. To handle this, a raw signal first marks only the days we actually enter or exit. Then, using the fill function (`.ffill()`), any day where nothing happens gets filled with the last known signal value, giving us a running record of our position over time. To fix the same look-ahead bias as the moving average strategy, a signal shift was also applied here too.

To measure this strategy we use the same metrics as in the moving average project, however due to the difference in strategy a streak counter was added to know the number of days in/out of position and the average trade duration.

## How to run

### Prerequisites

This project requires Python along with the following libraries: `yfinance`, `pandas`, `numpy`, and `matplotlib`.

### Installation

```
pip install yfinance pandas numpy matplotlib
```

### Running the script

```
python BollingerBands.py
```

You'll be prompted to enter a ticker symbol (e.g. `SPY`), then asked whether you'd like to add another. Repeat as many times as needed, then type `no` to finish. The script will then download data, calculate the strategy for each ticker, and display an equity curve chart for each one, close each chart window to move on to the next. Once all charts have been closed, a combined summary table with performance metrics for every ticker will print in the terminal.

## Results

Each cell shows train / test values. Cumulative return of 1.00 = break-even; values are growth of $1 invested. ORCL's test-period Sharpe is N/A because the strategy never entered a position during that period (zero variance, undefined ratio).

| Ticker | Cum. Return (Strategy) | Cum. Return (Buy & Hold) | Sharpe (Strategy) | Sharpe (Buy & Hold) | Max Drawdown (Strategy) |
|--------|------------------------|---------------------------|---------------------|------------------------|----------------------------|
| SPY    | 0.98 / 1.04            | 1.09 / 0.98                | -0.55 / 4.20         | 1.95 / -0.80            | -0.07 / -0.03               |
| AAPL   | 1.02 / 1.06            | 1.23 / 1.03                | 0.89 / 1.72          | 2.63 / 0.75             | -0.03 / -0.08               |
| UPRO   | 0.93 / 1.12            | 1.24 / 0.92                | -0.63 / 4.18         | 1.71 / -1.03            | -0.19 / -0.09               |
| TSLA   | 1.07 / 1.05            | 1.02 / 0.72                | 0.94 / 1.14          | 0.31 / -2.97            | -0.11 / -0.09               |
| ORCL   | 1.12 / 1.00            | 1.12 / 0.59                | 1.42 / N/A           | 0.87 / -4.68            | -0.06 / 0.00                |

In almost every ticker, this strategy beats the buy-and-hold control in the test period, a stark contrast to the moving average project, where the trend-following approach mostly underperformed.

A notable result is ORCL's test period, shown in the table, where a position was never entered, meaning the market never produced a price move extreme enough to trigger a buy signal. This is why the Sharpe value is N/A and drawdown is zero for that period. Looking at buy-and-hold's own test result for ORCL, a steep decline, it's likely a good thing the strategy never entered a position here.

With TSLA, we can see a large gap between the strategy and buy-and-hold in the test period. Buy-and-hold lost around 28% over this window, since it has no way to avoid a decline once it's holding the asset. The strategy, by contrast, only entered when price fell to an extreme, oversold level, and exited once it reverted back to the average, doing this roughly four times over about 40 days total. Because of this, the strategy avoided being exposed to most of the decline, only stepping in for short windows after sharp drops, which is why its cumulative return held up so much better than simply holding the asset throughout.

## Limitations and improvements

- Fixed 20-day window and 2 standard deviations, results are specific to this setup and haven't been tested against other parameter combinations.
- As shown in the results section, ORCL experienced zero trades in its test period, since the market never produced a move extreme enough to trigger an entry.
- The only exit condition tested is reverting to the middle band. Other options, such as a fixed risk to reward exit, were considered but not implemented or compared.
- If this project were repeated, an entry confirmation filter would be a worthwhile addition, giving one final check before entering to reduce false signals. The current version enters on the raw band touch alone, which makes it more susceptible to acting on noise rather than a genuine reversal.

## Tech Stack

- **Python** - core language
- **Pandas** - data handling, rolling averages, time series operations
- **Numpy** - vectorized calculations
- **yfinance** - historical price data
- **Matplotlib** - visualizing strategy vs buy and hold performance

## Column glossary

- **ticker** - a symbol to represent a financial asset on markets
- **latest_close** - the last price an asset was valued at when the market closes
- **daily_return** - this is the percentage change of today's close price to yesterday's close price
- **signal_shift** - this represents whether a trade is entered, it's important to note that this is delayed by a day to accurately represent today's position using yesterday's known information. This prevents acting on data we wouldn't know at the time
- **train** - refers to the 70% of the data used to evaluate how the strategy performs before testing it on unseen data
- **test** - refers to the last 30% of the data used to simulate unseen and out-of-sample performance of the algorithm
- **cumulative_strategy** - this is the combined result of the trading strategy. This applies to both train and test
- **cumulative_buy/hold** - this column is to have a standard/control variable to compare our strategy to, and refers to simply buying and holding the asset. This applies to both train and test
- **sharpe_strategy** - this takes the Sharpe value of our Bollinger Bands strategy, Sharpe refers to how much we are risking to generate profit
- **sharpe_buy/hold** - this takes the Sharpe value of the buy-hold control, Sharpe refers to how much we are risking to generate profit
- **max_drawdown** - the largest percentage drop from a peak in the strategy's cumulative value to a subsequent low, showing the worst loss an investor following this strategy would have experienced at any point
- **middle_band** - a 20-day moving average
- **upper/lower band** - the middle band plus or minus 2 standard deviations respectively
- **raw_signal** - marks only the days a position is actually entered (1) or exited (0), and is left blank (NaN) on every other day where nothing changes
- **signal** - `raw_signal` after being filled forward (`.ffill()`), so it shows a continuous record of whether a position is held on any given day, not just the days something changed
- **changed** - marks True on a day where the `signal` column's value differs from the day before, used to detect the start of a new streak
- **streak** - a running count that increases by one every time `changed` is True, giving each continuous stretch of holding (or not holding) a position its own unique ID
- **days_in_position / days_out_of_position** - total number of days across the whole period spent in or out of a position
- **avg_days_in_position** - the average length, in days, of a single continuous "in position" streak, i.e. how long a typical trade lasted
- **strategy_return** - `daily_return` earned only on days `signal_shift` = 1; zero on days out of the market
- **drawdown** - for every day, how far `cumulative_strategy_return` has fallen from its highest point so far, as a percentage
