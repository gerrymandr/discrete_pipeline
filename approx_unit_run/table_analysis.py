# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:24:29 2018

@author: assaf, adriana
"""

unit = "bg"
file = "tigerline"
#plot_df = pd.read_csv("./tables_merged/" + file + "_" + unit + ".csv")
#plot_df.plot(x="rank_dpolsby_0.1", y="rank_dpolsby_pro_0.1", 
#             title = "Scores for " + unit + "'s from: " + file, 
#             kind = 'scatter')

def myplot(xtable_name, ytable_name, xvec, yvec):
    df1 = pd.read_csv("./tables_merged/" + xtable_name)
    df2 = pd.read_csv("./tables_merged/" + ytable_name)
    x = df1[xvec]
    y = df1[yvec]
    plt.scatter(x,y)
    plt.title("Scatter plot of " + xvec + " and " + yvec)
    plt.ylabel(ytable_name + " : " + yvec)
    plt.xlabel(xtable_name + " : " + xvec)

myplot("cb20m_bg.csv", "tigerline_bg.csv", "rank_cpolsby", "rank_dpolsby_0.1")
#plt.figure
#plt.scatter(x,y)
