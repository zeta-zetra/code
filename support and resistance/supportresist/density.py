
import numpy as np 
import pandas as pd
import pandas_ta as ta 
import plotly.graph_objects as go 

from scipy.signal import find_peaks
from scipy.stats  import gaussian_kde
from sklearn.neighbors import KernelDensity


# Own modules
from pivots import find_pivot_points
from plotting import plot_density

def density_method(df: pd.DataFrame, method, bandwidth: float = 0,visualise: bool = False) -> pd.DataFrame:
    """
    Find the support and resistance lines using density based method
    
    :params df 
    :type :pd.DataFrame 
    
    :params method is the density method to use 
    :type :str
    
    :params bandwidth 
    :tyoe :float
    
    :params visualise the density plot 
    :type :bool
    
    :return: (pd.DataFrame)
    """
    
    if method == "density_1":
        # Find the peaks and troughs
        peak_df, trough_df = find_pivot_points(df)
        
        # Get the peak and troughs as separate arrays 
        extrema_idx    = np.concatenate( (peak_df["peak_idx"], trough_df["trough_idx"]))
        extrema_values = np.concatenate( (peak_df["pivot_high"], trough_df["pivot_low"]))
        
        # Estimate the Kernel Density 
        if bandwidth == 0:
            kde = KernelDensity(kernel='gaussian', bandwidth=extrema_values[0]/1000).fit(extrema_values.reshape(-1,1))
        else:
            kde = KernelDensity(kernel='gaussian', bandwidth=extrema_values[0]/bandwidth).fit(extrema_values.reshape(-1,1))
        
        # Visualize the results given the selected bandwidth
        a, b        = min(extrema_values), max(extrema_values)
        price_range = np.linspace(a, b, 1000).reshape(-1,1)
        pdf         = np.exp(kde.score_samples(price_range))
        
        if visualise:
            x_price_range = [ p[0] for p in price_range]
            plot_density(x_price_range, pdf)

        # Find the peaks 
        kde_peaks = find_peaks(pdf)[0]
        
        # Get the lines 
        price_peaks = price_range[kde_peaks] 
        sr          = [ pk[0] for pk in price_peaks]
        
        df["support"]    = min(sr)
        df["resistance"] = max(sr)
    elif method == "density_2":
    
       levels      = support_resistance_levels(df, 200, first_w=1.0, atr_mult=3.0)
       
       n_levels         = len(levels)
       last_levels      = levels[n_levels-1]
       df["support"]    = min(last_levels)
       df["resistance"] = max(last_levels)
        
    return df 

def get_levels( 
        price: np.array, atr: float, # Log closing price, and log atr 
        first_w: float = 0.1, 
        atr_mult: float = 3.0, 
        prom_thresh: float = 0.1
):

    # Setup weights
    last_w = 1.0
    w_step = (last_w - first_w) / len(price)
    weights = first_w + np.arange(len(price)) * w_step
    weights[weights < 0] = 0.0

    # Get kernel of price. 
    kernal = gaussian_kde(price, bw_method=atr*atr_mult, weights=weights)

    # Construct market profile
    min_v = np.min(price)
    max_v = np.max(price)
    step  = (max_v - min_v) / 200
    if step == 0:
        max_v+=1e-5
        step+=1e-5
        
    price_range = np.arange(min_v, max_v, step)
    pdf = kernal(price_range) # Market profile

    # Find significant peaks in the market profile
    pdf_max = np.max(pdf)
    prom_min = pdf_max * prom_thresh

    peaks, props = find_peaks(pdf, prominence=prom_min)
    levels = [] 
    for peak in peaks:
        levels.append(np.exp(price_range[peak]))

    return levels, peaks, props, price_range, pdf, weights




def support_resistance_levels(
        df: pd.DataFrame, lookback: int, 
        first_w: float = 0.01, atr_mult:float=3.0, prom_thresh:float =0.25
):

    # Get log average true range, 
    atr = ta.atr(np.log(df['high']), np.log(df['low']), np.log(df['close']), lookback)
 
    all_levels = [None] * len(df)
    for i in range(lookback, len(df)):
        i_start  = i - lookback
        vals = np.log(df.iloc[i_start+1: i+1]['close'].to_numpy())
        levels, peaks, props, price_range, pdf, weights= get_levels(vals, atr.iloc[i], first_w, atr_mult, prom_thresh)
        all_levels[i] = levels
    return all_levels