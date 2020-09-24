import time
import json
import winsound

from requests import exceptions 

from uuid import uuid1
from decimal import Decimal, getcontext
from yaspin import yaspin
from Binance import Binance

from multiprocessing.pool import ThreadPool as Pool
from functools import partial
from Database import BotDatabase

from TradingModel import TradingModel

from Strategies import *
from functions import *

class TradingAlgorithm:

	def __init__(self, sp, exchange, database):
		self.sp = sp
		self.exchange = exchange
		self.database = database
		self.update_balance = True
		self.ask_permission = True

def Main():

	sp = yaspin()


	options = {}
	try:
		with open('options.json') as json_file:
			options = json.load(json_file)
	except Exception as e:
		print("Exception occured when trying to access options.json")
		print(e)
	
	exchange = Binance(filename = options['credentialLocation'])
	database = BotDatabase(options['database'])
	prog = TradingAlgorithm(sp, exchange, database)

	print("It works!")


if __name__ == "__main__":
	Main()

