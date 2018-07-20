# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:24:29 2018

@author: assaf, adriana
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import scipy.stats as stats


# create a dictionary of FIPS code : state name for titles
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n',
                   dtype={"STATE": str, "FIP": str})
fips_dict = {}
for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]: row["STATE"]})


def different_table_plot(xtable_name, ytable_name, xvec, yvec):

    # read and merge relevant dataframes
    df1 = pd.read_csv(xtable_name, dtype={"geoid": str})
    df2 = pd.read_csv(ytable_name, dtype={"geoid": str})

    xdf = df1["geoid"].to_frame()
    xdf["xname"] = df1[xvec]

    ydf = df2["geoid"].to_frame()
    ydf["yname"] = df2[yvec]

    mergedf = xdf.merge(ydf, left_on="geoid", right_on="geoid")

    # the order of these lists is important.
    x = mergedf["xname"]
    y = mergedf["yname"]
    geoids = mergedf["geoid"]
    return (x, y, list(geoids))


def find_subplot(event):
    mouse = event.mouseevent
    (fx, fy) = f.transFigure.inverted().transform((mouse.x, mouse.y))
    bb1 = ax1.get_position()
    bb2 = ax2.get_position()
    bb3 = ax3.get_position()
    if bb1.contains(fx, fy):
        return 1
    if bb2.contains(fx, fy):
        return 2
    if bb3.contains(fx, fy):
        return 3
    return 0


def highlight_event(event, plotnum):
    ind = event.ind[0]
    if plotnum == 1:
        selected_geoid = geoids1[ind]
    if plotnum == 2:
        selected_geoid = geoids2[ind]
    if plotnum == 3:
        selected_geoid = geoids3[ind]

    ind1 = geoids1.index(selected_geoid)
    selected1.set_visible(True)
    selected1.set_data([x1[ind1]], [y1[ind1]])

    ind2 = geoids2.index(selected_geoid)
    selected2.set_visible(True)
    selected2.set_data([x2[ind2]], [y2[ind2]])

    ind3 = geoids3.index(selected_geoid)
    selected3.set_visible(True)
    selected3.set_data([x3[ind3]], [y3[ind3]])
    return selected_geoid


# this function is called when a point is clicked
def on_pick(event):
    plotnum = find_subplot(event)
    selected_geoid = highlight_event(event, plotnum)
    # x_df is the dataframe I use to plot the district
    x_df = gpd.read_file("../approx_unit_run/districting_plans/" +
                         "cb_2013_us_cd113_500k/" +
                         "cb_2013_us_cd113_500k.shp")
    if selected_geoid:
        if selected_geoid[2:] == "ZZ":
            print("district made of water :o")
        else:
            # draws the map that happens when you click a point
            drawmap(selected_geoid, x_df)
    f.canvas.draw()


def drawmap(geoid, df):
    # create a new figure
    # fig2, ax2 = plt.subplots()
    ax4.clear()
    patchdict = {}
    for i, dist in df.iterrows():
        if dist["GEOID"] == geoid:
            # this patch corresponds to the district in question
            special_patch = PolygonPatch(dist.geometry, fc='#ff6a06',
                                         ec='#D3D3D3', alpha=1, zorder=2)
        if dist["GEOID"][:2] == geoid[:2]:  # only add the rest of the state
            # these patches correspond to all other districts
            patch = PolygonPatch(dist.geometry, fc='#D3D3D3',
                                 ec='#D3D3D3', alpha=1, zorder=2)
            patchdict.update({i: patch})
            ax4.add_patch(patch)
            ax4.axis('scaled')
    ax4.add_patch(special_patch)
    ax4.axis('scaled')
    ax4.set_title("district " + str(int(geoid[2:])) + " in " +
                  fips_dict[geoid[:2]])
    plt.draw()


f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)


xvec = "500k_rank_4pi*a/p^2"
yvec = "rank_a/p^2 (g) 0.5"
xtable_name = "zoom_table.csv"
ytable_name = "zoom_table.csv"

(x1, y1, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected1 = ax1.plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False)[0]

ax1.plot(x1, y1, 'o', picker=10, color='purple')
ax1.set_title("Scatter plot of " + xvec + " and " + yvec)
ax1.set_ylabel(ytable_name + " : " + yvec)
ax1.set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x1, y1)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
ax1.text(0.05, 0.95, str(tau)[:6], transform=ax1.transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)

xvec = "rank_a/p^2 (g) 0.5"
yvec = "rank_a/p^2 (t) 0.5"
(x2, y2, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected2 = ax2.plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False)[0]

ax2.plot(x2, y2, 'o', picker=10, color='purple')
ax2.set_title("Scatter plot of " + xvec + " and " + yvec)
ax2.set_ylabel(ytable_name + " : " + yvec)
ax2.set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x2, y2)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
ax2.text(0.05, 0.95, str(tau)[:6], transform=ax2.transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)

xvec = "rank_a/p^2 (t) 0.5"
yvec = "rank_a/p^2 (b) 0.5"
(x3, y3, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected3 = ax3.plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False)[0]

ax3.plot(x3, y3, 'o', picker=10, color='purple')
ax3.set_title("Scatter plot of " + xvec + " and " + yvec)
ax3.set_ylabel(ytable_name + " : " + yvec)
ax3.set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x3, y3)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
ax3.text(0.05, 0.95, str(tau)[:6], transform=ax3.transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)
'''
xvec = "rank_tiger_aland"
yvec = "tiger_rank_c_4pi*a/p^2"
(x4, y4, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected4 = ax4.plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False)[0]

ax4.plot(x4, y4, 'o', picker=10, color='purple')
ax4.set_title("Scatter plot of " + xvec + " and " + yvec)
ax4.set_ylabel(ytable_name + " : " + yvec)
ax4.set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x4, y4)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
ax4.text(0.05, 0.95, str(tau)[:6], transform=ax3.transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)
'''
f.canvas.mpl_connect('pick_event', on_pick)
plt.suptitle("Comparing discrete Polsby Popper scores across unit resolutions (with normalized Kendall tau scores)", 
             fontsize = 22)
