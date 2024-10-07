# Key principles to identify trends by comparing short-term and long-term simple moving averages (SMA):
# 1. Key Rule of Thumb:
#    Ensure the ratio of short-term to long-term SMAs is in range of 0.25 - 0.50
#    (e.g., a 10-day vs. 50-day SMA).

# 2. Upper Limit for Long-term SMAs:
#    200 days is often used as the maximum.

# 3. Minimum for Short-term SMAs:
#    10 days is generally a good baseline to filter out short-term noise.

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
warnings.simplefilter(action="ignore", category=FutureWarning)

end_date = datetime.now()
start_date = end_date - timedelta(days=1825)

# Input desired asset
asset = str(input("Assets' Ticker:", ))
data = yf.download(asset, start=start_date, end=end_date)


# Set the scope
short_terms = range(10, 51)
long_terms = range(50, 201)

# Initialize results list
results = []


for short in short_terms:
    for long in long_terms:
        # Key Rule of Thumb
        if 0.50 >= short / long >= 0.25:
            # Define profit
            data['Profit'] = data['Close'] - data['Close'].shift(1)
            
            # Calculate Simple Moving Averages
            data['SMA_short'] = data['Close'].rolling(window = short).mean()
            data['SMA_long'] = data['Close'].rolling(window = long).mean()

            # Create a mask for when the short SMA is above the long SMA
            mask = data['SMA_short'] > data['SMA_long']

            # Apply the mask and calculate profit for only those rows
            df = data[mask].copy()

            # Calculate the culmulative profit
            df['Cumulative Profit'] = df['Profit'].cumsum()

            # Ensure df is not empty before accessing the last row
            if not df.empty:
                total_return = df['Cumulative Profit'].iloc[-1]
            else:
                total_return = 0  # In case there's no valid data in df

            # Append the results
            results.append((short, long, total_return))


# Return the SMA pair with greatest cumulative profit
if results:
    best_pair = max(results, key=lambda x: x[2])
    short_term, long_term, total_return = best_pair

    #Format the output for better readability
    print(f"Best Moving Average Pair")
    print(f"Short: {short_term}-day")
    print(f"Long: {long_term}-day")
    print(f"Total Return: ${total_return}")


# Test the Strategy
test = yf.download(asset, start=start_date, end=end_date)


# Calculate the Best Pair Simple Moving Averages
test['Best Pair Short SMA'] = test['Close'].rolling(best_pair[0]).mean()
test['Best Pair Long SMA'] = test['Close'].rolling(best_pair[1]).mean()

# Generate signals for the Best Pair Strategy
test['Best Pair Shares'] = (test['Best Pair Short SMA'] > test['Best Pair Long SMA']).astype(int)
test['Best Pair Previous Close'] = test['Close'].shift(1)
test['Best Pair Profit'] = (test['Close'] - test['Best Pair Previous Close']) * test['Best Pair Shares']
test['Best Pair Wealth'] = test['Best Pair Profit'].cumsum()


# Calculate the 50-200 Simple Moving Averages
test['SMA50'] = test['Close'].rolling(50).mean()
test['SMA200'] = test['Close'].rolling(200).mean()

#Generate signals for the 50-200 SMA Strategy
test['SMA50-200 Shares'] = (test['SMA50'] > test['SMA200']).astype(int)
test['SMA50-200 Previous Close'] = test['Close'].shift(1)
test['SMA50-200 Profit'] = (test['Close'] - test['SMA50-200 Previous Close']) * test['SMA50-200 Shares']
test['SMA50-200 Wealth'] = test['SMA50-200 Profit'].cumsum()


# Calculate Buy and Hold Asset Growth
test['Buy and Hold Asset Growth'] = test['Open'].shift(-1) - test['Open']


# Plotting the results
plt.figure(figsize=(14, 7))
plt.plot(test['Best Pair Wealth'].values, color='green', label=f'SMA{best_pair[0]}-{best_pair[1]} Strategy')
plt.plot(test['SMA50-200 Wealth'].values, color='blue', label='SMA50-200 Strategy')
plt.plot(test['Buy and Hold Asset Growth'].cumsum().values, color='red', label='Buy and Hold Strategy')

# Chart aesthetics
plt.title(f"Trading Strategy Comparison of {asset}")
plt.xlabel('Date')
plt.ylabel('Cumulative Wealth')
plt.legend()
plt.grid()
plt.show()
