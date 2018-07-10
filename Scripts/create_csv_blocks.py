import csv
import os

#specific to block code
from approximate_assignment_blocks import *
from discrete_measures_blocks import *

import geopandas as gpd
import json
import time

def dict_invert(dictionary):
  dict = {val: [key for key in dictionary.keys() if dictionary[key] == val] for val in dictionary.values()}
  return dict

state_codes = dict_invert({
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'NJ': '34', 'NM': '35', 'TX': '48', 'LA': '22',
    'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36', 'PA': '42',
    'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08', 'CA': '06',
    'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13', 'IN': '18',
    'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09', 'ME': '23',
    'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29', 'MN': '27',
    'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28', 'SC': '45',
    'KY': '21', 'OR': '41', 'SD': '46'
})

#Grab Districts
districts = gpd.GeoDataFrame.from_file('./districting_plans/cd2013/tl_rd13_us_cd113.shp')
percent_list = [0.5, 0.1]
unit = "bg"

plan_name = "tigerline"
districts["geoid"] = districts["GEOID"]

header_list = ["geoid"]

#####


if unit=="block":


    header_list.extend(["dperim", "dpperim"])
    header_list.extend(["darea", "dparea"])

    data = {}

    for state in ["44","02"]:#state_codes.keys():
        print("state: " + state)
        #initialize_dataframes(state_fips, unit_df, district_df)
        os.chdir('./states/'+state)

        #Retrieve GeoDataFrames
        state_districts = districts.iloc[[districts.iloc[i]['STATEFP'] == state for i in range(len(districts))]]
        #make sure there exists a lowercase geoid column
        state_districts["geoid"] = state_districts["GEOID"]

        for d_geoid in state_districts["geoid"]:
            data[d_geoid] = []

        block_filename = '2010_' + state + '_' + unit + '_pop.shp'
        state_units = gpd.GeoDataFrame.from_file(block_filename)
        state_units["geoid"] = state_units["GEOID10"]

        #TODO: check if membership has already been computed
        print('working on making membership files')
        membership = make_membership_dict(state_districts, state_units)
        with open(state + '_' + unit + '_membership.json', 'w') as fp:
            json.dump(membership, fp)





            d_perim = {}
            d_area = {}


            print('working on approximating districts')

            ########approx_districts=state_districts
            with open(state + "_" + unit + "approximated_by_block" +  ".json", "w") as fp:
                json.dump((approx_districts.to_json(), membership), fp)


            print('computing discrete measures')
            (perim, area) = discrete_perim_and_area(state_districts, state_units, membership, pop_field = "P0010001")
            d_perim.update(perim)
            d_area.update(area)

    #note that we're not doing prjections when calculating percent inclusion

            for dist_geoid in state_districts["geoid"]:
                data[dist_geoid].extend(d_perim[dist_geoid])
                data[dist_geoid].extend(d_area[dist_geoid])
        os.chdir("../../")

os.chdir("./tables")
#save_d_data(data, name, path)
with open(plan_name + "_" + unit + '.csv', 'w', newline='') as csvfile:
    metric_writer = csv.writer(csvfile, delimiter=',',\
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
    metric_writer.writerow(header_list)
    for d_geoid in data.keys():
        metric_writer.writerow([d_geoid,*data[d_geoid]])
