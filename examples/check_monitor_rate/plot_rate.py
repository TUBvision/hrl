# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


#fnames = ['20190704-144237_services.txt',
#          '20190704-145730_services.txt',
#          '20190704-145602_services.txt',
#          '20190704-150000_services.txt']

  
fnames = ['20190704-144116_noservices.txt',
          '20190704-145052_noservices.txt',
          '20190704-144954_noservices.txt',
          '20190704-145453_noservices.txt']
  

for f in fnames:
    
    df = pd.read_csv(f, names=['delta'])
    
    df['rate'] = 1.0/df['delta']
    
    rate = df.loc[df.rate>100, 'rate']
    
    plt.figure()
    sns.distplot(rate)
    plt.title('%s // %f +- %f Hz ' % (f, rate.mean(), rate.std()))

