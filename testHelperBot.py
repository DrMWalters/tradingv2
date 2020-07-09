from uuid import uuid1
from decimal import Decimal, getcontext
from yaspin import yaspin

import json
import pandas as pd
import statistics
import math
import winsound
import time

from Binance import Binance
from StrategyEvaluator import StrategyEvaluator
from Strategies import *
from TradingModel import TradingModel
from BotRunner import *
from functions import *

def BacktestStrategies( symbols=[], 
						intervals=[], 
						plot=False, 
						strategy_evaluators=[], 
						options = dict(starting_balance=100, initial_profits = 1.012, initial_stop_loss = 0.9, incremental_profits = 1.006, incremental_stop_loss = 0.996)):

	for currentInterval in intervals:
		coins_tested = 0
		trade_value = options['starting_balance']
		maxStratName = ""
		maxStratResult = 0
		print("For time interval: ("+currentInterval+").")
		for symbol in symbols:
			print("\t"+symbol[0])
			model = TradingModel(symbol=symbol[0], timeframe=currentInterval)
			for evaluator in strategy_evaluators:
				resulting_balance = evaluator.backtest(
					model,
					starting_balance = options['starting_balance'],
					initial_profits = options['initial_profits'],
					initial_stop_loss = options['initial_stop_loss'],
					incremental_profits = options['incremental_profits'],
					incremental_stop_loss = options['incremental_stop_loss'],
				)

				if( resulting_balance > maxStratResult ):
					maxStratName = evaluator.strategy.__name__
					maxStratResult = resulting_balance

				if resulting_balance != trade_value:
					print("\t"+evaluator.strategy.__name__ 
					+ ": starting balance: " + str(trade_value)
					+ ": resulting balance: " + str(round(resulting_balance, 2)))

					if plot:
						model.plotData(
							buy_signals = evaluator.results[model.symbol]['buy_times'],
							sell_signals = evaluator.results[model.symbol]['sell_times'],
							plot_title = evaluator.strategy.__name__+" on "+model.symbol+"("+model.timeframe+")")
						
					evaluator.profits_list.append(resulting_balance - trade_value)
					evaluator.updateResult(trade_value, resulting_balance)
				
				coins_tested = coins_tested + 1
		
		print("The best strategy for time interval ("+currentInterval+") is:\n"+maxStratName+" with a resulting balance = "+str(round(maxStratResult, 2)))

	# for evaluator in strategy_evaluators:
	# 	print("")
	# 	evaluator.printResults()

# def EvaluateStrategies( symbols=[], 
# 						strategy_evaluators=[], 
# 						interval='1h', 
# 						options = dict(starting_balance=100, initial_profits= 1.012, initial_stop_loss = 0.9, incremental_profits = 1.006, incremental_stop_loss = 0.996)):
						
# 	for symbol in symbols:
# 		print(symbol[0])
# 		model = TradingModel(symbol=symbol[0], timeframe=interval)
# 		for evaluator in strategy_evaluators:
# 			if evaluator.evaluate(model):
# 				print("\n"+evaluator.strategy.__name__+" matched on "+symbol[0])
# 				answer = input()

# 				if answer == 'b':
# 					resulting_balance = evaluator.backtest(
# 						model,
# 						starting_balance=options['starting_balance'],
# 						initial_profits = options['initial_profits'],
# 						initial_stop_loss = options['initial_stop_loss'],
# 						incremental_profits = options['incremental_profits'],
# 						incremental_stop_loss = options['incremental_stop_loss'],
# 					)
# 					model.plotData(
# 						buy_signals = evaluator.results[model.symbol]['buy_times'],
# 						sell_signals = evaluator.results[model.symbol]['sell_times'],
# 						plot_title=evaluator.strategy.__name__+" matched on "+symbol
# 					)

def printAverageVolume(df, symbol, currentInterval, options, outputFile):
	indexOfLast = len(df['quoteAssetVolume']) - 1
	averageVolPerMinAll = float(df['quoteAssetVolume'].mean())/float(options['intervals_InMin'][currentInterval])
	outputFile.write('"'+symbol[1]+'":\t\t'+str(averageVolPerMinAll)+',\n')

	
