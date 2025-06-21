# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
#from pandas_datareader import data
from datetime import datetime as dt
from pandas.tseries.offsets import BDay
#import pickle
#import dill

#Please include 'ss' and 'sz' directories in my folder to run the code effectively
#os.chdir("Code")
#from Security import Security
#from Data_Puller import sec_create
from M_scorer import m_score_weights
from Portfolio import Portfolio
from Strategy import Strategy
#os.chdir("..//S&P 500 EOD")

###HYPERPARAMETERS
rebal_period=10
ed='2017-01-01'                                                 #End Date
end_of_in_sample="2015-11-03"                                   #Last date of In sample data
end_of_out_sample="2017-02-21"                                   #Last date of Out sample data
num_signals=10
sd='2006-08-15'                                                #Starting date
leverage=2


"""
all_data=pd.DataFrame()
count=0
for file in os.listdir():

    try:
        df=pd.read_csv(file)
        df['Ret']=df['Close']/df['Close'].shift(1)-1
        df['Adj Close']=df['Close']
        df['Mom']=np.log(df['Adj Close'].shift(1)/df['Adj Close'].shift(5))
        df['Rev']=np.log(df['Adj Close'].shift(25)/df['Adj Close'].shift(1))
        df['Std']=df['Ret'].rolling(30).std()
        all_data=all_data.append(df)
        count+=1
        print(file,count)
    except:
        continue
    
all_data1.to_csv("Data2.csv")
all_data1=all_data.dropna()
all_data=m_score_weights(all_data,ed) 
all_data['Ticker']=all_data['Symbol']                     
"""
#data_missing=1

"""
while(data_missing>0 and data_missing<10):
    try:
        mktdf=data.get_data_yahoo('^BSESN', sd,end_of_out_sample)    #Market Index data
        data_missing=0
    except:
        data_missing+=1
        """

all_data=pd.read_csv("Data.csv")
all_data=all_data.loc[all_data['Date']>=sd]
all_data=all_data.loc[all_data['Volume']>10000]
#Initializing date as the date we will start our backtesting loop
#Note we start with initial date+100 BDays since we need 100 days for Beta calculation

old_data=all_data.copy()

#I have completed following parameter tests (using cross validation), now choosing best params out of-;
# Mom_periods->5,10,15,20
# Rev_periods->10,15,20,25
# Vol_periods->10,20,30,40
i=5
j=20
k=20
            
date=(dt.strptime(sd,"%Y-%m-%d")+BDay(100)).strftime("%Y-%m-%d")
s=Strategy(old_data,date)
all_data=s.modify_predictors(i,j,k)

#Old holdings will keep track of our Buys and Sells in previous period of each
#time period
old_holdings=pd.DataFrame()
trades_sheet=pd.DataFrame(columns=['Date','Ticker','Signal','Shares'])

#old_Beta=0.0
pf_val=10000000.0
pf_vals=pd.DataFrame()

while date<=end_of_out_sample:
    
    all_data=m_score_weights(all_data,date)
    #s.subset_vol(1000000)
    
    date2=(dt.strptime(date,"%Y-%m-%d")+BDay(rebal_period)).strftime("%Y-%m-%d")
    
    #Checking whether we have market data for that date.
    while len(all_data.loc[all_data['Date']==date2])==0 and date2<=end_of_in_sample:
        date2=(dt.strptime(date2,"%Y-%m-%d")+BDay(1)).strftime("%Y-%m-%d")
    temp=all_data['Ticker'].loc[all_data['Date']==date].isin(all_data['Ticker'].loc\
    [all_data['Date']==date2])
    temp2=temp.index[temp==True]
    temp3=all_data.loc[all_data.index.isin(temp2)]
    
    s=Strategy(temp3,date)
    cur_holdings=s.signal_generator(num_signals)                        #Current holdings
    p=Portfolio(old_holdings,cur_holdings,all_data,date,pf_val)
    #cur_Beta,new_mkt_price=p.calc_Betas(mktdf)
    
    #Next checking if we are still in first time period before doing Pnl computations
    if len(old_holdings)>0:
        #mkt_ret=old_mkt_price/new_mkt_price-1
        old_pf_val=pf_val
        
        pf_val,pf_ret,date=p.compute_PnL(num_signals)                   #Adding stock returns
        if pf_val!=pf_val:
            print("PF Val is an NA")
            break
        #pf_val+=mkt_ret*old_pf_val*old_Beta/num_signals-abs(cur_Beta*\
        #pf_val-old_Beta*old_pf_val)*0.001/num_signals                   #Adding mkt returns                     
                                                            
        pf_vals=pf_vals.append([[date,pf_val]])
        print("Your new Pf Value at "+date+" is "+str(pf_val))
        #Appending trades to trades sheet to keep track of all of them
        trades_sheet=p.generate_trades_sheet(trades_sheet,pf_val,num_signals)
        
    #old_mkt_price=new_mkt_price
    old_holdings=cur_holdings
    #old_Beta=cur_Beta
    #Updating date to next rebalancing time point
    date=date2
    #break

os.chdir("New_results")

#trades_sheet.to_csv("Fixed_10_stocks_Trades2.csv")
#pf_vals.columns=['Date','Pf_Value']
#pf_vals.to_csv("Fixed_10_stocks_PF.csv")

os.chdir("..")

results=pd.DataFrame()
for result in os.listdir("Rebal_10_results"):
    if result.endswith("PF.csv"):
        pf_result=pd.read_csv("Rebal_10_results//"+result)
        results=results.append(p.perf_eval(pf_result,rebal_period,result))

results.columns=['Portfolio','Sharpe','Annual_Ret','Annual_std','MaxDD']
results.to_csv("Results.csv")
        
best_pf=results.loc[results['Sharpe']==np.max(results['Sharpe'])]

print("\nBEST IN SAMPLE DATA PORTFOLIO STATISTICS:")
print("Sharpe Ratio: "+str(best_pf['Sharpe'].values[0]))
print("Annual Return: "+str(best_pf['Annual_Ret'].values[0]))
print("Annual Std: "+str(best_pf['Annual_std'].values[0]))
print("MaxDD: "+str(best_pf['MaxDD'].values[0]))
print("\nThe best pf combination is "+str(result.split('.')[0]))
