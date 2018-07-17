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
    state_districts.crs = {'init': 'epsg:2163'}
    
    unit_filename = '2010_' + state + '_' + unit + '_pop.shp'
    state_units = gpd.GeoDataFrame.from_file(unit_filename)
    state_units["geoid"] = state_units["GEOID10"]
    state_units.crs = {'init': 'epsg:2163'}

    #TODO: check if membership has already been computed
    print('looking for membership files')
    mem_file_name = state+ "_" + unit + "_membership_percentages.json"
    try:
        with open(mem_file_name) as json_data:
            membership = json.load(json_data)
            print("found membership files!")
    except:
        print("failed to find existing membership files, making new ones")
        membership = make_membership_dict(state_districts, state_units)
        with open(state + '_' + unit + '_membership_percentages.json', 'w') as fp:
            json.dump(membership, fp)

    for inclusion_percent in percent_list:
        #TODO: make_data(membership, units_df, districts) - maybe make this a class?
        d_perim = {}
        d_area = {}
        perc = str(inclusion_percent*100)

        approx_file = state + "_" + unit + "_approx_" + perc + ".json"
        try:
            with open(approx_file) as json_data:
                (approx_districts, approx_assignment) = json.load(json_data)
                print("I found some approximated districts! Using them...")
        except:
            print("No approximated data found... working on approximating districts")
            (approx_districts, approx_assignment) = make_approx_geometries(state_units, membership, inclusion_percent)
            with open(state + "_" + unit + "_approx_" + perc + ".json", "w") as fp:
                json.dump((approx_districts.to_json(), approx_assignment), fp)

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
            metric_writer.writerow([d_geoid, carea[d_geoid], cperim[d_geoid], *data[d_geoid]])


dist_df = gpd.GeoDataFrame.from_file("./districting_plans/cd2013/"
                                           + "tl_rd13_us_cd113.shp")
states = ['53', '10', '11', '55','54',
          '15', '12', '56', '34', '35',
          '48', '22', '37', '38', '31',
          '47', '36', '42', '02', '32',
          '33', '51', '08', '06', '01',
          '05', '50', '17', '13', '18',
          '19', '25', '04', '16', '09',
          '23', '24', '40', '39', '49',
          '29', '27', '26', '44', '20',
          '30', '28', '45', '21', '41', '46']
for i in ["01"]:#states:
    print(os.getcwd())
    compute_measures(i, dist_df, "tract")
    print("done fips: "+i)
