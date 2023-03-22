from numba import jit

@jit(nopython=True)
def backtesting(input_arr, fund=100, leverage=0, takerFee=0.0004, 
                slippage=0.0001, stopLoss_slippageAdd=0.001,
                exit_timeOut=False, exParam1=20, from_exit_condition=False,
                exit_profitOut=False, exParam2=0.02,
                exit_lossOut=False, lossOut_condition=1, exParam3=0.05, 
                price_trigger3='HL', risk_control=False, rc_percent=0.5,
                exit_condition=1, exParam0=0, price_trigger0='HL'
                ):

    '''
    - vol_arr, you should input ATR or standard deviation (not volume!!)
    - leverage = 0, order with equal amount $fund
    - when exit_condition=1 & exParam0=0, there's no exit condition
    '''

    open_arr = input_arr[0]
    high_arr = input_arr[1]
    low_arr = input_arr[2]
    close_arr = input_arr[3]
    entryLong_arr = input_arr[4]
    entrySellShort_arr = input_arr[5]
    exitShort_arr = input_arr[6]
    exitBuyToCover_arr = input_arr[7]
    vol_arr = input_arr[8]

    LS = ''
    buy = []
    sell = []
    sellshort = []
    buytocover = []
    profit_list = [0]
    profit_fee_list = [0]
    profit_list_realized = [0]
    profit_fee_list_realized = [0]
    profit_fee_list_realized_time = [0]

    fund_money = fund
    feeRate = takerFee + slippage
    stopLoss_feeRate = takerFee + slippage + stopLoss_slippageAdd
    
    endPointHigh_C = close_arr[0]
    endPointHigh_H = close_arr[0]
    endPointLow_C = close_arr[0]
    endPointLow_L = close_arr[0]
    exitSwitch = False
    stopLoss = False
    stopProfit = False
    stopTime = False
    riskControlSwitch = False
    ts = 1
    ts2 = 1
    t = 0
    exT = 0

    for i in range(len(open_arr)):

        if i == len(open_arr)-1:
            break

        if exit_lossOut == True and lossOut_condition == 4:
            if i < exParam3:
                profit_list.append(0)
                profit_fee_list.append(0)
                continue

        # stop time condition
        if exit_timeOut == True:
            if from_exit_condition == False:
                if ts >= exParam1:
                    stopTime = True
                else:
                    stopTime = False
            else:
                if exitSwitch == True:
                    if ts2 > exParam1:
                        stopTime = True
                else:
                    stopTime = False

        # stop profit condition
        if exit_profitOut == True:
            if exitSwitch == True:
                if LS == 'L':
                    stopProfit = high_arr[i] >= open_arr[exT] * (1+exParam2)
                    if stopProfit:
                        exitPrice = open_arr[exT] * (1+exParam2)
                elif LS == 'S':
                    stopProfit = low_arr[i] <= open_arr[exT] * (1-exParam2)
                    if stopProfit:
                        exitPrice = open_arr[exT] * (1-exParam2)
                else:
                    stopProfit = False

        # stop loss condition
        if exit_lossOut == True:
            if exitSwitch == True:

                if lossOut_condition == 1:
                    if LS == 'L':
                        stopLoss = low_arr[i] <= open_arr[exT] * (1-exParam3)
                        if stopLoss:
                            exitPrice = open_arr[exT] * (1-exParam3)
                    elif LS == 'S':
                        stopLoss = high_arr[i] >= open_arr[exT] * (1+exParam3)
                        if stopLoss:
                            exitPrice = open_arr[exT] * (1+exParam3)
                    else:
                        stopLoss = False

                elif lossOut_condition == 2:
                    if LS == 'L':
                        if price_trigger3 == 'C':
                            stopLoss = low_arr[i] <= endPointHigh_C * (1-exParam3)
                            if stopLoss:
                                exitPrice = endPointHigh_C * (1-exParam3)
                        elif price_trigger3 == 'HL':
                            stopLoss = low_arr[i] <= endPointHigh_H * (1-exParam3)
                            if stopLoss:
                                exitPrice = endPointHigh_H * (1-exParam3)
                    elif LS == 'S':
                        if price_trigger3 == 'C':
                            stopLoss = high_arr[i] >= endPointLow_C * (1+exParam3)
                            if stopLoss:
                                exitPrice = endPointLow_C * (1+exParam3)
                        elif price_trigger3 == 'HL':
                            stopLoss = high_arr[i] >= endPointLow_L * (1+exParam3)
                            if stopLoss:
                                exitPrice = endPointLow_L * (1+exParam3)
                    else:
                        stopLoss = False

                elif lossOut_condition == 3:
                    if LS == 'L':
                        if price_trigger3 == 'C':
                            stopLoss = low_arr[i] <= endPointHigh_C - exParam3*vol_arr[exT-1]
                            if stopLoss:
                                exitPrice = endPointHigh_C - exParam3*vol_arr[exT-1]
                        elif price_trigger3 == 'HL':
                            stopLoss = low_arr[i] <= endPointHigh_H - exParam3*vol_arr[exT-1]
                            if stopLoss:
                                exitPrice = endPointHigh_H - exParam3*vol_arr[exT-1]
                    elif LS == 'S':
                        if price_trigger3 == 'C':
                            stopLoss = high_arr[i] >= endPointLow_C + exParam3*vol_arr[exT-1]
                            if stopLoss:
                                exitPrice = endPointLow_C + exParam3*vol_arr[exT-1]
                        elif price_trigger3 == 'HL':
                            stopLoss = high_arr[i] >= endPointLow_L + exParam3*vol_arr[exT-1]
                            if stopLoss:
                                exitPrice = endPointLow_L + exParam3*vol_arr[exT-1]
                    else:
                        stopLoss = False

                elif lossOut_condition == 4:
                    if LS == 'L':
                        if price_trigger3 == 'C':
                            stopLoss = low_arr[i] <= min(close_arr[i-exParam3:i])
                            if stopLoss:
                                exitPrice = min(close_arr[i-exParam3:i])
                        elif price_trigger3 == 'HL':
                            stopLoss = low_arr[i] <= min(low_arr[i-exParam3:i])
                            if stopLoss:
                                exitPrice = min(low_arr[i-exParam3:i])
                    elif LS == 'S':
                        if price_trigger3 == 'C':
                            stopLoss = high_arr[i] >= max(close_arr[i-exParam3:i])
                            if stopLoss:
                                exitPrice = max(close_arr[i-exParam3:i])
                        elif price_trigger3 == 'HL':
                            stopLoss = high_arr[i] >= max(high_arr[i-exParam3:i])
                            if stopLoss:
                                exitPrice = max(high_arr[i-exParam3:i])
                    else:
                        stopLoss = False

                ## when touch stopLoss, control risk after next trade
                if LS != '' and risk_control == True and stopLoss == True:
                    riskControlSwitch = True

        # start exit condition
        if LS != '' and exitSwitch == False:

            if exit_condition == 1:
                if ts >= exParam0:
                    exitSwitch = True

            elif exit_condition == 2:
                if price_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                elif price_trigger0 == 'HL':
                    if LS == 'L':
                        if high_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if low_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
        
            elif exit_condition == 3:
                if price_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
                elif price_trigger0 == 'HL':
                    if LS == 'L':
                        if high_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if low_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
            
            elif exit_condition == 4:
                if price_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                elif price_trigger0 == 'HL':
                    if LS == 'L':
                        if low_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if high_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True

            elif exit_condition == 5:
                if price_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                elif price_trigger0 == 'HL':
                    if LS == 'L':
                        if low_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if high_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True

            elif exit_condition == 6:
                if vol_arr[i] >= exParam0*vol_arr[t-1]:
                    exitSwitch = True

            if exitSwitch == True:
                exT = i+1
                endPointHigh_C = close_arr[i]
                endPointHigh_H = close_arr[i]
                endPointLow_C = close_arr[i]
                endPointLow_L = close_arr[i]

        # no position
        if LS == '':
            profit_list.append(0)
            profit_fee_list.append(0)
            
            if entryLong_arr[i] == True:
                LS = 'L'
                t = i+1
                buy.append(t)

            elif entrySellShort_arr[i] == True:
                LS = 'S'
                t = i+1
                sellshort.append(t)

            if entryLong_arr[i] == True or entrySellShort_arr[i] == True:
                profit_list_realized.append(0)
                profit_fee_list_realized.append(0)
                profit_fee_list_realized_time.append(t)

                if riskControlSwitch == False:
                    if leverage == 0:
                        orderMoney = fund_money
                    else:
                        orderMoney = fund * leverage
                elif riskControlSwitch == True:
                    if leverage == 0:
                        orderMoney = fund_money * rc_percent
                    else:
                        orderMoney = fund * leverage * rc_percent

                orderSize = orderMoney / open_arr[i+1]

                ts = 1
                ts2 = 1
                exitSwitch = False

                if exit_condition == 1 and exParam0 == 0:
                    exitSwitch = True
                    exT = i+1
                    endPointHigh_C = close_arr[i]
                    endPointHigh_H = close_arr[i]
                    endPointLow_C = close_arr[i]
                    endPointLow_L = close_arr[i]
                    ts2 += 1

        # long position
        elif LS == 'L':
            if stopLoss or stopProfit:
                profit = orderSize * (exitPrice - open_arr[i])
            else:
                profit = orderSize * (open_arr[i+1] - open_arr[i])
            profit_list.append(profit)
            ts += 1

            if exitSwitch == True:
                ts2 += 1
                if close_arr[i] > endPointHigh_C:
                    endPointHigh_C = close_arr[i]
                if high_arr[i] > endPointHigh_H:
                    endPointHigh_H = high_arr[i]
                if close_arr[i] < endPointLow_C:
                    endPointLow_C = close_arr[i]
                if low_arr[i] < endPointLow_L:
                    endPointLow_L = low_arr[i]

            if exitShort_arr[i] == True or i == len(open_arr)-2 or stopLoss or stopProfit or stopTime: 
                if stopLoss or stopProfit:
                    pl_round = orderSize * (exitPrice - open_arr[t])
                    if stopLoss:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                    else:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                else:
                    pl_round = orderSize * (open_arr[i+1] - open_arr[t])
                    profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                
                profit_fee_list.append(profit_fee)
                sell.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
                if stopLoss:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                else:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                fund += profit_fee_realized

                profit_list_realized.append(profit_realized)
                profit_fee_list_realized.append(profit_fee_realized)
                profit_fee_list_realized_time.append(i+1)

                # close riskControlSwitch
                if riskControlSwitch == True and profit_fee_realized > 0:
                    riskControlSwitch = False

                # reset stop condition
                exitSwitch = False
                stopLoss = False
                stopProfit = False
                stopTime = False
                ts = 1
                ts2 = 1

                if entrySellShort_arr[i] == False:
                    LS = ''
                
                ## turn over
                elif entrySellShort_arr[i] == True:
                    LS = 'S'
                    t = i+1
                    sellshort.append(t)

                    if riskControlSwitch == False:
                        if leverage == 0:
                            orderMoney = fund_money
                        else:
                            orderMoney = fund * leverage
                    elif riskControlSwitch == True:
                        if leverage == 0:
                            orderMoney = fund_money * rc_percent
                        else:
                            orderMoney = fund * leverage * rc_percent

                    orderSize = orderMoney / open_arr[i+1]

                    if exit_condition == 1 and exParam0 == 0:
                        exitSwitch = True
                        exT = i+1
                        endPointHigh_C = close_arr[i]
                        endPointHigh_H = close_arr[i]
                        endPointLow_C = close_arr[i]
                        endPointLow_L = close_arr[i]
                        ts2 += 1

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)

        # short position
        elif LS == 'S':
            if stopLoss or stopProfit:
                profit = orderSize * (open_arr[i] - exitPrice)
            else:
                profit = orderSize * (open_arr[i] - open_arr[i+1])
            profit_list.append(profit)
            ts += 1

            if exitSwitch == True:
                ts2 += 1
                if close_arr[i] > endPointHigh_C:
                    endPointHigh_C = close_arr[i]
                if high_arr[i] > endPointHigh_H:
                    endPointHigh_H = high_arr[i]
                if close_arr[i] < endPointLow_C:
                    endPointLow_C = close_arr[i]
                if low_arr[i] < endPointLow_L:
                    endPointLow_L = low_arr[i]

            if exitBuyToCover_arr[i] == True or i == len(open_arr)-2 or stopLoss or stopProfit or stopTime: 
                if stopLoss or stopProfit:
                    pl_round = orderSize * (open_arr[t] - exitPrice)
                    if stopLoss:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                    else:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                else:
                    pl_round = orderSize * (open_arr[t] - open_arr[i+1])
                    profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                
                profit_fee_list.append(profit_fee)
                buytocover.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
                if stopLoss:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                else:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                fund += profit_fee_realized

                profit_list_realized.append(profit_realized)
                profit_fee_list_realized.append(profit_fee_realized)
                profit_fee_list_realized_time.append(i+1)

                # close riskControlSwitch
                if riskControlSwitch == True and profit_fee_realized > 0:
                    riskControlSwitch = False

                # reset stop condition
                exitSwitch = False
                stopLoss = False
                stopProfit = False
                stopTime = False
                ts = 1
                ts2 = 1

                if entryLong_arr[i] == False:
                    LS = ''

                ## turn over
                elif entryLong_arr[i] == True:
                    LS = 'L'
                    t = i+1
                    buy.append(t)

                    if riskControlSwitch == False:
                        if leverage == 0:
                            orderMoney = fund_money
                        else:
                            orderMoney = fund * leverage
                    elif riskControlSwitch == True:
                        if leverage == 0:
                            orderMoney = fund_money * rc_percent
                        else:
                            orderMoney = fund * leverage * rc_percent

                    orderSize = orderMoney / open_arr[i+1]

                    if exit_condition == 1 and exParam0 == 0:
                        exitSwitch = True
                        exT = i+1
                        endPointHigh_C = close_arr[i]
                        endPointHigh_H = close_arr[i]
                        endPointLow_C = close_arr[i]
                        endPointLow_L = close_arr[i]
                        ts2 += 1

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)

    return buy, sell, sellshort, buytocover, profit_list, profit_fee_list, profit_list_realized, profit_fee_list_realized, profit_fee_list_realized_time


