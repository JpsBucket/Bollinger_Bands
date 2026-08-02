import yfinance as yt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def main():
    tickers = []

    while True:
        req = input("ticker:").strip().upper()
        data_req = yt.download(req, period = "6mo")

        if data_req.empty:
            print("data n/A")
        else: 
            tickers.append(req)
            print("added")

        q = input("Would you like to add another ticker? ").strip().lower()

        if q == "no":
            break
        elif q != "yes":
            print("not a valid answer, assuming yes")
        

        print("Final tickers:", *tickers)
    
    manipulate(tickers)



def manipulate(tickers):
    
    all_summaries = []

    #download each info on tickers req, we need the multi level index because some data sets have data sets as a value
    for t in tickers:
        df = yt.download(t, period = "6mo", multi_level_index= False)
        df = df.dropna(subset=["Close"])
    #data we want: latest_close, rolling 20 mean, std of lastest_close, sharpe, test/train, cumulative
        df["daily_return"] = df["Close"].pct_change()
        df["middle_band"] = df["Close"].rolling(window = 20).mean()
        df["r_std"] = df["Close"].rolling(window = 20).std()
        df["upper_band"] = df["middle_band"] + (2 * df["r_std"])
        df["lower_band"] = df["middle_band"] - (2 * df["r_std"])
        

        # making a row of NaN, then on condition replace with 1, 0
        df["raw_signal"] = np.nan
        df.loc[df["Close"] < df["lower_band"], "raw_signal"] = 1
        df.loc[df["Close"] >= df["middle_band"], "raw_signal"] = 0

        #filling 1,0 when we are in a position
        df["signal"] = df["raw_signal"].ffill().fillna(0)
        
        #avoid look ahead bias
        df["signal_shift"] = df["signal"].shift(1)        
        df["cumulative_strategy_return"] = (1 + (df["daily_return"] * df["signal_shift"])).cumprod()
        df["cumulative_buyhold_return"] = (1 + df["daily_return"]).cumprod()

        df["drawdown"] = (df["cumulative_strategy_return"] - df["cumulative_strategy_return"].cummax()) / df["cumulative_strategy_return"].cummax()

        #making variables    .iloc to get the specific values in a table
        daily_return = float(df["daily_return"].iloc[-1])
        latest_close = float(df["Close"].iloc[-1])
        upper_band = float(df["upper_band"].iloc[-1])
        lower_band = float(df["lower_band"].iloc[-1])
        middle_band = float(df["middle_band"].iloc[-1])
        signal = float(df["signal_shift"].iloc[-1])

        #this gets the total days of in or out
        days_in_position = int((df["signal"] == 1).sum())
        days_out_of_position = int((df["signal"] == 0).sum())

        #changed is asking if theres a difference if they dont sum to 0
        df["changed"] = df["signal"].diff().ne(0)
        df["streak"] = df["changed"].cumsum()

        streak_summ = df.groupby("streak").agg(
            signal_value=("signal", "first"),
            days_long=("signal", "size")
        )

        in_position_streaks = streak_summ[streak_summ["signal_value"] == 1]
        avg_days_in_position = float(in_position_streaks["days_long"].mean())

        #strategy return, if were in multiplied by the daily return 

        df["strategy_return"] = df["signal_shift"] * df["daily_return"]

        # we need a train test split, 70/30, sharpe, cumulative and drawdown, then buyhold for each and train test for each

        #splitting train/test
        splt = int(len(df) * 0.7)
        train_data = df.iloc[:splt]
        test_data = df.iloc[splt:]
        print(t, "test signal_shift mean:", test_data["signal_shift"].mean())

        #sharpe
        sharpe_strategy_train = (train_data["strategy_return"].mean() / train_data["strategy_return"].std()) * np.sqrt(252)
        sharpe_strategy_test = (test_data["strategy_return"].mean() / test_data["strategy_return"].std()) * np.sqrt(252)
        sharpe_buyhold_train = (train_data["daily_return"].mean() / train_data["daily_return"].std()) * np.sqrt(252)
        sharpe_buyhold_test = (test_data["daily_return"].mean() / test_data["daily_return"].std()) * np.sqrt(252)

        #cumulative 1 + the stra retrun make it cum make it iloc -1
        cumulative_strategy_train = (1 + train_data["strategy_return"]).cumprod().iloc[-1]
        cumulative_strategy_test = (1 + test_data["strategy_return"]).cumprod().iloc[-1]
        cumulative_buyhold_train = (1 + train_data["daily_return"]).cumprod().iloc[-1]
        cumulative_buyhold_test = (1 + test_data["daily_return"]).cumprod().iloc[-1]

        #drawdown - 
        max_drawdown_train = float(train_data["drawdown"].min())
        max_drawdown_test = float(test_data["drawdown"].min())

        summary = pd.DataFrame([{
            "tickers": t, 
            "daily_return": daily_return,
            "latest_close": latest_close,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "middle_band": middle_band,
            "signal": signal, 
            "days_in_position": days_in_position,
            "days_out_of_position": days_out_of_position,
            "avg_days_in_position": avg_days_in_position,
            "cumulative_strategy_train": cumulative_strategy_train,
            "cumulative_strategy_test": cumulative_strategy_test,
            "cumulative_buyhold_train": cumulative_buyhold_train,
            "cumulative_buyhold_test": cumulative_buyhold_test,
            "sharpe_strategy_train": sharpe_strategy_train,
            "sharpe_strategy_test": sharpe_strategy_test,
            "sharpe_buyhold_train": sharpe_buyhold_train, 
            "sharpe_buyhold_test": sharpe_buyhold_test, 
            "max_drawdown_train": max_drawdown_train,
            "max_drawdown_test": max_drawdown_test,
        }])


        all_summaries.append(summary)

        plt.figure()
        plt.plot(df.index, df["cumulative_strategy_return"], label="Strategy")
        plt.plot(df.index, df["cumulative_buyhold_return"], label="Buy & Hold")
        plt.legend()
        plt.title(f"{t} - Strategy vs Buy & Hold")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Return")
        plt.show(block=False)
        plt.pause(0.001)
    


    
    combined = pd.concat( all_summaries, ignore_index=True)
    print(combined)

    plt.show()
    
if __name__ == "__main__":
    main()
