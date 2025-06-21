# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 11:57:55 2017

@author: ksingla6
"""

from datetime import datetime as dt
from pandas.tseries.offsets import BDay
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np

class Portfolio(object):
    
    """
    Creates a portfolio object which changes ever =y rebalancing step according to the date,
    the signals given to it, old holdings and its current pf_val(portfolio value)
    """
    
    def __init__(self,old_holdings,signals,all_data,date,pf_val):
        
        self.old_holdings=old_holdings
        self.signals=signals
        self.data=all_data
        self.startdate=(dt.strptime(date,"%Y-%m-%d")-BDay(1000)).strftime("%Y-%m-%d")
        self.date=date
        self.subset=all_data.loc[(self.data['Date']>self.startdate)&(self.data['Date']<=self.date)]
        self.pf_val=pf_val
        
    def compute_PnL(self,K,lev):
        
        """
        Given the number of stocks in our pf K, this function calculates the gain/
        loss of the portfolio in the current rebalancing step.
        """
        
        pf_stocks=self.old_holdings['Ticker'].unique()
        cur_holdings=self.data.loc[(self.data['Date']==self.date)&(self.data['Ticker']\
        .isin(pf_stocks))]
        while len(cur_holdings)==0:
            self.date=(dt.strptime(self.date,"%Y-%m-%d")+BDay(1)).strftime("%Y-%m-%d")
            cur_holdings=self.data.loc[self.data['Date']==self.date]
        total_ret=0
        buy_ret=0
        sell_ret=0
        
        #Assume zero return for stocks data not present on current day
        self.old_holdings['Ret']=0.0
        self.old_holdings['Entry_Price']=0.0
        self.old_holdings['Exit_Price']=0.0
        for stock in pf_stocks:
            if stock in cur_holdings['Ticker'].values:
                status=self.old_holdings.loc[self.old_holdings['Ticker']==stock,\
                'Signal'].values[0]
                if status=='Buy':
                    ret=cur_holdings.loc[cur_holdings['Ticker']==stock,'Adj Close']\
                    .values[0]/self.old_holdings.loc[self.old_holdings['Ticker']==\
                    stock,'Adj Close'].values[0]-1
                    buy_ret+=ret
                    if stock not in self.signals['Ticker'].values and stock in cur_holdings\
                    ['Ticker'].values:
                        buy_ret-=0.0015*lev
                   
                elif status=='Sell':
                    ret=self.old_holdings.loc[self.old_holdings['Ticker']==stock,\
                    'Adj Close'].values[0]/cur_holdings.loc[cur_holdings['Ticker']==\
                    stock,'Adj Close'].values[0]-1
                    sell_ret+=ret   
                    if stock not in self.signals['Ticker'].values and stock in cur_holdings\
                    ['Ticker'].values:
                        sell_ret-=0.0015*lev                       
                    
                if abs(ret)>1:
                    ret=0
                self.old_holdings.loc[self.old_holdings['Ticker']==stock,\
                'Ret']=ret
                self.old_holdings.loc[self.old_holdings['Ticker']==stock,\
                'Entry_Price']=self.old_holdings.loc[self.old_holdings['Ticker']==\
                stock,'Adj Close'].values[0]
                self.old_holdings.loc[self.old_holdings['Ticker']==stock,\
                'Exit_Price']=cur_holdings.loc[cur_holdings['Ticker']==\
                stock,'Adj Close'].values[0]    
                  
                total_ret+=ret*lev
            if stock not in self.signals['Ticker'].values and stock in cur_holdings\
            ['Ticker'].values:
                total_ret-=0.0015*lev
        self.pf_val+=total_ret*self.pf_val/(K)
        #print(str(buy_ret)+","+str(sell_ret)+","+str(np.mean(self.subset['M_score'])))
        return self.pf_val,total_ret,self.date
    
    def generate_trades_sheet(self,ts,pf_val,K):
        
        """
        Makes a detailed trades sheet, documenting each trade, so that the portfolio
        value can easily be monitored using the trades sheet.
        """
        
        self.signals['Shares']=(pf_val/(K))/self.signals['Adj Close']
        newsignals=self.signals.copy()
        
        
        self.old_holdings['Shares']=(pf_val/K)/self.old_holdings['Adj Close']
        self.old_holdings['Exit_date']=self.date

        ts=ts.append(self.old_holdings[['Date','Exit_date','Ticker','Entry_Price','Exit_Price',\
        'Signal','Shares','Ret']])

        
        return ts
    
    def perf_eval(self,pf_vals,rebal_period,ID,rf=0.03):
        """
        Given the pf_vals df which should have a monthwise portfolio value ennumerated.
        'ID' justs stands to identify what were the parameters used in the given pf df
        so that we know which portfolio created what statistics.
        """
        
        pf_vals['ret_vals']=pf_vals['Pf_Value']/pf_vals['Pf_Value'].shift(1)-1
        annual_std=np.std(pf_vals['ret_vals'])*np.sqrt(252.0/rebal_period)
        annual_ret=np.mean(pf_vals['ret_vals'])*252.0/rebal_period
        sharpe_ratio=(annual_ret-rf)/annual_std
        
        #The next chunk calcultes drawdown by iteratively updating max pf value and dd values
        maxpt=pf_vals['Pf_Value'].iloc[0]
        maxdd=0.0
        
        for date in pf_vals['Date']:
            
            if pf_vals['Pf_Value'].loc[pf_vals['Date']==date].values[0]>maxpt:
                maxpt=pf_vals['Pf_Value'].loc[pf_vals['Date']==date].values[0]
                
            if (maxpt-pf_vals['Pf_Value'].loc[pf_vals['Date']==date].values[0])/maxpt>maxdd:
                maxdd=(maxpt-pf_vals['Pf_Value'].loc[pf_vals['Date']==date].values[0])/maxpt
                
        return [[ID,sharpe_ratio,annual_ret,annual_std,maxdd]]
        