def Main():

	'''
	Current options:

		FILES:
		"credentialLocation":	string	- location of file containing API keys
		"currentDir": 			string	- should be this directory address
		"outputFile:":			string	- the output file location (currentDir + 'signals/output.txt')
		"outputURLsFile":		string	- the output URLs location (currentDir + 'signals/URLs.txt')
 

		VARIABLES:
		"currentIntervals"		list	- current time intervals we are interested in
		"orderedMinVolumeDict"	dict	- coins and a corresponding minimum average volumn (per minuite)
										  the ordering is important and any quote assets we want to consider must first be added to this...
		"quoteAssets"			list	- quote assets that we want to consider
		"baseAssets"			list	- base assets that we want to consider
		"minPeriod"				int		- the minimuim period/length of any df downloaded from the exchange (i.e. this number 										  should be >= than the highest ema/sma etc)

		CONSTANTS:
		"intervals_InMin"		dict	- all time intervals in minuites

	'''

	options = {}
	try:
		with open('options.json') as json_file:
			options = json.load(json_file)
	except Exception as e:
		print("Exception occured when trying to access options.json")
		print(e)

	sp = yaspin()
	exchange = Binance(filename = options['credentialLocation'])

	symbols = exchange.GetTradingSymbols(quoteAssets=options['quoteAssets'], baseAssets=options['baseAssets'])

	outputFile = open(options['currentDir']+options['outputFile'], "w")
	outputURLs = open(options['currentDir']+options['outputURLsFile'], "w")
	# currentVolURLsFile = open(currentFileStr+"\\signals\\minVol_URLs.txt", "w")
	# currentNearEMAURLsFile = open(currentFileStr+"\\signals\\nearEMA_URLs.txt", "w")

	# reset all the currentBaseAsset files 
	# btcSymbolFile = open(currentFileStr+"\\signals\\BTC_URLs.txt", "w")
	# bnbSymbolFile = open(currentFileStr+"\\signals\\BNB_URLs.txt", "w")

	orderedSymbols = orderSymbolsFunc(symbols, list(options['orderedMinVolumeDict'].keys()))
	database = BotDatabase(options['database'])
	prog = BotRunner(sp, exchange, database)

	backTesting = False
	if(backTesting == True):
		symbolsToBeBackTested = []
		with yaspin() as sp:
			currentInterval = "1h"
			for symbol in orderedSymbols:
				outputText = ""
				if symbol[2] in options['quoteAssets']:
					currentURLStr = "https://www.binance.com/en/trade/pro/"+symbol[1]+"_"+symbol[2]+"\n\n"
		

					model = TradingModel(symbol[0], currentInterval)
					df = model.df
					
					if len(df['close']) > options['minPeriod'] and avgMinVolumnCheck(	df, period = 0,
																						minVolume = options['orderedMinVolumeDict'][symbol[2]], 
																						timeInMinuites = options['intervals_InMin'][currentInterval]) != False:
						symbolsToBeBackTested.append(symbol)
		
			strategy_evaluators = []
			for strat in options["btStrategies"]:
				strategy_evaluators.append(StrategyEvaluator(strategy_function=strategies_dict[strat]))


			sp.stop()
			BacktestStrategies(symbols=symbols, intervals=options["currentIntervals"], plot=True, strategy_evaluators=strategy_evaluators, options = options["btInitialOptions"])
			sp.start()
	
	order_id = str(uuid1())
	# buy at 0.4% lower than current price
	# q_qty = Decimal(bot_params['trade_allocation'])
	# buy_price = exchange.RoundToValidPrice(
	# 	symbol_data = symbol_data, 
	# 	desired_price = Decimal(df['close'][i]) * Decimal(1.01))
	# quantity = exchange.RoundToValidQuantity(
	# 	symbol_data = symbol_data, 
	# 	desired_quantity = q_qty / buy_price)

	# desired_price and quantity using only Decimals

	buy_price = 0.0016999
	quantity = 1.19

	order_params = dict(
		symbol = "BNBBTC",
		side = "BUY",
		type = "LIMIT",
		timeInForce = "GTC",
		price = format(buy_price, 'f'),
		quantity = format(quantity, 'f'),
		newClientOrderId = order_id)

	prog.PlaceOrder(order_params, False)


	

						
		
if __name__ == "__main__":
	Main()
