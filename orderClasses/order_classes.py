import numpy as np
import pandas as pd
data=pd.read_csv('media/csv/demo.csv',encoding='gbk')


x=data.iloc[:,1:-1]
y=data.iloc[:,-1:]
from sklearn.linear_model import LinearRegression
model=LinearRegression().fit(x,y)




