# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 20:33:45 2018

@author: assaf
"""

import csv
import os

from approximate_assignment import *
from discrete_measures import *
import geopandas as gpd
import json
import time

def dict_invert(dictionary):
  dict = {val: [key for key in dictionary.keys() if dictionary[key] == val] for val in dictionary.values()}
  return dict

def compute_measures(state, districts, unit):
    percent_list = [0.5, 0.1]
    plan_name = "tigerline"

    header_list = ["geoid"]
    header_list.extend(["carea", "cperim"])

    for percent in percent_list:
        perc = str(percent)
        header_list.extend(["dperim_" + perc, "dpperim_" + perc, "dperim_pro_" + perc, "dpperim_pro_" + perc])
        header_list.extend(["darea_" + perc, "dparea_" + perc, "darea_pro_" + perc, "dparea_pro_" + perc])

    data = {}

    #initialize_dataframes(state_fips, unit_df, district_df)
    os.chdir('./states/'+state)
    
    #Retrieve GeoDataFrames
    state_ind = [districts.iloc[i]['STATEFP'] == state
                 for i in range(len(districts))]
    state_districts = districts.iloc[state_ind]
    if "geoid" not in list(state_districts):
        state_districts["geoid"] = state_districts["GEOID"]
    for d_geoid in state_districts["geoid"]:
        data[d_geoid] = []
    
    unit_filename = '2010_' + state + '_' + unit + '_pop.shp'
    state_units = gpd.GeoDataFrame.from_file(unit_filename)
    state_units["geoid"] = state_units["GEOID10"]
    
    #TODO: check if membership has already been computed
    print('working on making membership files')
    membership = make_membership_dict(state_districts, state_units)
    with open(state + '_' + unit + '_membership_percentages.json', 'w') as fp:
        json.dump(membership, fp)
        
    for inclusion_percent in percent_list:
        #TODO: make_data(membership, units_df, districts) - maybe make this a class?
        d_perim = {}
        d_area = {}
        perc = str(inclusion_percent*100)
        
        #TODO: check if already exists
        print('working on approximating districts')
        (approx_districts, approx_assignment) = make_approx_geometries(state_units, membership, inclusion_percent)        
        with open(state + "_" + unit + "_approx_" + perc + ".json", "w") as fp:
            json.dump((approx_districts.to_json(), approx_assignment), fp)

        #TODO: check if already exists
        print('computing discrete measures')            
        (perim, area) = discrete_perim_and_area(state_districts, state_units, membership, approx_assignment, prorate = True, pop_field = "P0010001")
        d_perim.update(perim)
        d_area.update(area)
    
        carea = {}
        cperim = {}
        
        for dist_geoid in state_districts["geoid"]:
            #data[dist_geoid].extend([carea[dist_geoid],cperim[dist_geoid]])
            data[dist_geoid].extend(d_perim[dist_geoid])
            data[dist_geoid].extend(d_area[dist_geoid])

    print('running continuous metrics')
    proj = ProjectionCalculator(state_districts)
    for i, dist in proj.gdf.iterrows():
        carea[dist["geoid"]] = dist.geometry.area
        cperim[dist["geoid"]] = dist.geometry.length

    os.chdir("../../")
    if not os.path.exists(os.path.join(os.getcwd(),"./tables")):
        os.makedirs(os.path.join(os.getcwd(),"./tables"))
    os.chdir("./tables")
    #save_d_data(data, name, path)
    with open(plan_name + "_" + state + "_" + unit + '.csv', 'w', newline='') as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=',',\
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)
        metric_writer.writerow(header_list)
        for d_geoid in data.keys():
            print(carea[d_geoid])
            print(type(carea[d_geoid]))
            metric_writer.writerow([d_geoid, carea[d_geoid], cperim[d_geoid], *data[d_geoid]])


dist_df = gpd.GeoDataFrame.from_file("./districting_plans/cd2013/"
                                           + "tl_rd13_us_cd113.shp")
compute_measures("15", dist_df, "tract")
