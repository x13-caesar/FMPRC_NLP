#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 
import os 

merged = pd.concat([pd.read_csv('./data/'+f, header=0) for f in os.listdir('./data/') if os.path.splitext(f)[1] == '.csv'])
merged.dropna(axis=0, inplace=True)
merged.drop_duplicates(['title'], inplace=True)
merged.to_csv( "merged.csv", index=False, encoding='utf-8-sig')