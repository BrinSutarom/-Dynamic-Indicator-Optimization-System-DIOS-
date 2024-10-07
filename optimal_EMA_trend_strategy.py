# Key principles to identify trends by comparing short-term and long-term exponential moving averages (EMA): 
# 1. Key Rule of Thumb:
#    Ensure the ratio of short-term to long-term EMAs is in range of 0.25 - 0.50
#    (e.g., a 10-day vs. 50-day EMA).
 
# 2. Upper Limit for Long-term EMAs:
#    200 days is often used as the maximum.

# 3. Minimum for Short-term EMAs:
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


# Loop through the short and long terms EMAs combination
for short in short_terms:
    for long in long_terms:
        # Key Rule of Thumb
        if 0.50 >= short / long >= 0.25:
            # Define profit
            data['Profit'] = data['Close'] - data['Close'].shift(1)
            
            # Calculate Exponential Moving Averages
            data['EMA_short'] = data['Close'].ewm(span=short, adjust=False).mean()
            data['EMA_long'] = data['Close'].ewm(span=long, adjust=False).mean()

            # Create a mask for when the short EMA is above the long EMA
            mask = data['EMA_short'] > data['EMA_long']

            # Apply the mask and create a new DataFrame for valid signals
            df = data[mask].copy()

            # Calculate cumulative profit
            df['Cumulative Profit'] = df['Profit'].cumsum()

            # Ensure df is not empty before accessing the last row
            if not df.empty:
                total_return = df['Cumulative Profit'].iloc[-1]  # Get total return from last valid signal
            else:
                total_return = 0  # No valid data in df

            # Append the results
            results.append((short, long, total_return))


  # Return the EMA pair with greatest cumulative profit
if results:
    best_pair = max(results, key=lambda x: x[2])
    short_term, long_term, total_return = best_pair

    #Format the output for better readability
    print(f"Best Exponential Moving Average Pair")
    print(f"Short: {short_term}-day")
    print(f"Long: {long_term}-day")
    print(f"Total Return: ${total_return}")


# Test the Strategy
test = yf.download(asset, start=start_date, end=end_date)


# Calculate the Best Pair Exponential Moving Averages
test['Best Pair Short EMA'] = test['Close'].ewm(span=best_pair[0], adjust=False).mean()
test['Best Pair Long EMA'] = test['Close'].ewm(span=best_pair[1], adjust=False).mean()

# Generate signals for the Best Pair Strategy
test['Best Pair Shares'] = (test['Best Pair Short EMA'] > test['Best Pair Long EMA']).astype(int)
test['Best Pair Previous Close'] = test['Close'].shift(1)
test['Best Pair Profit'] = (test['Close'] - test['Best Pair Previous Close']) * test['Best Pair Shares']
test['Best Pair Wealth'] = test['Best Pair Profit'].cumsum()


# Calculate the 50-200 Exponential Moving Averages
test['EMA50'] = test['Close'].ewm(span=50, adjust=False).mean()
test['EMA200'] = test['Close'].ewm(span=200, adjust=False).mean()

# Generate signals for the 50-200 EMA Strategy
test['EMA50-200 Shares'] = (test['EMA50'] > test['EMA200']).astype(int)
test['EMA50-200 Previous Close'] = test['Close'].shift(1)
test['EMA50-200 Profit'] = (test['Close'] - test['EMA50-200 Previous Close']) * test['EMA50-200 Shares']
test['EMA50-200 Wealth'] = test['EMA50-200 Profit'].cumsum()


# Calculate Buy and Hold Asset Growth
test['Buy and Hold Asset Growth'] = test['Open'].shift(-1) - test['Open']


# Plotting the results
plt.figure(figsize=(14, 7))
plt.plot(test['Best Pair Wealth'].values, color='green', label=f'EMA{best_pair[0]}-{best_pair[1]} Strategy')
plt.plot(test['EMA50-200 Wealth'].values, color='blue', label='EMA50-200 Strategy')
plt.plot(test['Buy and Hold Asset Growth'].cumsum().values, color='red', label='Buy and Hold Strategy')

# Chart aesthetics
plt.title(f"Trading Strategy Comparison of {asset}")
plt.xlabel('Date')
plt.ylabel('Cumulative Wealth')
plt.legend()
plt.grid()
plt.show()
