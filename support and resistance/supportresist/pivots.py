import numpy as np
import pandas as pd 


from scipy.signal import argrelextrema
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from typing import List, Tuple

# Own modules
from utils import resample_ohlc, get_resample_period


def within_limit(price: float, upper_limit: float, lower_limit:float) -> bool:
    """
    Check if the given price is within the given bounds

    :params price check if is within the bounds
    :type :float

    :params upper_limit 
    :type :float

    :params lower_limit
    :type :float

    :return: (bool)
    """

    if price > lower_limit and price < upper_limit:
        return True
    else:
        return False

def calculate_price_scores(df: pd.DataFrame, prices: pd.DataFrame, limit_perc:float=0.05) -> pd.DataFrame:
    """
    Calculate the score for the given prices 

    :params df is the OHLC data 
    :type :pd.DataFrame

    :params prices to be scored 
    :type :pd.DataFrame

    :params limit forms the area around the prices to be scored 
    :type :float
    
    :params limit_perc is the percentage to use for the price bounds
    :type :float

    :return: (pd.DataFrame)
    """

    for r in range(0,prices.shape[0]):
        
        price = prices.iloc[r,1]
        upper_limit = price*(1+limit_perc)
        lower_limit = price*(1- limit_perc) 
        score = 0
        for row in df.iterrows():
            s = sum([within_limit(row[1][p], upper_limit, lower_limit) for p in ["open","high", "low", "close"]])
            if s>=2:
            
                score+=1
            else:
                score-=1
            
        prices.loc[r,"score"] = score

    return prices 


def scoring_method_1(df: pd.DataFrame, pivot_highs: pd.DataFrame, pivot_lows: pd.DataFrame, 
                      limit_perc:float=0.05,filter_limit: float = 1e-5 ) -> pd.DataFrame:
    """
    Scoring method number 1
    
    The scoring method is based on if two or more of the OHLC prices are within the bounds set by limit
    
    :params df is the OHLC data
    :type :pd.DataFrame

    :params pivot_highs is a dataframe that has the pivot highs 
    :type :pd.DataFrame

    :params pivot_lows is a dataframe that has the pivot lows 
    :type :pd.DataFrame

    :params limit_perc is the percentage to use for the price bounds
    :type :float

    :params filter_limit is the limit between how close the prices should be
    :type :float 

    :return: (pd.DataFrame)
    """

    # Get the scores
    highs_scores  = calculate_price_scores(df, pivot_highs, limit_perc)
    lows_scores   = calculate_price_scores(df, pivot_lows, limit_perc)

    # Sort the scores
    highs_scores.sort_values("score", ascending=False, inplace=True)
    lows_scores.sort_values("score", ascending=False, inplace=True)

    # Remove prices that are close
    filter_highs = abs(highs_scores["pivot_high"].diff())>filter_limit 
    filter_lows  = abs(lows_scores["pivot_low"].diff())>filter_limit
    highs_scores = highs_scores[filter_highs]
    lows_scores  = lows_scores[filter_lows]


    # Select the top X as l1 and l2
    l_1 = highs_scores.head()
    l_2    = lows_scores.head()

    # Sort by index 
    l_1.sort_values("peak_idx", inplace=True)
    l_2.sort_values("trough_idx", inplace=True)

    # Create the L columns
    df["l_1"]    = np.nan
    df["l_2"]    = np.nan 

    
    # Find the indexes of the Levels
    trough_idx = l_2["trough_idx"].tolist()
    peak_idx   = l_1["peak_idx"].tolist()
    
    # Add the last data point to the indexes
    trough_idx.append(df.shape[0])
    peak_idx.append(df.shape[0])

    # Fill the columns of S/R with values    
    sr =   [("l_2",trough_idx, l_2), ("l_1", peak_idx, l_1)]
    for pair in sr:
        for i in range(len(pair[1])-1):
            start = pair[1][i]
            end   = pair[1][i+1]

            level = pair[2].iloc[i, 1]
            df.loc[start: end, pair[0]] = level

    df["resistance"] = df[["l_1","l_2"]].max(axis=1)
    df["support"]    = df[["l_1","l_2"]].min(axis=1)
    return df 

def scoring_methods(df: pd.DataFrame, method: str, **kwargs):
    """
    Find the levels using scoring methods

    :params df 
    :type :pd.DataFrame
    """
    
    # Get the pivot dataframes
    pivot_highs,  pivot_lows = find_pivot_points(df)

    # Find the S/R Levels
    if method == "scoring_1":
        df = scoring_method_1(df, pivot_highs, pivot_lows)



    return df

