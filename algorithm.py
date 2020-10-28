import numpy as np
import pandas as pd


def calculPeriodEMAv(i, val, tabEMAv, data, periodValue):
    if i == periodValue:
        return np.array(data[0:i], dtype=np.float32).mean()
    if i > periodValue:
        return val * (2/(periodValue+1)) +  tabEMAv[-1] * (1- (2/(periodValue+1)))
    elif i < periodValue:
        return None


def initEMAv(data):
    i = 1
    p_5 = []
    p_20 = []
    p_50 = []
    periodEMAv = ['p_5', 'p_20', 'p_50']
    ## pour D1 & H1 : 12,20,50
    for val in data['askclose']:
        p_5.append(calculPeriodEMAv(i, val, p_5, data['askclose'], 12))
        p_20.append(calculPeriodEMAv(i, val, p_20, data['askclose'], 20))
        #p_20.append(ema(data['askclose'], 5))
        p_50.append(calculPeriodEMAv(i, val, p_50, data['askclose'], 50))
        i += 1
    emav = pd.DataFrame(columns=periodEMAv)
    emav['p_5']= (p_5)
    #emav['p_5']= ema(data['askclose'], 12)
    emav['p_20']= (p_20)
    #emav['p_20']= ema(data['askclose'], 20)
    emav['p_50']= (p_50)
    emav.index = data.index
    return (emav)



def calculsen(i, data, offset):
    # tenkan = (H+B)/2
    # H  max du prix sur offset bougies precedente
    # B  min du prix sur offset bougies precedente
    if i < offset:
        return None
    else:
        return ((max(data['askhigh'][i-offset:i]) + min(data['asklow'][i-offset:i])) / 2)



def calculspan(i ,data, offset, types, tenkan, kijun):
    if i < offset:
        return None
    if types == 'Chikou':
        return data['askclose'][i - offset]
    if types == 'SenkouA':
        if kijun[i - offset] != None:
            return (tenkan[i - offset] + kijun[i - offset]) / 2
        else:
            return None
    if types == 'SenkouB':
        return ((max(data['askhigh'][i-offset:i]) + min(data['asklow'][i-offset:i])) / 2)



def initIchimoku(data):
    i = 0
    tenkan_sen = []
    kijun_sen = []
    chikou_span = []
    senkou_spanA = []
    senkou_spanB = []
    kumo = []
    for z in range(26):
        senkou_spanB.append(None)
    for val in data['askclose']:
        tenkan_sen.append(calculsen(i, data, 9))
        kijun_sen.append(calculsen(i, data, 26))
        chikou_span.append(calculspan(i, data, 26, 'Chikou', tenkan_sen, kijun_sen))
        senkou_spanA.append(calculspan(i, data, 26, 'SenkouA', tenkan_sen, kijun_sen))
        senkou_spanB.append(calculspan(i, data, 52, 'SenkouB', tenkan_sen, kijun_sen))
        i += 1
    senkou_spanB = senkou_spanB[:len(senkou_spanB)-26]
    ichimoku = pd.DataFrame()
    ichimoku['tenkan'] = tenkan_sen
    ichimoku['kijun'] = kijun_sen
    ichimoku['chikou'] = chikou_span
    ichimoku['senkouA'] = senkou_spanA
    ichimoku['senkouB'] = senkou_spanB
    ichimoku = ichimoku.set_index(data.index)
    return ichimoku



def decisionIchimoku(data, ichimokuisTrade, isTrade, con, instrument):
    # nuage  = Kumo : nuage enter senkouA et SenkouB
    # haussier fort : prix au dessus du nuage, tenkan > kijun, roisement au dessus du nuage, chikou au dessus de prix

    if data['askclose'][-1] > ichimoku['senkouA'][-1] and data['askclose'][-1] > ichimoku['senkouB'][-1]:
        if ichimoku['chikou'][-1] > data['askclose'][-1]:
            if ichimoku['tekan'][-2] < ichimoku['kijun'][-2] and ichimoku['tekan'][-1] > ichimoku['kijun'][-1]:
                if isTrade == False:
                    con.create_market_buy_order(instrument, 10)
                    return True

            #if ichimoku['tenkan'][-1] > ichimoku['senkouA'][-1] and ichimoku['tenkan'][-1] > ichimoku['senkouB'][-1]:
                    # haussier fort au dessus du nuage
                #if ichimoku['tenkan'][-1] < ichimoku['senkouA'][-1] and ichimoku['tenkan'][-1] < ichimoku['senkouB'][-1]:
                    # haussier faible au dessous du nuage
                #else:
                    # haussier moyen dans le nuage

    if data['askclose'][-1] < ichimoku['senkouA'][-1] and data['askclose'][-1] < ichimoku['senkouB'][-1]:
        if ichimoku['chikou'][-1] < data['askclose'][-1]:
            if ichimoku['tekan'][-2] > ichimoku['kijun'][-2] and ichimoku['tekan'][-1] < ichimoku['kijun'][-1]:
                if isTrade == True:
                    con.create_market_sell_order(instrument, 10)
                    return False
                #if ichimoku['kijun'][-1] < ichimoku['senkouA'][-1] and ichimoku['kijun'][-1] < ichimoku['senkouB'][-1]:
                    # baissier fort au dessus du nuage
                #if ichimoku['kijun'][-1] > ichimoku['senkouA'][-1] and ichimoku['kijun'][-1] > ichimoku['senkouB'][-1]:
                    # baissier faible au dessous du nuage
                #else:
                    # baissier moyen dans le nuage



def decisionEMAv(data, EMAv, isTrade, con, instrument):
    # ENTRY LOGIC
    # buy if p5 go upper than p20
    if EMAv['p_5'][-1] > EMAv['p_20'][-1]:
        # P20 and p5 are upper p50
        # and last price upper p50
        if EMAv['p_20'][-1] > EMAv['p_50'][-1] and data['askclose'][-1] > EMAv['p_50'][-1]:
            ### je achete
            if isTrade == False:
                con.create_market_buy_order(instrument, 10)
                return True

    # EXIT LOGIC
    # sell if p5 go under than p20
    if EMAv['p_5'][-2] > EMAv['p_20'][-1] and EMAv['p_5'][-1] < EMAv['p_20'][-1]:
        # P20 and p5 are under p50 and last price under p50
        if EMAv['p_20'][-1] < EMAv['p_50'][-1] and data['askclose'][-1] < EMAv['p_50'][-1]:
            ### je vend
            if isTrade == True:
                con.create_market_sell_order(instrument, 10)
                return False

    return isTrade
