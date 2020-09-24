from uuid import uuid1
from decimal import Decimal, getcontext
from yaspin import yaspin

import os
import shutil
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


def dirChange(path, filename, deleteContentsDir = False):

	if(deleteContentsDir == False):
		dir = os.path.join(path,filename)
		if not os.path.exists(dir):
			os.mkdir(dir)

	else:
		folder = path+"\\"+filename
		for filename in os.listdir(folder):
			file_path = os.path.join(folder, filename)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete %s. Reason: %s' % (file_path, e))
	
def Main():

	'''
	Current options:

		FILES:
		"credentialLocation":	string	- location of file containing API keys
		"currentDir": 			string	- should be this directory address
		"outputFile:":			string	- the output file location (currentDir + 'signals/output.txt')
		"outputURLsFile":		string	- the output URLs location (currentDir + 'signals/URLs.txt')
 

		VARIABLES:
		"manualTradingFun"		dict	- current function of manualTranding.py
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

	#clears the URL dir
	dirChange(options['currentDir']+"\\signals", "URLs", True)

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

	if(options['manualTradingFun']['backTesting'] != False):
		symbolsToBeBackTested = []
		with yaspin() as sp:
			print("checking interval")
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

	if(options['manualTradingFun']['strategyURLs'] != False):
		with yaspin() as sp:

			for currentInterval in options['currentIntervals']:

				dirChange(options['currentDir']+"\\signals\\URLs", currentInterval)
				currentDir = options['currentDir']+"\\signals\\URLs\\"+currentInterval

				for symbol in orderedSymbols:

					currentFileStr = "https://www.binance.com/en/trade/pro/"+symbol[1]+"_"+symbol[2]+"\n\n"
					sp.text = "Looking for signals on "+symbol[0]+" ("+currentInterval+")"
					model = TradingModel(symbol[0], currentInterval)
					df = model.df
					mVolume = options['orderedMinVolumeDict'][symbol[2]]
					timeInMins = options['intervals_InMin'][currentInterval]

					if avgMinVolumnCheck(df, 	period = 0,
												minVolume = mVolume, 
												timeInMinuites = timeInMins) != False:
																					
						if( rsiSignal(df, len(df['close']) - 1 ) == 1):	
							f=open(currentDir+"\\rsi.txt", "a+")
							f.write(currentFileStr)
							f.close()

						# if( macdCrossover(df, len(df['close']) - 1 ) == 1):
						# 	f=open(currentDir+"\\macd.txt", "a+")
						# 	f.write(currentFileStr)
						# 	f.close()


						# if( maCrossoverStrategy(df, len(df['close']) - 1 ) != False):
						# 	f=open(currentDir+"\\maCrossover.txt", "a+")
						# 	f.write(currentFileStr)
						# 	f.close()

						# if( float(df['close'].max()) < float(exchange.currentPrice(symbol[0])) ):
						# 	f=open(currentDir+"\\breakout.txt", "a+")
						# 	f.write(currentFileStr)
						# 	f.close()

						
						# if ( currentInterval == "1d" ):
						# 	if (avgChgBetweenPeriods(df, 	firstPeriod = 10, 
						# 									lastPeriod = 1, 
						# 									minVolume = mVolume,
						# 									timeInMinuites = timeInMins,
						# 									minVolPcntChange = 50) != False ):
						# 		f=open(currentDir+"\\volumnSpike.txt", "a+")
						# 		f.write(currentFileStr)
						# 		f.close()
			

	


	

						
		
if __name__ == "__main__":
	Main()
