import fxcmpy
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyti.exponential_moving_average import exponential_moving_average as ema
from algorithm import *


class tradeFXCM:
    def __init__(self, instrument, frequency, con):
        # smallest change value
        self.pip = .0879
        # basic number of lot order
        self.lot_size = 10
        self.instrument = instrument
        self.frequency = frequency
        self.data = con.get_candles(instrument, period=frequency, number=1000)
        utils_columns = ['askclose', 'bidclose','askhigh', 'asklow', 'askopen']
        self.data = self.data[utils_columns]
        self.EMAv = initEMAv(self.data)
        self.isTrade = False
        #self.ichimoku = initIchimoku(self.data)

        # a faire en dernier
        self.time_update = datetime.datetime.now()
        print(self.time_update)



    # Exponentielle moving average instead of moving average
    # better reaction to last price
    def ExpMovingAvCalc(self):
        self.EMAv.append(
            {
                'p_5' :
                    calculPeriodEMAv(len(self.data), self.data['askclose'].iloc[-1], self.EMAv['p_5'].tolist(), self.data['askclose'], 12)
            },
            {
                'p_20' :
                    calculPeriodEMAv(len(self.data), self.data['askclose'].iloc[-1], self.EMAv['p_20'].tolist(), self.data['askclose'], 20)
            },
            {
                'p_50' :
                    calculPeriodEMAv(len(self.data), self.data['askclose'].iloc[-1], self.EMAv['p_50'].tolist(), self.data['askclose'], 50)
            }
        )

    def IchimokuCalc(self):
        self.ichimoku.append(
            {
                'tenkan': calculsen(len(self.data), self.data, 9)
            },
            {
                'kijun': calculsen(len(self.data), self.data, 26)
            },
            {
                'chikou': calculspan(len(self.data), self.data, 26, 'Chikou', None, None)
            },
            {
                'senkouA': calculspan(len(self.data), self.data, 26, 'SenkouA', self.ichimoku['tenkan'], self.ichimoku['kijun'])
            },
            {
                'senkouB': calculspan(len(self.data), self.data, 52, 'SenkouB', None, None)
            }
        )


    def update(self, con):
        temp = con.get_candles(self.instrument, period=self.frequency, number=1)
        temp = temp[['askclose', 'bidclose','askhigh', 'asklow', 'askopen']]
        self.data = self.data.append(temp)
        #self.time_update = self.data.last_valid_index()
        self.time_update = datetime.datetime.now()
        print('ma valeur index qui marche pas')
        print(self.data.last_valid_index())
        print(temp)
        # add EMAv new
        self.ExpMovingAvCalc()
        #self.IchimokuCalc()

        # decision emav
        self.isTrade = decisionEMAv(self.data, self.EMAv, self.isTrade, con, self.instrument)


