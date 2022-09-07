
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn")
import yfinance as yf
import streamlit as st


st.set_page_config(page_title = 'Backtester',page_icon = ":back:", layout= "wide")

#---- HEADER SECTION ----
with st.container():
    st.subheader("Hi, :wave:")
    st.title("Bollinger Bands Backtester")
    st.write("This Web App backtests the bollinger bands mean reversion strategy on different currencies over a ten year period from 2012-01-01 to 2021-12-31.","[Learn More >](https://www.investopedia.com/trading/using-bollinger-bands-to-gauge-trends/#:~:text=Bollinger%20Bands%C2%AE%20are%20a%20trading%20tool%20used%20to%20determine,lot%20of%20other%20relevant%20information.)")
    st.write("This base app will evolve to include optimization, and leverage, after which forward testing will be performed from 2021-12-21 to current date.")


with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("Backtester configurations")
        st.write("##")
        st.write(
            """
            -Moving Average Window: 30  \n
            -Standard Deviation: 2  \n
            -Data Granularity: 1 Day  \n

        
        
        
        
        
        
        
            """
        )


currency_pairs = ["EURUSD", "USDJPY", "AUDUSD","GBPUSD","USDCAD", "NZDUSD","ZARUSD","AUDCAD","AUDJPY","CADJPY", "CHFJPY","EURAUD","EURCAD","GBPJPY" ]
symbol = st.sidebar.selectbox("Select Currency Pair: ", currency_pairs)


#price = st.sidebar.selectbox("Select currency pair", currency_pairs)
data= yf.download(symbol+"=X", start="2012-01-01", end="2021-12-31")
data= data.drop(columns=['Open','High','Low','Adj Close','Volume']).copy()


data.columns=["price"]



data["returns"] = np.log(data.div(data.shift(1)))

SMA = 30
dev = 2

data["SMA"] = data["price"].rolling(SMA).mean()
data["Lower"] = data["SMA"] - data["price"].rolling(SMA).std() * dev # Lower Band -2 Std Dev
data["Upper"] = data["SMA"] + data["price"].rolling(SMA).std() * dev # Upper Band -2 Std Dev

data.drop(columns = "returns").plot(figsize = (12, 8))
plt.show()

data.dropna(inplace = True)

data["distance"] = data.price - data.SMA # helper Column
data["position"] = np.where(data.price < data.Lower, 1, np.nan) # 1. oversold -> go long
data["position"] = np.where(data.price > data.Upper, -1, data["position"]) # 2. overbought -> go short
# 3. crossing SMA ("Middle Band") -> go neutral
data["position"] = np.where(data.distance * data.distance.shift(1) < 0, 0, data["position"])

data["position"] = data.position.ffill().fillna(0) # where 1-3 isn´t applicable -> hold previous position

data["strategy"] = data.position.shift(1) * data["returns"]
data.dropna(inplace = True)
data["creturns"] = data["returns"].cumsum().apply(np.exp)
data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)

fig_1 = data[["creturns", "cstrategy"]]#plot(figsize = (12 , 8))
#plt.show()

st. line_chart(fig_1)



ptc = 0.00007
data["trades"] = data.position.diff().fillna(0).abs()
data["strategy_net"] = data.strategy - data.trades * ptc
data["cstrategy_net"] = data.strategy_net.cumsum().apply(np.exp)


fig_2 =data[["creturns", "cstrategy", "cstrategy_net"]]#plot(figsize = (12 , 8))


st.line_chart(fig_2)
st.caption("creturns = Buy and hold returns,     cstrategy =  Strategy returns,   cstrategy_net = Strategy returns after trading costs",)

cummulative_return = round(data.strategy_net.mean() * (252)*100, 3) # annualized return
cummulative_risk = round(data.strategy_net.std() * np.sqrt(252) *100, 3)  # annualized risk
st.write("Annualized return |",cummulative_return, "%")
st.write("Annualized risk |",cummulative_risk, "%")

mu = data.cstrategy_net.mean() # arithmetic mean return -> Reward
ma = data.cstrategy_net.std()

Reward = ""
Risk = ""

if mu > 1:
    reward = round((mu-1)*100, 3)
    st.write("Reward | ", reward,"%")
elif mu < 1:
    reward = round((mu-1)*100, 3)
    st.write("Reward | ", reward,"%")




if ma > 1:
    Risk = round((ma-1)*100, 3)
    st.write("Risk | ", Risk,"%")
elif ma < 1: 
    Risk = round((ma)*100, 3)
    st.write("Risk | ", Risk,"%")

st.write("Reward is the arithmetic mean return, while risk is the volatility of returns or standard deviation of returns.")

