def find_optimal_clusters_silhouette(data, min_clusters, max_clusters, method="agglomerative"):
    cluster_range = range(min_clusters, max_clusters + 1)

    if method == "agglomerative":
        clustering_function = AgglomerativeClustering
    elif method == "kmeans":
        clustering_function = KMeans
    else:
        raise ValueError(
            "Invalid clustering method. Choose either 'agglomerative' or 'kmeans'."
        )

    silhouette_scores = [
        silhouette_score(
            data, clustering_function(n_clusters=i).fit(data).labels_
        )
        for i in cluster_range
    ]

    optimal_clusters = cluster_range[np.argmax(silhouette_scores)]
    return optimal_clusters

def clustering_methods(df: pd.DataFrame, method: str ="kmeans", pivot_method:str="argrel") -> pd.DataFrame:
    """
    Use Clustering methods to find the support and resistance levels 

    :params df 
    :type :pd.DataFrame

    :params method to use for clustering 
    :type :str 

    :params pivot_method is to calculate for pivot points 
    :type :str 

    :return: (pd.DataFrame)
    """

    pivot_highs, pivot_lows = find_pivot_points(df, method=pivot_method)

    peaks    = np.reshape(pivot_highs, (-1,1))
    troughs  = np.reshape(pivot_lows, (-1,1))

    min_clusters          = 3
    max_clusters_peaks    = len(peaks) - 1
    max_clusters_troughs  = len(troughs) - 1

    # Find the optimal number of clusters for peaks and troughs
    optimal_clusters_peaks = find_optimal_clusters_silhouette(
        peaks, min_clusters, max_clusters_peaks, method=method
    )
    optimal_clusters_troughs = find_optimal_clusters_silhouette(
        troughs, min_clusters, max_clusters_troughs, method=method
    )

    # Clustering Algorithms
    if method == "agglomerative":
        cluster_peak_model   = AgglomerativeClustering(n_clusters=optimal_clusters_peaks)
        cluster_trough_model = AgglomerativeClustering(n_clusters=optimal_clusters_troughs)
    elif method == "kmeans":
        cluster_peak_model   = KMeans(n_clusters=optimal_clusters_peaks)
        cluster_trough_model = KMeans(n_clusters=optimal_clusters_troughs)

    peak_labels    = cluster_peak_model.fit_predict(peaks)
    trough_labels  = cluster_trough_model.fit_predict(troughs)

    # Get the last values from the peaks and troughs
    last_peak   = peaks[-1]
    last_trough = troughs[-1]

    # Determine which cluster the last peak and trough belong to
    peak_cluster_label   = peak_labels[-1]
    trough_cluster_label = trough_labels[-1]

    # Find the max(min) of the last peak(trough) cluster group
    max_high_peak_cluster  = np.max(peaks[peak_labels==peak_cluster_label])
    min_low_trough_cluster = np.min(troughs[trough_labels==trough_cluster_label])

    print(f"Last trough belongs to Trough CLuster {trough_cluster_label}")
    print(f"Last peak belongs to Peak CLuster {peak_cluster_label}")

    df["support"]    = min_low_trough_cluster
    df["resistance"] = max_high_peak_cluster

    return df 


