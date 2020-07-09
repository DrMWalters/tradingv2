To do
    - volumn check need to be average over all time... (need to research this)
    - testHelperBot - pick strategys based on best back tested results 

    - write function that takes symbol and returns avg price, but prints it into json format into file
    - convert all floats to decimal/strings
    - write bot/program that follows a manual trade and can edit the stop_loss/target price if nessasary


Seperate check functions:
    - checkValueTol(Tolerance)

Additional:
    - database with exchange constants (precision, min qualtity etc)



########################
#       OPTIONS        #
########################

Current options.json:

FILES:
"credentialLocation":	string	- location of file containing API keys
"currentDir": 			string	- should be this directory address
"database":             string  - location of database
"outputFile:":			string	- the output file location (currentDir + 'signals/output.txt')
"outputURLsFile":		string	- the output URLs location (currentDir + 'signals/URLs.txt')


VARIABLES:
"currentIntervals"		list	- current time intervals we are interested in
"orderedMinVolumeDict"	dict	- coins and a corresponding minimum average volumn (per minuite)
                                  the ordering is important and any quote assets we want to consider must first be added to this...

"quoteAssets"			list	- quote assets that we want to consider
"baseAssets"			list	- base assets that we want to consider
"minPeriod"				int		- the minimuim period/length of any df downloaded from the exchange (i.e. this number 										          should be >= than the highest ema/sma etc)

"btInitialOptions"           dict    - 
"btStrategies"

CONSTANTS:
"intervals_InMin"		dict	- all time intervals in minuites