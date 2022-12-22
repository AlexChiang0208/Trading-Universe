import numpy as np
import numba
from numba import jit


@jit(nopython=True)
def backtesting(input_arr, fund=100, leverage=0, takerFee=0.0004, slippage=0.0008,
                exit_timeOut=False, exParam1=20, from_exit_condition=False,
                exit_profitOut=False, exParam2=0.02, end_trigger2='C',
                exit_lossOut=False, lossOut_condition=1, exParam3=0.05, start_trigger3='C', 
                end_trigger3='C', risk_control=False, rc_percent=0.5,
                exit_condition=1, exParam0=0, end_trigger0='C'
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

    feeRate = takerFee + slippage
    fund_money = fund

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
                if end_trigger2 == 'C':
                    if LS == 'L':
                        stopProfit = close_arr[i] >= open_arr[exT] * (1+exParam2)
                    elif LS == 'S':
                        stopProfit = close_arr[i] <= open_arr[exT] * (1-exParam2)
                    else:
                        stopProfit = False

                elif end_trigger2 == 'HL':
                    if LS == 'L':
                        stopProfit = high_arr[i] >= open_arr[exT] * (1+exParam2)
                    elif LS == 'S':
                        stopProfit = low_arr[i] <= open_arr[exT] * (1-exParam2)
                    else:
                        stopProfit = False

        # stop loss condition
        if exit_lossOut == True:
            if exitSwitch == True:

                if lossOut_condition == 1:
                    if end_trigger3 == 'C':
                        if LS == 'L':
                            stopLoss = close_arr[i] <= open_arr[exT] * (1-exParam3)
                        elif LS == 'S':
                            stopLoss = close_arr[i] >= open_arr[exT] * (1+exParam3)
                        else:
                            stopLoss = False

                    elif end_trigger3 == 'HL':
                        if LS == 'L':
                            stopLoss = low_arr[i] <= open_arr[exT] * (1-exParam3)
                        elif LS == 'S':
                            stopLoss = high_arr[i] >= open_arr[exT] * (1+exParam3)
                        else:
                            stopLoss = False

                elif lossOut_condition == 2:
                    if end_trigger3 == 'C':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] <= endPointHigh_C * (1-exParam3)
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] <= endPointHigh_H * (1-exParam3)
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] >= endPointLow_C * (1+exParam3)
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] >= endPointLow_L * (1+exParam3)
                        else:
                            stopLoss = False

                    elif end_trigger3 == 'HL':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = low_arr[i] <= endPointHigh_C * (1-exParam3)
                            elif start_trigger3 == 'HL':
                                stopLoss = low_arr[i] <= endPointHigh_H * (1-exParam3)
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = high_arr[i] >= endPointLow_C * (1+exParam3)
                            elif start_trigger3 == 'HL':
                                stopLoss = high_arr[i] >= endPointLow_L * (1+exParam3)
                        else:
                            stopLoss = False

                elif lossOut_condition == 3:
                    if end_trigger3 == 'C':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] <= endPointHigh_C - exParam3*vol_arr[exT-1]
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] <= endPointHigh_H - exParam3*vol_arr[exT-1]
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] >= endPointLow_C + exParam3*vol_arr[exT-1]
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] >= endPointLow_L + exParam3*vol_arr[exT-1]
                        else:
                            stopLoss = False

                    elif end_trigger3 == 'HL':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = low_arr[i] <= endPointHigh_C - exParam3*vol_arr[exT-1]
                            elif start_trigger3 == 'HL':
                                stopLoss = low_arr[i] <= endPointHigh_H - exParam3*vol_arr[exT-1]
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = high_arr[i] >= endPointLow_C + exParam3*vol_arr[exT-1]
                            elif start_trigger3 == 'HL':
                                stopLoss = high_arr[i] >= endPointLow_L + exParam3*vol_arr[exT-1]
                        else:
                            stopLoss = False

                elif lossOut_condition == 4:
                    if end_trigger3 == 'C':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] <= min(close_arr[i-exParam3:i])
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] <= min(low_arr[i-exParam3:i])
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = close_arr[i] >= max(close_arr[i-exParam3:i])
                            elif start_trigger3 == 'HL':
                                stopLoss = close_arr[i] >= max(high_arr[i-exParam3:i])
                        else:
                            stopLoss = False

                    elif end_trigger3 == 'HL':
                        if LS == 'L':
                            if start_trigger3 == 'C':
                                stopLoss = low_arr[i] <= min(close_arr[i-exParam3:i])
                            elif start_trigger3 == 'HL':
                                stopLoss = low_arr[i] <= min(low_arr[i-exParam3:i])
                        elif LS == 'S':
                            if start_trigger3 == 'C':
                                stopLoss = high_arr[i] >= max(close_arr[i-exParam3:i])
                            elif start_trigger3 == 'HL':
                                stopLoss = high_arr[i] >= max(high_arr[i-exParam3:i])
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
                if end_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                elif end_trigger0 == 'HL':
                    if LS == 'L':
                        if high_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if low_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
        
            elif exit_condition == 3:
                if end_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
                elif end_trigger0 == 'HL':
                    if LS == 'L':
                        if high_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if low_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
            
            elif exit_condition == 4:
                if end_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True
                elif end_trigger0 == 'HL':
                    if LS == 'L':
                        if low_arr[i] <= open_arr[t] * (1-exParam0):
                            exitSwitch = True
                    elif LS == 'S':
                        if high_arr[i] >= open_arr[t] * (1+exParam0):
                            exitSwitch = True

            elif exit_condition == 5:
                if end_trigger0 == 'C':
                    if LS == 'L':
                        if close_arr[i] <= open_arr[t] - exParam0*vol_arr[t-1]:
                            exitSwitch = True
                    elif LS == 'S':
                        if close_arr[i] >= open_arr[t] + exParam0*vol_arr[t-1]:
                            exitSwitch = True
                elif end_trigger0 == 'HL':
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
                pl_round = orderSize * (open_arr[i+1] - open_arr[t])
                profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                profit_fee_list.append(profit_fee)
                sell.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
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
                pl_round = orderSize * (open_arr[t] - open_arr[i+1])
                profit_fee = profit - orderMoney*feeRate - (orderMoney+pl_round)*feeRate
                profit_fee_list.append(profit_fee)
                buytocover.append(i+1)
                
                # Realized PnL
                profit_realized = pl_round
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


def dictType_output(output_tuple):
    
    output_dict = {'buy': output_tuple[0], 'sell': output_tuple[1], 'sellshort': output_tuple[2], 'buytocover': output_tuple[3],
                   'profit_list': output_tuple[4], 'profit_fee_list': output_tuple[5], 'profit_list_realized': output_tuple[6],
                   'profit_fee_list_realized': output_tuple[7], 'profit_fee_list_realized_time': output_tuple[8]}
    
    return output_dict