def pivot_point_methods(df: pd.DataFrame, method: str="traditional", levels="l") -> pd.DataFrame:
    """
    Calculate the support and resistance levels using the specified method

    :params df
    :type :str 

    :params method to use to find the levels. Options: ["fibonacci", "camarilla", "traditional", "dm"]
    :type :str 

    :return: (pd.DataFrame)
    """
    
    df["date"]       = pd.to_datetime(df["date"], dayfirst=True)
    df.set_index("date", inplace=True)

    # Resample the OHLC data
    resample_period = get_resample_period(df)
    resample_df     = resample_ohlc(df, period=resample_period)    


    intra_date    = df.index.strftime('%Y-%m-%d')
    df["MDate"] = intra_date
    if method == "dm":
        # Calculate the pivot points for DM  
        resample_df["PP"] = (resample_df["High"] + resample_df["Low"] + resample_df["Close"])/3

        resample_df["R1"] = resample_df["PP"]*2 - resample_df["Low"]
        resample_df["S1"] = resample_df["PP"]*2 - resample_df["High"]
        
        resample_df["R2"] = resample_df["PP"] + (resample_df["High"] - resample_df["Low"])
        resample_df["S2"] = resample_df["PP"] - (resample_df["High"] - resample_df["Low"])

        # Shift the Pivot Points
        resample_df["PP"] = resample_df["PP"].shift(1)
        resample_df["R1"] = resample_df["R1"].shift(1)
        resample_df["S1"] = resample_df["S1"].shift(1)
        resample_df["R2"] = resample_df["R2"].shift(1)
        resample_df["S2"] = resample_df["S2"].shift(1)

    elif method == "traditional":
        # Calculate the pivot points on the Traditional Method
        resample_df["PP"] = (resample_df["High"] + resample_df["Low"] + resample_df["Close"])/3

        resample_df["R1"] = resample_df["PP"]*2 - resample_df["Low"]
        resample_df["S1"] = resample_df["PP"]*2 - resample_df["High"]
        
        resample_df["R2"] = resample_df["PP"] + (resample_df["High"] - resample_df["Low"])
        resample_df["S2"] = resample_df["PP"] - (resample_df["High"] - resample_df["Low"])

        # Shift the Pivot Points
        resample_df["PP"] = resample_df["PP"].shift(1)
        resample_df["R1"] = resample_df["R1"].shift(1)
        resample_df["S1"] = resample_df["S1"].shift(1)
        resample_df["R2"] = resample_df["R2"].shift(1)
        resample_df["S2"] = resample_df["S2"].shift(1)



    elif method == "fibonacci":
        # Calculate the pivot points on the Fibonacci method 
        resample_df["PP"] = (resample_df["High"] + resample_df["Low"] + resample_df["Close"])/3

        resample_df["R1"] = resample_df["PP"] + 0.382*(resample_df["High"] - resample_df["Low"])
        resample_df["S1"] = resample_df["PP"] - 0.382*(resample_df["High"] - resample_df["Low"])
        
        resample_df["R2"] = resample_df["PP"] + 0.618*(resample_df["High"] - resample_df["Low"])
        resample_df["S2"] = resample_df["PP"] - 0.618*(resample_df["High"] - resample_df["Low"])

        # Shift the Pivot Points
        resample_df["PP"] = resample_df["PP"].shift(1)
        resample_df["R1"] = resample_df["R1"].shift(1)
        resample_df["S1"] = resample_df["S1"].shift(1)
        resample_df["R2"] = resample_df["R2"].shift(1)
        resample_df["S2"] = resample_df["S2"].shift(1)

        # Subset and get the Pivot points
        resample_df = resample_df[["MDate", "PP", "S1", "S2", "R1", "R2"]]



    elif method == "camarilla":
        # Calculate the pivot points on the Camarilla method
        resample_df["PP"] = (resample_df["High"] + resample_df["Low"] + resample_df["Close"])/3

        resample_df["R1"] = resample_df["Close"]  + 1.1*(resample_df["High"] - resample_df["Low"])/12
        resample_df["S1"] = resample_df["Close"] - 1.1*(resample_df["High"] - resample_df["Low"])/12
        
        resample_df["R2"] = resample_df["Close"]  + 1.1*(resample_df["High"] - resample_df["Low"])/6
        resample_df["S2"] = resample_df["Close"]  - 1.1*(resample_df["High"] - resample_df["Low"])/6

        # Shift the Pivot Points
        resample_df["PP"] = resample_df["PP"].shift(1)
        resample_df["R1"] = resample_df["R1"].shift(1)
        resample_df["S1"] = resample_df["S1"].shift(1)
        resample_df["R2"] = resample_df["R2"].shift(1)
        resample_df["S2"] = resample_df["S2"].shift(1)

    # Subset and get the Pivot points
    resample_df = resample_df[["MDate", "PP", "S1", "S2", "R1", "R2"]]

    # Merge the intra day and daily pivot point data
    ohlc_merged = df.merge(resample_df, left_on="MDate", right_on="MDate")
    ohlc_merged.set_index(df.index, inplace=True)
    
    # Drop missing info
    ohlc_merged.dropna(inplace=True)

    if levels == "l":
        ohlc_merged = ohlc_merged.tail(100)

    return ohlc_merged



def find_pivot_points(df: pd.DataFrame, method: str ="argrel") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Find the Pivot Points given the OHLC data

    :params df is the OHLC data
    :type :str 

    :params method is the method to calculate the pivot points 
    :type  :str

    :return: (Tuple[pd.DataFrame, pd.DataFrame])
    """

    if method == "argrel":
        high = df["high"].values 
        lows = df["low"].values 

        peak_idx   = argrelextrema(high, np.greater)
        trough_idx = argrelextrema(lows, np.less)
       
        pivot_high   = high[peak_idx] 
        pivot_low    = lows[trough_idx]


        peak_df      = pd.DataFrame({"peak_idx": peak_idx[0], "pivot_high": pivot_high})
        trough_df    = pd.DataFrame({"trough_idx": trough_idx[0], "pivot_low": pivot_low})

        return peak_df, trough_df



