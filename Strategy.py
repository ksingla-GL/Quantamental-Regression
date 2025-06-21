# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 11:57:24 2017

@author: ksingla6
"""
import numpy as np                   
     
class Strategy(object):
    
    """
    The main purpose of this class is to generate signals and add/modify predictors.
    """
    
    def __init__(self,all_data,date):
        
        self.subdata=all_data.loc[all_data['Date']==date]
        self.date=date
        self.data=all_data
    
    def subset_vol(self,vol_target):
        
        """
        Subsetting stocks which do not meet the 15-day ADV limit.
        """
        
        for sec in self.subdata['Ticker'].unique():
            if (self.subdata.loc[self.subdata['Ticker']==sec,'Volume']<vol_target).any():
               self.subdata=self.subdata.loc[self.subdata['Ticker']!=sec]           
    
    def signal_generator(self,k=100):
        """
        This is the meat of the strategy and everything
        """
        
        self.subdata=self.subdata.sort_values('M_score',ascending=False)
        self.subdata['Signal']=""
        self.subdata['Signal'].iloc[:k]="Buy"
        self.subdata['Signal'].iloc[len(self.subdata)-k:]="Sell"
        
        return self.subdata.loc[self.subdata['Signal']!=""]
    
    def modify_predictors(self,n,m,l):   
        """
        Will be used when running in-sample optimization to find the perfect parameters.
        """
        
        self.data['Mom']=np.where(self.data['Ticker']==self.data['Ticker'].shift(n),np.log(self.data\
        ['Adj Close'].shift(1)/self.data['Adj Close'].shift(n)),np.nan)
        self.data['Rev']=np.where(self.data['Ticker']==self.data['Ticker'].shift(m),np.log(self.data\
        ['Adj Close'].shift(m)/self.data['Adj Close'].shift(1)),np.nan)
        
        self.data['Ret']=np.log(self.data['Adj Close']/self.data['Adj Close'].shift(1))
        self.data['Std']=np.where(self.data['Ticker']==self.data['Ticker'].shift(l),self.data['Ret'].\
        rolling(l).std(),np.nan)
        
        self.data=self.data.dropna()
        return self.data