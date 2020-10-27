import fxcmpy
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyti.exponential_moving_average import exponential_moving_average as ema
from algorithm import *

class BacktestingFXCM:
    def __init__(self, instrument, frequency, start, end, con):
        # smallest change value
        self.pip = .0879
        # basic number of lot order
        self.lot_size = 10
        self.instrument = instrument
        self.frequency = frequency
        # exemple of str to send '2018-06-29 08:15:27'
        date_time_start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        date_time_end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        self.data = con.get_candles(instrument, period=frequency, start=date_time_start, end=date_time_end)
        utils_columns = ['askclose', 'bidclose','askhigh', 'asklow', 'askopen']
        self.data = self.data[utils_columns]
        self.EMAv = initEMAv(self.data)
        #self.ichimoku = initIchimoku(self.data)
        self.result = pd.DataFrame(columns=['position', 'position_test'])



    def calculPositionEMAv(self):
        #self.result['position'] = np.where(self.EMAv['p_5'] > self.EMAv['p_20'], 1, 0)
        self.result['position'] = np.where(
            (self.EMAv['p_5'] > self.EMAv['p_20'])
            &
            (self.EMAv['p_20'] > self.EMAv['p_50']) & (self.data['askclose'] > self.EMAv['p_50'])
            ,1,0)
        self.result['signal'] = self.result['position'].diff()
        self.result['signal_test'] = self.result['position_test'].diff()
        self.result['difference_pips'] = (self.data['askclose'].values - self.data['askopen'].values) * 100


    def calculPositionIchimoku(self):
        self.result['position'] = np.where((self.data['askclose'] > self.ichimoku['senkouA']) & (self.data['askclose'] > self.ichimoku['senkouB'])
                                           & (self.ichimoku['chikou'] >self.data['askclose'] &
                                              (self.ichimoku['tenkan'] > self.ichimoku['kinju'])), 1,0)
        self.result['signal'] = self.result['position'].diff()
        self.result['difference_pips'] = (self.data['askclose'].values - self.data['askopen'].values) * 100


    def calculProfit(self):
        returns = 0
        CountPL=False
        print("calcul profit")
        for i, row in self.result.iterrows():
            if CountPL==True:
                returns += (row['difference_pips'] * self.pip * self.lot_size)
                self.result.loc[i,'total'] = returns
            else:
                self.result.loc[i,'total'] = returns
            if row['position'] == 1:
                CountPL=True
            else:
                CountPL=False


    def plotting(self):
        fig = plt.figure(figsize=(42,32))
        ax1 = fig.add_subplot(111,  ylabel='GBP/JPY Price')
        dataplot = self.data.merge(self.result, left_on=self.result.index, right_index=True).reset_index()
        dataplot = dataplot.merge(self.EMAv, on='date')
        #print(dataplot.head(100))
        dataplot['askclose'].plot(ax=ax1, color='r', lw=2, label='askclose')
        dataplot[['p_5','p_20', 'p_50']].plot(ax=ax1, lw=1)

        ax1.plot(dataplot.loc[dataplot.position == 1.0].index,
                 dataplot.p_5[dataplot.position == 1.0],
                 'D', markersize=10, color='k' )
        ax1.plot(dataplot.loc[dataplot.position == -1.0].index,
                 dataplot.p_20[dataplot.position == -1.0],
                 'X', markersize=10, color='m')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Profit $')
        ax2.plot(dataplot['total'], color='m', lw=3)
