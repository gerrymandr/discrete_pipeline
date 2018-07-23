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
    bb1 = axarr[0,0].get_position()
    bb2 = axarr[0,1].get_position()
    bb3 = axarr[1,0].get_position()
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
    selected[0].set_visible(True)
    selected[0].set_data([x1[ind1]], [y1[ind1]])

    ind2 = geoids2.index(selected_geoid)
    selected[1].set_visible(True)
    selected[1].set_data([x2[ind2]], [y2[ind2]])

    ind3 = geoids3.index(selected_geoid)
    selected[2].set_visible(True)
    selected[2].set_data([x3[ind3]], [y3[ind3]])
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
    axarr[1,1].clear()
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
            axarr[1,1].add_patch(patch)
            axarr[1,1].axis('scaled')
    axarr[1,1].add_patch(special_patch)
    axarr[1,1].axis('scaled')
    axarr[1,1].set_title("district " + str(int(geoid[2:])) + " in " +
                  fips_dict[geoid[:2]])
    plt.draw()


f, axarr = plt.subplots(2, 2)
selected = []

xvec = "rank_a/p^2 (b) 0.5"
yvec = "rank_a/p^2 (g) 0.5"
xtable_name = "big_table.csv"
ytable_name = "big_table.csv"

# xvec = "rank_tiger_aland"
# yvec = "tiger_rank_c_4pi*a/p^2"
# xtable_name = "zoom_table.csv"
# ytable_name = "zoom_table.csv"
(x1, y1, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected.extend(axarr[0,0].plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False))

axarr[0,0].plot(x1, y1, 'o', picker=10, color='purple')
axarr[0,0].set_title("Scatter plot of " + xvec + " and " + yvec)
axarr[0,0].set_ylabel(ytable_name + " : " + yvec)
axarr[0,0].set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x1, y1)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
axarr[0,0].text(0.05, 0.95, str(tau)[:6], transform=axarr[0,0].transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)

xvec = "rank_a/p^2 (g) 0.5"
yvec = "rank_a/p^2 (t) 0.5"
xtable_name = "big_table.csv"
ytable_name = "big_table.csv"
(x2, y2, geoids2) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected.extend(axarr[0,1].plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False))

axarr[0,1].plot(x2, y2, 'o', picker=10, color='purple')
axarr[0,1].set_title("Scatter plot of " + xvec + " and " + yvec)
axarr[0,1].set_ylabel(ytable_name + " : " + yvec)
axarr[0,1].set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x2, y2)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
axarr[0,1].text(0.05, 0.95, str(tau)[:6], transform=axarr[0,1].transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)

xvec = "rank_a/p^2 (t) 0.5"
yvec = "rank_a/p^2 (b) 0.5"
(x3, y3, geoids3) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected.extend(axarr[1, 0].plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False))

axarr[1, 0].plot(x3, y3, 'o', picker=10, color='purple')
axarr[1, 0].set_title("Scatter plot of " + xvec + " and " + yvec)
axarr[1, 0].set_ylabel(ytable_name + " : " + yvec)
axarr[1, 0].set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x3, y3)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
axarr[1,0].text(0.05, 0.95, str(tau)[:6], transform=axarr[1,0].transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)
'''
xvec = "tiger_rank_c_4pi*a/p^2"
yvec = "20m_rank_c_4pi*a/p^2"
(x4, y4, geoids1) = different_table_plot(xtable_name, ytable_name,
                                         xvec, yvec)
selected4 = ax4.plot(0, 0, 'o', ms=12, alpha=1, color='red', visible=False)[0]

ax4.plot(x4, y4, 'o', picker=10, color='purple')
ax4.set_title("Scatter plot of " + xvec + " and " + yvec)
ax4.set_ylabel(ytable_name + " : " + yvec)
ax4.set_xlabel(xtable_name + " : " + xvec)

tau, p_value = stats.kendalltau(x4, y4)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
ax4.text(0.05, 0.95, str(tau)[:6], transform=ax4.transAxes, fontsize=14, 
        verticalalignment='top', bbox=props)
'''
f.canvas.mpl_connect('pick_event', on_pick)
plt.suptitle("Comparing Polsby Popper scores across cartographic boundary resolutions (with normalized Kendall tau scores)", 
             fontsize = 22)
