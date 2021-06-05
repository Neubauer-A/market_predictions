def add_MACD(df, ema1=12, ema2=26, sigline=9):
  # Add two exponential moving average columns.
  df['EMA'+str(ema1)] = df['Close'].ewm(span=ema1, adjust=False).mean()
  df['EMA'+str(ema2)] = df['Close'].ewm(span=ema2, adjust=False).mean()
  # Add MACD column.
  df['MACD'] = df['EMA'+str(ema1)] - df['EMA'+str(ema2)]
  # Add signal line column.
  df['MACDSignalLine'] = df['MACD'].ewm(span=sigline, adjust=False).mean()
  return df

def add_RSI(df, n=14):
  # Get the daily change in price.
  delta = df['Close'].diff()
  # Get the EMA of increases in price.
  up = delta.clip(lower=0)
  up = up.ewm(com=(n-1), adjust=False).mean()
  # Get the EMA of decreases in price.
  down = -delta.clip(upper=0)
  down = down.ewm(com=(n-1), adjust=False).mean()
  # Calculate RSI.
  df['RSI'] = 100-(100/(1+(up/down)))
  return df

def add_Bollinger(df, n=20):
  # Get the typical price per day.
  tp = (df['Close'] + df['Low'] + df['High'])/3
  # Get the simple moving average of the typical price.
  matp = tp.rolling(n).mean()
  # Add columns of 2 standard deviations above and below the SMA.
  std = tp.rolling(n).std(ddof=0)
  df['BOLU'] = matp + std*2
  df['BOLD'] = matp - std*2
  return df
