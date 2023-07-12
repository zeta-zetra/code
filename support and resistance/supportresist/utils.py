import pandas as pd


def get_resample_period(df: pd.DataFrame) -> str:
    """
    Get the resample period 

    :params df 
    :type :pd.DataFrame

    :return: (str)
    """

    
    date                = df.index
    diff_date           = date - pd.Series(date).shift() #date.shift(1)
    time_diff_minutes   = diff_date/pd.Timedelta(minutes=1) 
    period              = time_diff_minutes.value_counts().index[0]

    # Take from TradingView (i.e. Pivot Points Standard Help)
    if int(period) <= 15:
          resample_period = "D"
    elif int(periods) > 15 and int(period) < 24*60:
         resample_period = "W"
    elif int(periods) == 24*60:
        resample_period = "M"
    else:
        resample_period = "12M"

    return resample_period


def resample_ohlc(df: pd.DataFrame, period: str="D") -> pd.DataFrame:
    """
    Resample the OHLC data

    :params df is the dataframe
    :type :pd.DataFrame

    :params period is the resampling period
    :type :str

    :return: (pd.DataFrame)
    """
    
    open_resample       = df["open"].resample(period).first()
    close_resample      = df["close"].resample(period).last()
    high_resample       = df["high"].resample(period).max()
    low_resample        = df["low"].resample(period).min()
    
    date_index =  df["open"].resample(period).first().index.strftime('%Y-%m-%d')
    
    resample_df = pd.DataFrame({
                "Open": open_resample,
                "High": high_resample,
                "Low" : low_resample,
                "Close": close_resample,
                "MDate": date_index 
    })

    return resample_df
