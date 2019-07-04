# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv('20190704-144116_noservices.txt', names=['delta'])

df['rate'] = 1.0/df['delta']

sns.distplot( df.loc[df.rate>100, 'rate'])

print (df.loc[df.rate>100, 'rate'].mean())
print "+-"
print (df.loc[df.rate>100, 'rate'].std())
