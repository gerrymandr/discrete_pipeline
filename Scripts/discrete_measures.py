import geopandas as gpd
import pandas as pd
import shapely.wkt
import networkx as nx

def discrete_perim_and_area(df_dist, df_units, membership, approx_assignment, prorate = False, pop_field = "P0010001"):
    perim = {}
    area = {}
    for i, dist in df_dist.iterrows():
        perim[dist["geoid"]] = []
        dist_units = membership[dist["geoid"]]
        tmp_dperim = 0
        tmp_dpperim = 0
        tmp_dperim_pro = 0
        tmp_dpperim_pro = 0

        tmp_darea = 0
        tmp_dparea = 0
        tmp_darea_pro = 0
        tmp_dparea_pro = 0
        for j, unit in df_units.iterrows():
            if unit["geoid"] in approx_assignment[dist["geoid"]]:
                tmp_darea += 1
                tmp_dparea += unit[pop_field]
                if prorate:
                    tmp_darea_pro += dist_units[unit["geoid"]]
                    tmp_dparea_pro += unit[pop_field]*dist_units[unit["geoid"]]
                if unit.geometry.intersects(dist.geometry.boundary):
                    tmp_dperim += 1
                    tmp_dpperim += unit[pop_field]
                    if prorate:
                      tmp_dperim_pro += dist_units[unit["geoid"]]
                      tmp_dpperim_pro += unit[pop_field]*dist_units[unit["geoid"]]
        perim[dist["geoid"]] = [tmp_dperim, tmp_dpperim]
        if prorate:
            perim[dist["geoid"]].extend([tmp_dperim_pro, tmp_dpperim_pro])
        
        area[dist["geoid"]] = [tmp_darea, tmp_dparea]
        if prorate:
            area[dist["geoid"]].extend([tmp_darea_pro, tmp_dparea_pro])
    return (perim, area)