@jit(nopython=True)
def backtestingPair(input_arr, fund=100, leverage=0, takerFee=0.0004, 
                    slippage=0.0001, stopLoss_slippageAdd=0.001,
                    exit_timeOut=False, exParam1=20, from_exit_condition=False,
                    exit_profitOut=False, exParam2=0.02,
                    exit_lossOut=False, lossOut_condition=1, exParam3=0.05, risk_control=False, rc_percent=0.5,
                    exit_condition=1, exParam0=0
                    ):

    '''
    - vol_arr, you should input ATR or standard deviation (not volume!!)
    - leverage = 0, order with equal amount $fund
    - when exit_condition=1 & exParam0=0, there's no exit condition
    '''

    spreadOpen_arr = input_arr[0]
    spread_arr = input_arr[1]
    openA_arr = input_arr[2]
    openB_arr = input_arr[3]
    closeA_arr = input_arr[4]
    closeB_arr = input_arr[5]
    entryLong_arr = input_arr[6]
    entrySellShort_arr = input_arr[7]
    exitShort_arr = input_arr[8]
    exitBuyToCover_arr = input_arr[9]
    vol_arr = input_arr[10]

    LS = ''
    buy = []
    sell = []
    sellshort = []
    buytocover = []
    profit_list = [0]
    profit_fee_list = [0]
    profit_list_realized = [0]
    profit_fee_list_realized = [0]
    profit_fee_list_realized_time = [0]

    fund_money = fund
    feeRate = takerFee + slippage
    stopLoss_feeRate = takerFee + slippage + stopLoss_slippageAdd
    
    endPointHigh = spread_arr[0]
    endPointHigh_A = closeA_arr[0]
    endPointHigh_B = closeB_arr[0]
    endPointLow = spread_arr[0]
    endPointLow_A = closeA_arr[0]
    endPointLow_B = closeB_arr[0]
    exitSwitch = False
    stopLoss = False
    stopProfit = False
    stopTime = False
    riskControlSwitch = False
    ts = 1
    ts2 = 1
    t = 0
    exT = 0

    if exit_lossOut == True and (lossOut_condition == 1 or lossOut_condition == 2):
        lossOut_specialCase = True
    else:
        lossOut_specialCase = False

    for i in range(len(openA_arr)):

        if i == len(openA_arr)-1:
            break

        if exit_lossOut == True and lossOut_condition == 4:
            if i < exParam3:
                profit_list.append(0)
                profit_fee_list.append(0)
                continue

        # stop time condition
        if exit_timeOut == True:
            if from_exit_condition == False:
                if ts >= exParam1:
                    stopTime = True
                else:
                    stopTime = False
            else:
                if exitSwitch == True:
                    if ts2 > exParam1:
                        stopTime = True
                else:
                    stopTime = False

        # stop profit condition
        if exit_profitOut == True:
            if exitSwitch == True:
                if LS == 'L':
                    stopProfit = (((closeA_arr[i] / openA_arr[exT] - 1) + (1 - closeB_arr[i] / openB_arr[exT])) / 2) >= exParam2
                    if stopProfit:
                        exitPriceA = closeA_arr[i]
                        exitPriceB = openB_arr[exT] * (closeA_arr[i] / openA_arr[exT] - 2*exParam2)
                elif LS == 'S':
                    stopProfit = (((1 - closeA_arr[i] / openA_arr[exT]) + (closeB_arr[i] / openB_arr[exT] - 1)) / 2) >= exParam2
                    if stopProfit:
                        exitPriceA = closeA_arr[i]
                        exitPriceB = openB_arr[exT] * (2*exParam2 + closeA_arr[i] / openA_arr[exT])
                else:
                    stopProfit = False

        # stop loss condition
        if exit_lossOut == True:
            if exitSwitch == True:

                if lossOut_condition == 1:
                    if LS == 'L':
                        stopLoss = (((closeA_arr[i] / openA_arr[exT] - 1) + (1 - closeB_arr[i] / openB_arr[exT])) / 2) <= -exParam3
                        if stopLoss:
                            exitPriceA = closeA_arr[i]
                            exitPriceB = openB_arr[exT] * (closeA_arr[i] / openA_arr[exT] + 2*exParam3)
                    elif LS == 'S':
                        stopLoss = (((1 - closeA_arr[i] / openA_arr[exT]) + (closeB_arr[i] / openB_arr[exT] - 1)) / 2) <= -exParam3
                        if stopLoss:
                            exitPriceA = closeA_arr[i]
                            exitPriceB = openB_arr[exT] * (closeA_arr[i] / openA_arr[exT] - 2*exParam3)
                    else:
                        stopLoss = False

                elif lossOut_condition == 2:
                    if LS == 'L':
                        stopLoss = (((closeA_arr[i] / endPointHigh_A - 1) + (1 - closeB_arr[i] / endPointHigh_B)) / 2) <= -exParam3   
                        if stopLoss:
                            exitPriceA = closeA_arr[i]
                            exitPriceB = endPointHigh_B * (closeA_arr[i] / endPointHigh_A + 2*exParam3)
                    elif LS == 'S':
                        stopLoss = (((1 - closeA_arr[i] / endPointLow_A) + (closeB_arr[i] / endPointLow_B - 1)) / 2) <= -exParam3
                        if stopLoss:
                            exitPriceA = closeA_arr[i]
                            exitPriceB = endPointLow_B * (closeA_arr[i] / endPointLow_A - 2*exParam3)
                    else:
                        stopLoss = False

                elif lossOut_condition == 3:
                    if LS == 'L':
                        stopLoss = spread_arr[i] <= endPointHigh - exParam3*vol_arr[exT-1]
                    elif LS == 'S':
                        stopLoss = spread_arr[i] >= endPointLow + exParam3*vol_arr[exT-1]
                    else:
                        stopLoss = False

                elif lossOut_condition == 4:
                    if LS == 'L':
                        stopLoss = spread_arr[i] <= min(spread_arr[i-exParam3:i])
                    elif LS == 'S':
                        stopLoss = spread_arr[i] >= max(spread_arr[i-exParam3:i])
                    else:
                        stopLoss = False

                ## when touch stopLoss, control risk after next trade
                if LS != '' and risk_control == True and stopLoss == True:
                    riskControlSwitch = True

        # start exit condition
        if LS != '' and exitSwitch == False:

            if exit_condition == 1:
                if ts >= exParam0:
                    exitSwitch = True

            elif exit_condition == 2:
                if LS == 'L':
                    if (((closeA_arr[i] / openA_arr[t] - 1) + (1 - closeB_arr[i] / openB_arr[t])) / 2) >= exParam0:
                        exitSwitch = True
                elif LS == 'S':
                    if (((1 - closeA_arr[i] / openA_arr[t]) + (closeB_arr[i] / openB_arr[t] - 1)) / 2) >= exParam0:
                        exitSwitch = True
        
            elif exit_condition == 3:
                if LS == 'L':
                    if spread_arr[i] >= spreadOpen_arr[t] + exParam0*vol_arr[t-1]:
                        exitSwitch = True
                elif LS == 'S':
                    if spread_arr[i] <= spreadOpen_arr[t] - exParam0*vol_arr[t-1]:
                        exitSwitch = True
            
            elif exit_condition == 4:
                if LS == 'L':                    
                    if (((closeA_arr[i] / openA_arr[t] - 1) + (1 - closeB_arr[i] / openB_arr[t])) / 2) <= -exParam0:
                        exitSwitch = True
                elif LS == 'S':
                    if (((1 - closeA_arr[i] / openA_arr[t]) + (closeB_arr[i] / openB_arr[t] - 1)) / 2) <= -exParam0:
                        exitSwitch = True

            elif exit_condition == 5:
                if LS == 'L':
                    if spread_arr[i] <= spreadOpen_arr[t] - exParam0*vol_arr[t-1]:
                        exitSwitch = True
                elif LS == 'S':
                    if spread_arr[i] >= spreadOpen_arr[t] + exParam0*vol_arr[t-1]:
                        exitSwitch = True

            elif exit_condition == 6:
                if vol_arr[i] >= exParam0*vol_arr[t-1]:
                    exitSwitch = True

            if exitSwitch == True:
                exT = i+1
                endPointHigh = spread_arr[i]
                endPointHigh_A = closeA_arr[i]
                endPointHigh_B = closeB_arr[i]
                endPointLow = spread_arr[i]
                endPointLow_A = closeA_arr[i]
                endPointLow_B = closeB_arr[i]

        # no position
        if LS == '':
            profit_list.append(0)
            profit_fee_list.append(0)
            
            if entryLong_arr[i] == True:
                LS = 'L'
                t = i+1
                buy.append(t)

            elif entrySellShort_arr[i] == True:
                LS = 'S'
                t = i+1
                sellshort.append(t)

            if entryLong_arr[i] == True or entrySellShort_arr[i] == True:
                profit_list_realized.append(0)
                profit_fee_list_realized.append(0)
                profit_fee_list_realized_time.append(t)

                if riskControlSwitch == False:
                    if leverage == 0:
                        orderMoney = fund_money
                    else:
                        orderMoney = fund * leverage
                elif riskControlSwitch == True:
                    if leverage == 0:
                        orderMoney = fund_money * rc_percent
                    else:
                        orderMoney = fund * leverage * rc_percent

                orderSizeA = (orderMoney / 2) / openA_arr[i+1]
                orderSizeB = (orderMoney / 2) / openB_arr[i+1]

                ts = 1
                ts2 = 1
                exitSwitch = False

                if exit_condition == 1 and exParam0 == 0:
                    exitSwitch = True
                    exT = i+1
                    endPointHigh = spread_arr[i]
                    endPointHigh_A = closeA_arr[i]
                    endPointHigh_B = closeB_arr[i]
                    endPointLow = spread_arr[i]
                    endPointLow_A = closeA_arr[i]
                    endPointLow_B = closeB_arr[i]
                    ts2 += 1

        # long position
        elif LS == 'L':
            if (stopProfit==False and stopLoss==False) or (stopLoss==True and lossOut_specialCase==False):
                profit = orderSizeA * (openA_arr[i+1] - openA_arr[i]) + orderSizeB * (openB_arr[i] - openB_arr[i+1])
            else:
                profit = orderSizeA * (exitPriceA - openA_arr[i]) + orderSizeB * (openB_arr[i] - exitPriceB)
            profit_list.append(profit)
            ts += 1

            if exitSwitch == True:
                ts2 += 1
                if spread_arr[i] > endPointHigh:
                    endPointHigh = spread_arr[i]
                    endPointHigh_A = closeA_arr[i]
                    endPointHigh_B = closeB_arr[i]
                if spread_arr[i] < endPointLow:
                    endPointLow = spread_arr[i]
                    endPointLow_A = closeA_arr[i]
                    endPointLow_B = closeB_arr[i]

            if exitShort_arr[i] == True or i == len(openA_arr)-2 or stopLoss or stopProfit or stopTime: 
                if (stopProfit==False and stopLoss==False) or (stopLoss==True and lossOut_specialCase==False):
                    pl_round = orderSizeA * (openA_arr[i+1] - openA_arr[t]) + orderSizeB * (openB_arr[t] - openB_arr[i+1])
                    profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                else:
                    pl_round = orderSizeA * (exitPriceA - openA_arr[t]) + orderSizeB * (openB_arr[t] - exitPriceB)
                    if stopLoss and lossOut_specialCase:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                    else:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                
                profit_fee_list.append(profit_fee)
                sell.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
                if stopLoss and lossOut_specialCase:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                else:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                fund += profit_fee_realized

                profit_list_realized.append(profit_realized)
                profit_fee_list_realized.append(profit_fee_realized)
                profit_fee_list_realized_time.append(i+1)

                # close riskControlSwitch
                if riskControlSwitch == True and profit_fee_realized > 0:
                    riskControlSwitch = False

                # reset stop condition
                exitSwitch = False
                stopLoss = False
                stopProfit = False
                stopTime = False
                ts = 1
                ts2 = 1

                if entrySellShort_arr[i] == False:
                    LS = ''
                
                ## turn over
                elif entrySellShort_arr[i] == True:
                    LS = 'S'
                    t = i+1
                    sellshort.append(t)

                    if riskControlSwitch == False:
                        if leverage == 0:
                            orderMoney = fund_money
                        else:
                            orderMoney = fund * leverage
                    elif riskControlSwitch == True:
                        if leverage == 0:
                            orderMoney = fund_money * rc_percent
                        else:
                            orderMoney = fund * leverage * rc_percent

                    orderSizeA = (orderMoney / 2) / openA_arr[i+1]
                    orderSizeB = (orderMoney / 2) / openB_arr[i+1]

                    if exit_condition == 1 and exParam0 == 0:
                        exitSwitch = True
                        exT = i+1
                        endPointHigh = spread_arr[i]
                        endPointHigh_A = closeA_arr[i]
                        endPointHigh_B = closeB_arr[i]
                        endPointLow = spread_arr[i]
                        endPointLow_A = closeA_arr[i]
                        endPointLow_B = closeB_arr[i]
                        ts2 += 1

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)

        # short position
        elif LS == 'S':
            if (stopProfit==False and stopLoss==False) or (stopLoss==True and lossOut_specialCase==False):
                profit = orderSizeA * (openA_arr[i] - openA_arr[i+1]) + orderSizeB * (openB_arr[i+1] - openB_arr[i])
            else:
                profit = orderSizeA * (openA_arr[i] - exitPriceA) + orderSizeB * (exitPriceB - openB_arr[i])
            profit_list.append(profit)
            ts += 1

            if exitSwitch == True:
                ts2 += 1
                if spread_arr[i] > endPointHigh:
                    endPointHigh = spread_arr[i]
                    endPointHigh_A = closeA_arr[i]
                    endPointHigh_B = closeB_arr[i]
                if spread_arr[i] < endPointLow:
                    endPointLow = spread_arr[i]
                    endPointLow_A = closeA_arr[i]
                    endPointLow_B = closeB_arr[i]

            if exitBuyToCover_arr[i] == True or i == len(openA_arr)-2 or stopLoss or stopProfit or stopTime: 
                if (stopProfit==False and stopLoss==False) or (stopLoss==True and lossOut_specialCase==False):
                    pl_round = orderSizeA * (openA_arr[t] - openA_arr[i+1]) + orderSizeB * (openB_arr[i+1] - openB_arr[t])
                    profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                else:
                    pl_round = orderSizeA * (openA_arr[t] - exitPriceA) + orderSizeB * (exitPriceB - openB_arr[t])
                    if stopLoss and lossOut_specialCase:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                    else:
                        profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                
                profit_fee_list.append(profit_fee)
                buytocover.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
                if stopLoss and lossOut_specialCase:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*stopLoss_feeRate
                else:
                    profit_fee_realized = pl_round - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                fund += profit_fee_realized

                profit_list_realized.append(profit_realized)
                profit_fee_list_realized.append(profit_fee_realized)
                profit_fee_list_realized_time.append(i+1)

                # close riskControlSwitch
                if riskControlSwitch == True and profit_fee_realized > 0:
                    riskControlSwitch = False

                # reset stop condition
                exitSwitch = False
                stopLoss = False
                stopProfit = False
                stopTime = False
                ts = 1
                ts2 = 1

                if entryLong_arr[i] == False:
                    LS = ''

                ## turn over
                elif entryLong_arr[i] == True:
                    LS = 'L'
                    t = i+1
                    buy.append(t)

                    if riskControlSwitch == False:
                        if leverage == 0:
                            orderMoney = fund_money
                        else:
                            orderMoney = fund * leverage
                    elif riskControlSwitch == True:
                        if leverage == 0:
                            orderMoney = fund_money * rc_percent
                        else:
                            orderMoney = fund * leverage * rc_percent

                    orderSizeA = (orderMoney / 2) / openA_arr[i+1]
                    orderSizeB = (orderMoney / 2) / openB_arr[i+1]

                    if exit_condition == 1 and exParam0 == 0:
                        exitSwitch = True
                        exT = i+1
                        endPointHigh = spread_arr[i]
                        endPointHigh_A = closeA_arr[i]
                        endPointHigh_B = closeB_arr[i]
                        endPointLow = spread_arr[i]
                        endPointLow_A = closeA_arr[i]
                        endPointLow_B = closeB_arr[i]
                        ts2 += 1

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)

    return buy, sell, sellshort, buytocover, profit_list, profit_fee_list, profit_list_realized, profit_fee_list_realized, profit_fee_list_realized_time


def dictType_output(output_tuple):
    
    output_dict = {'buy': output_tuple[0], 'sell': output_tuple[1], 'sellshort': output_tuple[2], 'buytocover': output_tuple[3],
                   'profit_list': output_tuple[4], 'profit_fee_list': output_tuple[5], 'profit_list_realized': output_tuple[6],
                   'profit_fee_list_realized': output_tuple[7], 'profit_fee_list_realized_time': output_tuple[8]}
    
    return output_dict

