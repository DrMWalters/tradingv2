import pandas as pd
import requests
import json

import plotly.graph_objs as go
from plotly.offline import plot

from Binance import Binance

class TradingModel:
	
	# We can now remove the code where we're computing the indicators from this class,
	# As we will be computing them in the Strategies class (on a per-need basis)

	def __init__(self, symbol, timeframe:str='4h'):
		self.symbol = symbol
		self.timeframe = timeframe
		self.exchange = Binance()
		self.df = self.exchange.GetSymbolKlines(symbol, timeframe, 1000)
		self.last_price = self.df['close'][len(self.df['close'])-1]

	# We'll look directly in the dataframe to see what indicators we're plotting

	def plotData(self, buy_signals = False, sell_signals = False, plot_title:str="",
	indicators=[
		dict(col_name="slow_ema", color="rgba(0, 0, 255, 50)", name="SLOW EMA"),
		dict(col_name="fast_ema", color="rgba(255, 0, 0, 50)", name="FAST EMA"),
		dict(col_name="slow_sma", color="rgba(51, 51, 255, 50)", name="SLOW SMA"),
		dict(col_name="fast_sma", color="rgba(255, 51, 51, 50)", name="FAST SMA"),   
		dict(col_name="50_ema", color="rgba(255, 51, 0, 50)", name="50 EMA"), 
		dict(col_name="200_ema", color="rgba(0, 51, 255, 50)", name="200 EMA"),
		dict(col_name="low_boll", color="rgba(255, 102, 207, 50)", name="Lower Bollinger Band"),
		dict(col_name="tenkansen", color="rgba(40, 40, 141, 100)", name="Tenkansen"),
		dict(col_name="kijunsen", color="rgba(140, 40, 40, 100)", name="Kijunsen"),
		dict(col_name="senkou_a", color="rgba(160, 240, 160, 100)", name="Senkou A"),
		dict(col_name="senkou_b", color="rgba(240, 160, 160, 50)", name="Senkou B") ]):
		df = self.df

		# plot candlestick chart
		candle = go.Candlestick(
			x = df['time'],
			open = df['open'],
			close = df['close'],
			high = df['high'],
			low = df['low'],
			name = "Candlesticks")

		data = [candle]

		for item in indicators:
			if df.__contains__(item['col_name']):
				trace = go.Scatter(	x = df['time'],
									y = df[item['col_name']],
									name = item['name'],
									line = dict(color = (item['color'])))
				data.append(trace)

		if buy_signals:
			buys = go.Scatter(
					x = [item[0] for item in buy_signals],
					y = [item[1] for item in buy_signals],
					name = "Buy Signals",
					mode = "markers",
					marker_size = 20
				)
			data.append(buys)

		if sell_signals:
			sells = go.Scatter(
				x = [item[0] for item in sell_signals],
				y = [item[1] for item in sell_signals],
				name = "Sell Signals",
				mode = "markers",
				marker_size = 20
			)
			data.append(sells)

		# style and display
		# let's customize our layout a little bit:
		layout = go.Layout(
			title=plot_title,
			xaxis = {
				"title" : self.symbol,
				"rangeslider" : {"visible": False},
				"type" : "date"
			},
			yaxis = {
				"fixedrange" : False,
			})
			
		fig = go.Figure(data = data, layout = layout)

		plot(fig, filename='graphs/'+plot_title+'.html',auto_open=False)
