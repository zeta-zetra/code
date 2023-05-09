![image](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)


# Python Trading Code

> This repo houses python code about topics related to testing, trading and researching forex strategies. The code can be adapted
   for cryptocurrencies or other tradable asset classes.  


Table of Contents
=================

 * [Testing Forex Strategies](#testing-forex-strategies) 
 * [20 pips challenge](#20-pips-challenge) 
    * [EMA, RSI and Fractals](#ema-rsi-fractals)
    * [EMA Scalping](#ema-scalping)
 * [Automate Chart Patterns](#automate-chart-patterns)
     * [Head and Shoulders Patterns](#head-and-shoulders-patterns)
     * [Inverse Head and Shoulders Patterns](#inverse-head-and-shoulders-patterns)
     * [Triple top and bottom Patterns](#triple-top-and-bottom-patterns)
     * [Rectangle Patterns](#rectangle-patterns)
     * [Wedge Patterns](#wedge-patterns)
     * [Flag Patterns](#flag-patterns)
 * [MACD](#macd)
 * [Short Content](#short-content)
     * [42Dollars](#42dollars)
     * [Bullish Candlesticks](#bullish-candlesticks)
 * [Data](#data)
 * [License](#license)
 * [Contact](#contact)
 * [Buy me coffee](#buy-me-coffee)
 * [Disclaimer](#disclaimer)


## Testing Forex Strategies

> Please note this section was written by ChatGPT, May 3 version. 

Hey there! I'm always on the lookout for fresh and exciting ideas to try out. That's why I spend a good chunk of my time diving into books, blogs, papers, and even watching YouTube videos for some strategy inspiration. It's amazing how much you can learn from these sources!

Speaking of strategies, I've collected a bunch of Python code in this folder. These are strategies that I stumbled upon during my research and thought they were worth putting to the test. I've even categorized them for easier navigation:

  - First, we have strategies I discovered on YouTube. You know, those hidden gems shared by 'experts' in the field.
    
  - Then we have strategies from books, because there's nothing like some good old-fashioned wisdom between the pages. 
  
  - Of course, I couldn't miss out on strategies that were requested by fellow enthusiasts. It's always interesting to explore new ideas brought to the table.
  
  -  Next up, we've got strategies from blogs, where some fantastic minds share their insights and experiences.
   
  - Last but not least, we have chart pattern strategies, because patterns in the charts can hold valuable clues for successful trading.

If you're curious and want to take a peek at the details, I've got you covered. Just head over to the project's documentation [here](https://zeta-zetra.github.io/docs-forex-strategies-python/). Feel free to explore and let me know if you have any questions or suggestions!

## 20 pips challenge

You probably don't have $50 000, or $25 000 or $10 000 to start trading forex. Maybe we can start with $20 and grow it to over $50,000. The 20 pips challenge shows how you can grow your small account with at least 30 trades. See the image below.

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/20-pips.png" alt="20-pips-challenge">
  </a>


This folder contains scripts that you can test to grow your $20 to over $50,000. You can check out the YouTube video [here](https://www.youtube.com/watch?v=eaDgOT7FEOA).

### 1. EMA, RSI and Fractals

This is a scalping strategy from the ["Moving Average" channel](https://www.youtube.com/@TheMovingAverage).

The strategy uses the Williams Fractals, the RSI and 3 moving averages, namely: the 21 MA, the 50 MA, and the 200 MA. The strategy is tested in the 15 min timeframe.


### 2. EMA Scalping 

Here is another scalping strategy but from a different YouTube channel called [CodeTrading](https://www.youtube.com/watch?v=ybmep_u5MeU). The strategy only uses three moving averages.
The 50 EMA, the 100 EMA and the 150 EMA. It was tested in the 15-minute time frame. 

## Automate Chart Patterns

> In his book, Encyclopedia of Chart Patterns , Thomas Bulkowski says, "To knowledgeable investors, chart patterns are not squiggles on a
  price chart; they are the footprints of the smart money." Let's follow the smart money...

As the folder name states, it contains scripts that automate the detection of chart patterns. Several algorithms can be used to identify chart patterns. We have marked the ones we have used so far:

 - [x] Pivot Points

 - [x] Argrelextrema

 - Kernel Regression

 - Perceptually important points 

 - Directional Change

 - Rolling window 

 - Clustering Algorithms


The idea is to implement all of the above algorithms and produce a Python library called `chart_patterns`. You can check out the YouTube videos discussing the patterns already automated
[here](https://www.youtube.com/@zetratrading/videos).

You can check out the sample outputs below.

### 1. Head and Shoulders Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/head-and-shoulders.png" alt="head-and-shoulders">
  </a>


### 2. Inverse Head and Shoulders Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/inverse-head-and-shoulders.png" alt="inverse-head-and-shoulders">
  </a>

### 3. Triple top and bottom Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/triple-top-and-bottom.png" alt="triple-top-and-bottom">
  </a>

### 4. Rectangle Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/rectangle.png" alt="rectangle">
  </a>

### 5. Wedge Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/wedge.png" alt="wedge">
  </a>


### 6. Flag Patterns

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/flag.png" alt="flag">
  </a>


## MACD
The script looks at the MACD strategy and tests it on 31 currency pairs. There are plenty of videos on YouTube on the MACD strategy. But there have the following in common:

 1. The focus is on a single currency pair.
 
 2. The backtest is applied in one timeframe.

 3. The backtest ends on 100 trades. 


We wanted to improve on this by doing the backtest on multiple currency pairs. On three time frames. And focus on more than 100 trades. You can watch the video [here](https://www.youtube.com/watch?v=RwEEOriVVx8&t=49s).
## Short Content

This folder has code that does not fit in other folders.

### 1. 42Dollars

> Please note this section was written by ChatGPT, Mar 23 version. 

Are you ready to be blown away? This script is not your average run-of-the-mill program. It was inspired by a Reddit post that left many Forex enthusiasts in awe. That's right, we're talking about the one and only 47dollars!

This Reddit user calculated correlations for a whopping [47 currency pairs](https://www.reddit.com/r/Forex/comments/zwr0ck/i_created_a_heat_map_showing_the_correlations/). And we thought that was impressive, until we decided to put our own spin on things. Our script, aptly named 42dollars, consists of 42 carefully selected pairs that will leave your mind boggled.

But wait, there's more! The script goes above and beyond by calculating a rolling correlation for each and every currency pair. That's right, you heard it here first. We're not just talking about static correlations, we're talking about correlations that evolve over time.

And to top it all off, we present to you a stunning heatmap of the results. It's like watching a work of art come to life before your very eyes. So buckle up and prepare to have your mind blown by the incredible power of the 42dollars script!

  <a href="https://github.com/zeta-zetra/code">
    <img src="images/heatmap-all.png" alt="Logo">
  </a>


You can also check out the [YouTube shorts video](https://www.youtube.com/shorts/BOHgtnwbfsY) of the final result. 

### 2. Bullish Candlesticks

This file calculates bullish candlestick patterns. Here are the candlestick patterns:

    - engulfing

    - harami

    - dragonfly doji

    - inverted hammer

    - morningstar

Here is a [YouTube shorts video](https://www.youtube.com/shorts/bV_Oq2U-itA) to the results of the script.      

## Data

The data folder contains any files you will need to replicate the results found from testing, etc. This will usually be forex data
you can download from [Dukascopy](https://www.dukascopy.com/swiss/english/marketwatch/historical/). Please note there is no affiliation with
Dukascopy. 

## License
MIT

## Contact

You can reach me at  - info@zetra.io

## Buy me coffee

If you feel like buying me coffee, here is the [link](https://www.buymeacoffee.com/info90). Thank you. 

## Disclaimer 

We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.