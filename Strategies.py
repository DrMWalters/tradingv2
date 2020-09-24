from Indicators import Indicators

# But first, because we're not computing the indicators in TradingModel anymore,
# if they don't already exist within the df, we will be computing them here

def emaCrossoverStrategy(df, i:int, fast:int = 50, slow:int = 200, long:bool = True):
	'''
		 Strategy PASS conditions:
			If the value of the prevous fast ema < slow ema AND the current value of fast ema > slow ema	
	
	'''

	if len(df['close']) < slow:
		return False

	fastName = str(fast)+"_ema"
	slowName = str(slow)+"_ema"

	if not df.__contains__(fastName) and not df.__contains__(slowName):
		Indicators.AddIndicator(df, indicator_name="ema", col_name=fastName, args=[fast])
		Indicators.AddIndicator(df, indicator_name="ema", col_name=slowName, args=[slow])

	if i > 0 and df[fastName][i-1] <= df[slowName][i-1] and \
		df[fastName][i] > df[slowName][i]:
		print("############ STRAT IS SUCCESSFUL!! #########")
		print("\t (i-1) values are: fast = "+str(df[fastName][i-1])+" slow = "+str(df[slowName][i-1]))
		print("\t (i) values are: fast = "+str(df[fastName][i])+" slow = "+str(df[slowName][i]))
		print("\t Latest close value was = "+str(df['close'][i]))
		return df['close'][i] 

	return False

def smaCrossoverStrategy(df, i:int, fast:int = 50, slow:int = 200, long:bool = True):
	'''
		 Strategy PASS conditions:
			If the value of the prevous fast sma < slow sma AND the current value of fast sma > slow sma	
	
	'''
	if len(df['close']) < slow:
		return False

	fastName = str(fast)+"_sma"
	slowName = str(slow)+"_sma"

	if not df.__contains__(fastName) and not df.__contains__(slowName):
		Indicators.AddIndicator(df, indicator_name="sma", col_name=fastName, args=[fast])
		Indicators.AddIndicator(df, indicator_name="sma", col_name=slowName, args=[slow])

	if i > 0 and df[fastName][i-1] <= df[slowName][i-1] and \
		df[fastName][i] > df[slowName][i]:
		print("############ STRAT IS SUCCESSFUL!! #########")
		print("\t (i-1) values are: fast = "+str(df[fastName][i-1])+" slow = "+str(df[slowName][i-1]))
		print("\t (i) values are: fast = "+str(df[fastName][i])+" slow = "+str(df[slowName][i]))
		print("\t Latest close value was = "+str(df['close'][i]))
		return df['close'][i] 

	return False

def nearTwoHunEMAStrategy(df, i:int):

	if not df.__contains__('200_ema'):
		Indicators.AddIndicator(df, indicator_name="ema", col_name="200_ema", args=[200])

	if i > 0 and ((abs(df['200_ema'][i] - df['close'][i])*100)/df['200_ema'][i]) < 1:
		return df['close'][i]
	
	return False

def maStrategy(df, i:int):
	''' If price is 10% below the Slow MA, return True'''

	if not df.__contains__('slow_sma'):
		Indicators.AddIndicator(df, indicator_name="sma", col_name="slow_sma", args=[30])

	buy_price = 0.96 * df['slow_sma'][i]
	if buy_price >= df['close'][i]:
		return min(buy_price, df['high'][i])

	return False

def bollStrategy(df, i:int):
	''' If price is 2.5% below the Lower Bollinger Band, return True'''

	if not df.__contains__('low_boll'):
		Indicators.AddIndicator(df, indicator_name="lbb", col_name="low_boll", args=[14])

	buy_price = 0.975 * df['low_boll'][i]
	if buy_price >= df['close'][i]:
		return min(buy_price, df['high'][i])

	return False

# Now, we will write our Ichimoku Strategy. We will follow the one from ChartSchool:

def ichimokuBullish(df, i:int):
	''' If price is above the Cloud formed by the Senkou Span A and B, 
	and it moves above Tenkansen (from below), that is a buy signal.'''

	if not df.__contains__('tenkansen') or not df.__contains__('kijunsen') or \
		not df.__contains__('senkou_a') or not df.__contains__('senkou_b'):
		Indicators.AddIndicator(df, indicator_name="ichimoku", col_name=None, args=None)

	if i - 1 > 0 and i < len(df):
		if df['senkou_a'][i] is not None and df['senkou_b'][i] is not None:
			if df['tenkansen'][i] is not None and df['tenkansen'][i-1] is not None:
				if df['close'][i-1] < df['tenkansen'][i-1] and \
					df['close'][i] > df['tenkansen'][i] and \
					df['close'][i] > df['senkou_a'][i] and \
					df['close'][i] > df['senkou_b'][i]:
						return df['close'][i]
	
	return False

def macdCrossover(df, i:int):

	if not df.__contains__('macd'):
		Indicators.AddIndicator(df,indicator_name="macd", col_name="macd", args=[12 , 26])

	if i > 0:

		# sell signal
		if (df['macd'][i] <= 0 and df['macd'][i-1] >= 0):
			return -1

		# buy signal
		if (df['macd'][i] >= 0 and df['macd'][i-1] <= 0):
			return 1

	return False

def rsiSignal(df, i:int):

	if not df.__contains__('rsi'):
		Indicators.AddIndicator(df, indicator_name='rsi',col_name='rsi', args=[14])

	if i > 0:

		if df['rsi'][i] >= 70:
			return -1
		
		if df['rsi'][i] <= 30:
			return 1
		
	return False

strategies_dict = dict(
	ema_crossover = emaCrossoverStrategy,
	sma_crossover = smaCrossoverStrategy,
	ema200_close = nearTwoHunEMAStrategy,
	ma_simple = maStrategy,
	bollinger_simple = bollStrategy,
	ichimoku_bullish = ichimokuBullish,
)