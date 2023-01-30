"""
 
This script is inspired by a reddit user by the name of 47dollars. This one is 42 dollars because it only
consists of 42 pairs.
Here is the link: https://www.reddit.com/r/Forex/comments/zx80go/animation_showing_the_correlations_between_the/
                  https://www.reddit.com/r/Forex/comments/zwr0ck/i_created_a_heat_map_showing_the_correlations/


@author Zetra. See our YouTube Channel: https://www.youtube.com/channel/UC87AaqcveNqlkodJrr5zUsw
LICENSE: MIT
DATA SOURCE is Yahoo Finance 
"""

import glob 
import os 
import pandas as pd 
import random
import time
import yfinance as yf 
import plotly.express as px
import plotly.graph_objects as go

def calculate_rolling_corr(df,pair1,pair2,period=90):
    """
    Calculate a rolling correlation between two pairs

    :param df -> Dataframe of the currency pair
    :param pair1 -> First currency pair
    :type :str
    :param pair2 -> Second currency pair
    :type :str
    :param period -> Number of days to consider
    :type :int

    :return List of dicts 

    """

    all_corrs =[]
    for i in range(period,len(df)):
        df_         = df.loc[i-period:i,[pair1, pair2]]
        date_       = df.loc[i,"Date"]
        corr_result = df_.corr(numeric_only=True)
        final_corr  = corr_result[corr_result < 1].unstack().sort_values( ascending=False)[0]
        all_corrs.append({"Date":date_,"Corr":final_corr})
    return all_corrs


def display_table(corr_series, title=""):
    """
    Display table for Top N correlated pairs

    :params corr_matrix -> correlation series
    """
    pair_1_arr = []
    pair_2_arr = []
    for item in corr_series.index:
        pair_1_arr.append(item[0])
        pair_2_arr.append(item[1])

    
    corr_values = [round(value,2) for value in corr_series.values]

    fig = go.Figure(data=[go.Table(
                    header=dict(values=['Pair 1', 'Pair 2', 'Corr'],
                                fill_color='paleturquoise',
                               ),
                    cells=dict(values=[pair_1_arr, pair_2_arr, corr_values],
                                line_color='darkslategray',
                                fill_color='lavender'))
                        ] )

    fig.update_layout(
     title=f"{title}"
    )
    fig.show()



if __name__ == "__main__":

    START_DT     = "2010-11-13"
    END_DT       = "2022-12-31"
    download_new = False
    PAIRS        = ["AUDCAD","AUDCHF","AUDJPY","AUDNZD","AUDUSD","CADCHF","CADJPY",
                    "CHFJPY","EURAUD","EURCAD","EURCHF","EURDKK","EURGBP","EURJPY",
                    "EURNOK","EURNZD","EURRUB","EURSEK","EURTRY","EURUSD",
                    "EURZAR","GBPAUD", "GBPCAD","NZDCAD","NZDCHF","NZDJPY","NZDSGD",
                    "NZDUSD","SGDJPY","USDCAD","USDCHF","USDDKK","USDHKD",
                    "USDJPY","USDMXN","USDNOK","USDPLN","USDRUB","USDSEK","USDSGD",
                    "USDTRY","USDZAR"]

    dir_ = os.path.realpath('')
    data_dir = os.path.join(dir_,"data")


    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
        download_new = True 
    else:
        # Check if there are files
        files = glob.glob(os.path.join(data_dir,"*.csv"))
        if len(files) == 0:
            download_new = True

    # Download the data if required
    if download_new:
        for i, pair in enumerate(PAIRS):
            wait_time = random.randint(2, 5) # Be polite
            try:
                forex_data = yf.download(f'{pair}=X', start=START_DT, end=END_DT)
                file_name  = f"{pair.lower()}.csv"
                forex_data.to_csv(os.path.join( data_dir, file_name))
                print(f"Successfully downloaded {pair}")
                print(f"========= Completed {round((i+1)/len(PAIRS),2)*100}% =========")
                print(f"Waiting {wait_time} seconds before downloading next pair") 
            except Exception as e:
                print(f"Error with {pair}: {e}")
                print(f"========= Completed {round((i+1)/len(PAIRS),2)*100}% =========")
                print(f"Waiting {wait_time} seconds before downloading next pair") 
            
    # Read in the data and row bind
    df_all = pd.DataFrame()
    for i, pair in enumerate(PAIRS):
        try:
            file_name = f"{pair.lower()}.csv"
            df = pd.read_csv(os.path.join( data_dir, file_name))
            df = df[["Date","Adj Close"]]
            df.rename(columns ={"Adj Close":pair}, inplace=True)
        except Exception as e:
            print(f"There was an error reading the following file: {file_name}")
            print(f"Error: {e}")

        if i == 0:
            df_all = df 
            
            print(f"Successfully read first pair: {pair}")
            print(f"========= Completed {round((i+1)/len(PAIRS),2)*100}% =========")
            continue
            
        # Merge based on the Date column
        df_all = df_all.merge(df) 

        print(f"Successfully merged {pair}")
        print(f"========= Completed {round((i+1)/len(PAIRS),2)*100}% =========")


    
    # Drop na 
    df_all.dropna(inplace=True)
    


    # Calculate rolling correlations between two pairs
    period = 90
    pair_1 = PAIRS[random.randint(0, len(PAIRS)-1)] # randomly draw a pair


    pair_2 = pair_1
    while pair_2 == pair_1: 
        pair_2 = PAIRS[random.randint(0, len(PAIRS)-1)] 
    
    all_rolling_corrs = calculate_rolling_corr(df_all, pair_1, pair_2)
    df_rolling_corr = pd.DataFrame(all_rolling_corrs)


    fig = px.line(df_rolling_corr, x="Date", y="Corr", title=f'Rolling {period}-day correlation between {pair_1} and {pair_2}')
    fig.show()

    # Calculate the correlations for all pairs
    corr_matrix = df_all.corr(numeric_only=True) # method is pearson #see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html for more info

    # Top 10 positive correlations
    top_n = 10
    top_10_corr_matrix = corr_matrix[corr_matrix<1].unstack().sort_values( ascending=False).drop_duplicates()[:top_n]
    display_table(top_10_corr_matrix, title=f"Top {top_n} positively correlated pairs")


    # Top 10 negative correlations
    top_n = 10
    top_10_neg_corr_matrix = corr_matrix[corr_matrix<0].unstack().sort_values( ascending=True).drop_duplicates()[:top_n]
    display_table(top_10_neg_corr_matrix, title=f"Top {top_n} negatively correlated pairs")


    # Plot the correlation heatmap
    fig = px.imshow(corr_matrix)
    fig.show()