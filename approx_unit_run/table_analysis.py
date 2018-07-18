# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:24:29 2018

@author: assaf, adriana
"""
import pandas as pd
import matplotlib.pyplot as plt

unit = "bg"
file = "tigerline"
#plot_df = pd.read_csv("./tables_merged/" + file + "_" + unit + ".csv")
#plot_df.plot(x="rank_dpolsby_0.1", y="rank_dpolsby_pro_0.1", 
#             title = "Scores for " + unit + "'s from: " + file, 
#             kind = 'scatter')

def different_table_plot(xtable_name, ytable_name, xvec, yvec):
    #xtable_name = "cb20m_bg.csv"
    #ytable_name = "cb5m_bg.csv"
    #xvec = "rank_cpolsby"
    #yvec = "rank_cpolsby"
    
    df1 = pd.read_csv("./tables_merged/" + xtable_name, dtype={"geoid":str})
    df2 = pd.read_csv("./tables_merged/" + ytable_name, dtype={"geoid":str})
    
    xdf = df1["geoid"].to_frame()
    xdf["xname"] = df1[xvec]
    
    ydf = df2["geoid"].to_frame()
    ydf["yname"] = df2[yvec]
    
    mergedf = xdf.merge(ydf, left_on="geoid", right_on="geoid")
    
    x = mergedf["xname"]
    y = mergedf["yname"]
    
    plt.scatter(x,y)
    plt.title("Scatter plot of " + xvec + " and " + yvec)
    plt.ylabel(ytable_name + " : " + yvec)
    plt.xlabel(xtable_name + " : " + xvec)

different_table_plot("cb500k_bg.csv", "tigerline_bg.csv", "rank_cpolsby", "rank_cpolsby")
#plt.figure
#plt.scatter(x,y)
