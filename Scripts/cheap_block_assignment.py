'''
cheap_block_assignment
Thomas, Adriana, Assaf
This code combines functions from previous versions of our block discrete measure functions
to figure out which blocks are in which states

file currently does not saved, and membership methodology isn't fully optimized
right now every block is checked against every county, but in reality we can
delete a block from the list of blocks we are trying after its district is found
'''


import geopandas as gpd
import json
import time
import csv
import os

#This is the function that actually makes the membership dictionary
#the membership dictionary tracks which blocks are in which states
def make_membership_dict(districts, units):
    '''
    This used to be in approximate_assignment_blocks.py
    districts: geodataframe of districts with identifier "geoid"
    units: geodataframe of units with

    code returns membership, a dictionary keyed by geiods of districts, whose values are
    lists of geoids corrisponding to blocks whithin that district.
    '''
    membership = {}
    for i, dist in districts.iterrows():
        d_geoid = dist["geoid"]
        membership[d_geoid] = []
        for j, unit in units.iterrows():
            u_geoid = unit["geoid"]
            #because each block is in exactly one district, we cheaply compute a representative point
            #this point is used to determine which district a block is in
            if dist.geometry.contains(unit.geometry.representative_point()):
                membership[d_geoid].append(unit["geoid"])
    return membership

districts = gpd.GeoDataFrame.from_file('./sample_data/sample_districts.shp')
#make sure that geoid is lower case
districts["geoid"] = districts["GEOID"]

    for state in ["00"]:#state_codes.keys():    #"00" is the name of the state folder for the sample data
        print("state: " + state)

        #initialize_dataframes(state_fips, unit_df, district_df)
        os.chdir('./states/'+state)

        #Retrieve GeoDataFrames
        print(len(state_districts["geoid"]))

        #block_filename = '2010_' + state + '_' + unit + '_pop.shp'
        block_filename = 'sample_blocks.shp'
        state_units = gpd.GeoDataFrame.from_file(block_filename)
        state_units["geoid"] = state_units["GEOID"]

        print('working on making membership files')
        membership = make_membership_dict(districts, state_units)
