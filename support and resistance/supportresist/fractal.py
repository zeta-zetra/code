
import pandas as pd 




def fractal_method(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the support and resistance levels using Fractals
    
    :params df 
    :type :pd.DataFrame
    
    :return: (pd.DataFrame)
    """
    
    support_levels    = df[df["low"] == df["low"].rolling(5, center=True).min()]["low"]
    resistance_levels = df[df["high"] == df["high"].rolling(5, center=True).max()]["high"] 
    
    # Filter 
    support_levels    = support_levels[support_levels.diff()>1e-5]
    resistance_levels = resistance_levels[resistance_levels.diff()>1e-5]
    
    # Support and resistance 
    df["support"]    = min(support_levels)
    df["resistance"] = max(resistance_levels)
    
    return df 
    