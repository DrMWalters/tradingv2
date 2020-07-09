
#########################
#  ORDERING FUNCTIONS	#
#########################

'''

    orderSymbolsFunc - This function orders the symbols list (input) corresponding to the quoteAssets list.

        Example:
        if quoteAssets = ["BTC", "BNB", "USDT"] then: 
            symbolsForOrdering[0] should be all BTC markets
            symbolsForOrdering[1] should be all BNB markets
            symbolsForOrdering[2] should be all USDT markets

        orderedSymbols = symbolsForOrdering[0] + symbolsForOrdering[1] + symbolsForOrdering[2]

    Returns - List

'''

def orderSymbolsFunc(symbols = [], quoteAssets = []):

	symbolsForOrdering = [[] for i in range(len(quoteAssets))]

	for symbol in symbols:
        # if the current symbols quote asset is one that we are interested in...
		if symbol[2] in quoteAssets:
			i = 0
            # check quote assets and add symbol into ordered list of lists
			for quoteAsset in quoteAssets:
				if symbol[2] == quoteAsset:
					symbolsForOrdering[i].append((symbol[0], symbol[1], symbol[2]))
				i = i + 1

    # convert the list of lists into sigle list (now in order)
	orderedSymbols = []
	for i in range(len(symbolsForOrdering)):
		orderedSymbols.extend(symbolsForOrdering[i])

	return orderedSymbols


#########################
# 	VOLUMN FUNCTIONS	#
#########################

'''

	minVolumnCheck 	 - 	 Checks that the last 5 intervals have a minimium level of volumn

		Example: 
		If period = 5 then this function checks that for the last five intervals there has been at least minVolumn during each of those intervals.

	Returns - bool

'''

def minVolumnCheck(df, period:int = 1, minVolume:float = 1, timeInMinuites:int = 1):

	indexOfLast = len(df['quoteAssetVolume']) - 1
	
	assert period > 0, "period must be greater than 0"
	assert minVolume > 0, "minVolume must be greater than 0"
	assert timeInMinuites > 0, "timeInMinuites must be greater than 0"

	for i in range(indexOfLast - period, indexOfLast):
		if( float(df['quoteAssetVolume'][i])/float(timeInMinuites) < minVolume):
			return False

	return True

'''

	minVolumnCheck 	 - 	 checks the AVERAGE volumn traded over the period (if 0 then for all df) is > minVolumn

		Example: 
		If period = 50 then this function will check that the average quote asset volumn traded (per min) in the last 50 time inetrevals is greater than the minVolumn input 

	Returns - bool

'''


def avgMinVolumnCheck(df, period:int = 0, minVolume:float = 1, timeInMinuites:int = 1):

	indexOfLast = len(df['quoteAssetVolume']) - 1

	if( period <= 0 ):
		period = indexOfLast
	
	assert period > 0, "period must be greater than 0"
	assert minVolume > 0, "minVolume must be greater than 0"
	assert timeInMinuites > 0, "timeInMinuites must be greater than 0"

	averageVolAll = float(df['quoteAssetVolume'].iloc[(indexOfLast - period):indexOfLast].mean())/float(timeInMinuites)

	if(averageVolAll > minVolume):
		return True

	return False

'''

	avgChgBetweenPeriods 	 - 	compares the AVERAGE volumn traded in two periods moving toward the most recent interval.
								For this function to return true both averages of the periods must be > minVolumn and the percentage change between the averages must be > minVolPcntChange

		Example: 
		If firstPeriod = 5 and lastPeriod = 5 and indexOfLast = 200 then:

		Then:
		startPoint = 10
		averageVolPerMinlastPeriod =  average between (indexOfLast - lastPeriod =) 195 and (indexOfLast =) 200
		averageVolPerMinfirstPeriod =  average between (indexOfLast - startPoint = ) 190 and (indexOfLast-lastPeriod =) 195

		Example 2:
		If firstPeriod = 3 and lastPeriod = 8 and indexOfLast = 200 then:

		Then:
		startPoint = 11
		averageVolPerMinlastPeriod =  average between (indexOfLast - lastPeriod =) 192 and (indexOfLast =) 200
		averageVolPerMinfirstPeriod =  average between (indexOfLast - startPoint = ) 189 and (indexOfLast-lastPeriod =) 192
		
		Example 3:
		If firstPeriod = 0 and lastPeriod = 3 and indexOfLast = 200 then:

		Then:
		startPoint = 200
		averageVolPerMinlastPeriod =  average between (indexOfLast - lastPeriod =) 197 and (indexOfLast =) 200
		averageVolPerMinfirstPeriod =  average between (indexOfLast - startPoint = ) 0 and (indexOfLast-lastPeriod =) 197
		


	Returns - bool - In order for this function to return True the following conditions must be satisfied:

						1. averageVolPerMinlastPeriod > minVolumn
						2. averageVolPerMinfirstPeriod > minVolumn
						3. percentage change between averageVolPerMinlastPeriod and averageVolPerMinfirstPeriod > minVolPcntChange

'''

def avgChgBetweenPeriods(	df, 
							firstPeriod:int = 0, 
							lastPeriod:int = 1, 
							minVolume:float = 1, 
							timeInMinuites:int = 1,
							minVolPcntChange:int = 25):

	# calculate average volumn of quote asset over two periods and compare the defference
	# Example:  if firstPeriod == 0 then you are comparing the average volumn traded in the lastPeriod, compared to the
	# average volumn traded in the whole df.

	assert firstPeriod >= 0, "firstPeriod must be greater or equal to 0"
	assert lastPeriod > 0, "lastPeriod must be greater than 0"
	assert minVolume > 0, "minVolume must be greater than 0"
	assert timeInMinuites > 0, "timeInMinuites must be greater than 0"
	

	indexOfLast = len(df['quoteAssetVolume']) - 1
	if( firstPeriod > 0 ):
		startPoint = lastPeriod + firstPeriod
	else:
		startPoint = indexOfLast

	outPut = " startPoint = "+str(startPoint)

	if( indexOfLast >= startPoint):
		averageVolPerMinlastPeriod = float(df['quoteAssetVolume'].iloc[(indexOfLast - lastPeriod):indexOfLast].mean())/float(timeInMinuites)
		averageVolPerMinfirstPeriod = float(df['quoteAssetVolume'].iloc[(indexOfLast - startPoint):(indexOfLast-lastPeriod)].mean())/float(timeInMinuites)
		outPut += "\t First = "+str(averageVolPerMinfirstPeriod)+"\t Last = "+str(averageVolPerMinlastPeriod)
	else:
		return False
	
	diffInAvgVols = (averageVolPerMinlastPeriod - averageVolPerMinfirstPeriod)
	pcntChange = ( diffInAvgVols / averageVolPerMinfirstPeriod ) * 100
	outPut += "\t Per Change = "+str(pcntChange)
	if( averageVolPerMinlastPeriod > minVolume and averageVolPerMinfirstPeriod > minVolume and pcntChange >= minVolPcntChange ):
		return True
	
	return False