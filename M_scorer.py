# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 11:56:39 2017

@author: ksingla6
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime as dt
from pandas.tseries.offsets import BDay

def m_score_weights(df,date):
    
    """
    Runs a regression for a df which contains all stocks' prices' info.
    This regression gives us some optimum weights, which can be applied to find the M-score
    """
    
    regr_start_date=(dt.strptime(date,"%Y-%m-%d")-BDay(200)).strftime("%Y-%m-%d")
    regr_end_date=(dt.strptime(date,"%Y-%m-%d")-BDay(100)).strftime("%Y-%m-%d")
    dep=df.loc[(df['Date']<=regr_end_date)&(df['Date']>=regr_start_date),'Ret']                                       #Stands for dependent variable
    pred=df.loc[(df['Date']<=regr_end_date)&(df['Date']>=regr_start_date),['Mom','Rev','Std']]   
    #Stands for predictor variables
    
    regr=sm.OLS(dep,pred).fit()
    weights=regr.params
    
    #Calculating M_Score using the regression weights
    df.loc[(df['Date']<=date)&(df['Date']>regr_end_date),'M_score']=df.loc[(df['Date']<=date)&(df['Date']>=regr_end_date),'Mom']*weights[0]+df.loc\
    [(df['Date']<=date)&(df['Date']>regr_end_date),'Rev']*weights[1]+df.loc[(df['Date']<=date)&(df['Date']>=regr_end_date),'Std']*weights[2]
    
    #print("R2 for "+regr_date+" is "+str(regr.rsquared))

    
    return df