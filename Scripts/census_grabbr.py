#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 18:30:41 2018
@author: hannah
"""
import requests
import pandas as pd
from pprint import pprint
import os

def dict_invert(dictionary):
  dict = {val: [key for key in dictionary.keys() if dictionary[key] == val] for val in dictionary.values()}
  return dict

# constants
CENSUS_API_KEY = "YOUR KEY HERE"
HOST = "https://api.census.gov/data"

# set year for data and acs5 or sf1 (sf1 stands for summary file 1)
# as of July, 2018 - documentation can be found here: https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1

year = "2010"
dataset = "sf1"
base_url = "/".join([HOST, year, dataset])

# The variables we want are NAME and total population
get_variables = ["NAME", "P0010001"]

# List of all county codes in a txt file in this folder
county_codes = pd.read_csv('full_county_fips_2010.csv', header = None, names = ["STATE", "STATEFP", "COUNTYFP", "COUNTY_NAME", "CLASSFP"], dtype = {"STATE":str, "STATEFP":str, "COUNTYFP":str, "COUNTY_NAME":str, "CLASSFP":str})
# creates a dictionary {state: list of counties in that state}
county_state_dictionary = {county_codes.iloc[i]["STATEFP"] + county_codes.iloc[i]["COUNTYFP"] : county_codes.iloc[i]["STATEFP"] for i in range(len(county_codes))}
state_county_dict = dict_invert(county_state_dictionary)


os.chdir("./states")
#for unit_name in ["block:*", "block group:*", "tract:*"]:

#for state_fips in state_county_dict.keys():
for unit_name in ["tract", "block group"]:#, "block"]:
    if unit_name == "block group":
        uname = "bg"
    else:
        uname = unit_name
#unit_name = "block"
    for state_fips in ["15"]:#state_county_dict.keys():
        print('working on state FIPS: ' + state_fips)
        data = []
        if not os.path.exists(os.path.join(os.getcwd(), state_fips)):
            os.makedirs(os.path.join(os.getcwd(), state_fips))
        os.chdir("./" + state_fips)
        for county_code in state_county_dict[state_fips]:
            predicates = {}         
            predicates["get"] = ",".join(get_variables)
            #### make changes here for tracts
            predicates["for"] = unit_name + ":*"
            #state fips code, here 42 is Pennsylvania 
            predicates["in"] = "state:" + state_fips + "+county:" + county_code[2:]
            predicates["key"] = CENSUS_API_KEY
            # Write the result to a response object:
            response = requests.get(base_url, params=predicates)
            try:
                col_names = response.json()[0]
                data = data + response.json()[1:]
            except :
                print("failed to find data for: " + county_code)
        geoids = [] #initialize geoid vector
        census_df = pd.DataFrame(columns=col_names, data=data)
        for index, row in census_df.iterrows():
            ### make changes here for tracts
            if unit_name == "tract":
                geoid = row["state"] + row["county"] + row[unit_name]
            else:
                geoid = row["state"] + row["county"] + row["tract"] + row[unit_name]
            geoids.append(geoid)
        census_df["GEOID10"] = geoids
        census_df.set_index(["state", "county", "tract"], drop=False, inplace=True)
        # save the new dataframe to a csv in the right directory
        census_df.to_csv("2010_" + state_fips + "_" + uname + "_poptable.csv")
        os.chdir("..")
