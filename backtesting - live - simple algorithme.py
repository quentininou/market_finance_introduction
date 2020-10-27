#!/usr/bin/env python
# coding: utf-8

# In[1]:


import fxcmpy
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyti.exponential_moving_average import exponential_moving_average as ema
get_ipython().run_line_magic('matplotlib', 'inline')
pd.options.display.max_rows = 4000


# In[2]:


con = fxcmpy.fxcmpy(config_file='fxcm.cfg')


# In[3]:



# In[12]:


all_frequency = ['m1','m5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1', 'W1']
all_instrument = ['EUR/USD']


# # BACKTESTING

# In[34]:


start = '2016-01-01 00:00:00'
end = '2018-06-10 00:00:00'
test = BacktestingFXCM('GBP/JPY', 'D1', start, end)
test.calculPositionEMAv()
test.calculProfit()
test.plotting()


# In[73]:


start = '2016-01-01 00:00:00'
end = '2018-06-10 00:00:00'
testUSD = BacktestingFXCM('EUR/USD', 'D1', start, end)
testUSD.calculPositionEMAv()
testUSD.calculPositionIchimoku()
#testUSD.plotting()
print(testUSD.result.columns)


# In[64]:


print(testUSD.result['total'].iloc[-1])


# In[51]:


# mon calcul sur la emav
print(testUSD.result['total'].iloc[-1])


# In[47]:


# ma condition
print(testUSD.result['total'].iloc[-1])


# In[44]:


# le leur tutorial exemple
print(testUSD.result['total'].iloc[-1])


# # TRADING

# In[ ]:


all_market = []
all_market.append(tradeFXCM('EUR/USD', 'm1'))


# In[ ]:


while 1:
    for market in all_market:
        c = datetime.datetime.now() - market.time_update
        #check one minute
        if c.seconds / 60 >= 0.3:
            market.update()
            #decisionEMAv(self.data, self.EMAv)


# In[ ]:


con.close()


# In[ ]:




