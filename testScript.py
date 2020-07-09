from decimal import Decimal

def Main():
    numToChange = Decimal("30")
    newNum = numToChange
    percentageChg = Decimal("10")

    percentageChgSgn = percentageChg.as_tuple().sign
    percentageChgDig = percentageChg.as_tuple().digits
    percentageChgExp = percentageChg.as_tuple().exponent

    numToChangeDig = numToChange.as_tuple().digits
    numToChangeExp = numToChange.as_tuple().exponent
    
    hunPercent = (percentageChgSgn, numToChangeDig, numToChangeExp - 2)
    thoPercent = (percentageChgSgn, numToChangeDig, numToChangeExp - 3)
    tenThoPer  = (percentageChgSgn, numToChangeDig, numToChangeExp - 4)

    percentageChgIntValue = abs(int(percentageChg))

    if percentageChgIntValue > 0:
        for i in range(percentageChgIntValue):
            newNum = newNum + Decimal(hunPercent)
    
    if percentageChgExp < 0 and percentageChgExp > -3:
        temppchg = int(percentageChgExp)
        while temppchg < 0:

            if temppchg == -1:
                chg = thoPercent
            elif temppchg == -2:
                chg = tenThoPer

            for i in range(percentageChgDig[(len(percentageChgDig) + temppchg)]):
                newNum = newNum + Decimal(chg)
            temppchg = temppchg + 1

    print(newNum)

    # if abs(decExp) < 4:
    #     decTuple = percentage.as_tuple().digits

    #     if decTuple[0] == 0:
    #         sgn = -1
    #     elif decTuple[0] == 1:
    #         sgn = 1

    #     if abs(decExp) == 1:
            
    #     elif abs(decExp) == 2:
        
    #     elif abs(decExp) == 3:
    # percentage.as_tuple().exponent = percentage.as_tuple().exponent - 1




if __name__ == '__main__':
	Main()