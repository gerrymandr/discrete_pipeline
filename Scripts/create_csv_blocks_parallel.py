# specific to block code
from approximate_assignment_blocks import *
from discrete_measures_blocks import *

import csv
import os
import geopandas as gpd
import time
import threading
import psutil


def discrete_perim_and_area(df_dist, df_units, membership):
    '''
    This used to be in discrete_measures_blocks.py
    '''
    perim = {}
    area = {}
    for i, dist in df_dist.iterrows():
        perim[dist["geoid"]] = []

        tmp_dperim = 0
        tmp_dpperim = 0
        tmp_darea = 0
        tmp_dparea = 0

        for j, unit in df_units.iterrows():
            if unit["geoid"] in membership[dist["geoid"]]:
                tmp_darea += 1
#                tmp_dparea += unit[pop_field]  #uncomment to use population
                if unit.geometry.intersects(dist.geometry.boundary):
                    tmp_dperim += 1
#                    tmp_dpperim += unit[pop_field]  #uncomment to use pop
        perim[dist["geoid"]] = [tmp_dperim, tmp_dpperim]
        area[dist["geoid"]] = [tmp_darea, tmp_dparea]
    return (perim, area)


def dict_invert(dictionary):
    dict = {val: [key for key in dictionary.keys() if dictionary[key] == val]
            for val in dictionary.values()}
    return dict


def csv_to_dict(path):
    with open(path, mode="r") as f:
        return dict(csv.reader(f))


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


SLEEP_TIME = 1


def compute_measures(state):
# make sure you are on the right directory, maybe a failed thread failed to bring you back.

#   #Nel wrote these lines but they are commented for the sake of pushing to the github
#    if os.getcwd() != '/Users/Nel/discrete_pipeline/Scripts':
#        os.chdir('/Users/Nel/discrete_pipeline/Scripts')
    
    #Grab Districts
    districts = gpd.GeoDataFrame.from_file('./sample_data/sample_districts.shp')
    try:
        os.mkdir('./states/' + state)
    except:
        print('file exists already')
    unit = "block"

    plan_name = "tigerline"
    districts["geoid"] = districts["GEOID"]

    header_list = ["geoid"]

    #####

    print (time.time()-start)

    header_list.extend(["dperim", "dpperim"])
    header_list.extend(["darea", "dparea"])

    data = {}

#    for sample data, put sample_blocks.shp in states/00
#    for state in ["00", ]:#state_codes.keys():    #"00" is the name of the state folder for the sample data
    print(state)
    #initialize_dataframes(state_fips, unit_df, district_df)
    state_path = './states/{}'.format(state)
    os.chdir(state_path)

    #Retrieve GeoDataFrames
    #state_districts = districts.iloc[[districts.iloc[i]['STATEFP'] == state for i in range(len(districts))]]    #uncomment to use on non-sample
    state_districts = districts   #comment to use for non-sample
    #make sure there exists a lowercase geoid column
    state_districts["geoid"] = state_districts["GEOID"]
    print(len(state_districts["geoid"]))

    for d_geoid in state_districts["geoid"]:
        data[d_geoid] = []

    #block_filename = '2010_' + state + '_' + unit + '_pop.shp'
    block_filename = 'sample_blocks.shp'
    state_units = gpd.GeoDataFrame.from_file(block_filename)
    #state_units["geoid"] = state_units["GEOID10"]
    state_units["geoid"] = state_units["GEOID"]

    #TODO: check if membership has already been computed
    print('working on making membership files')
    block_assignment_path = "../../sample_data/assignment.csv"
    block_assignment = csv_to_dict(block_assignment_path)
    membership = dict_invert(block_assignment)

    #membership = make_membership_dict(state_districts, state_units)

    d_perim = {}
    d_area = {}

    ########approx_districts=state_districts
    #with open(state + "_" + unit + "approximated_by_block" +  ".json", "w") as fp:
    #json.dump((approx_districts.to_json(), membership), fp)

    print('computing discrete measures')
    #(perim, area) = discrete_perim_and_area(state_districts, state_units, membership, pop_field = "P0010001")
    (perim, area) = discrete_perim_and_area(state_districts, state_units, membership)   #use this for no population sample

    d_perim.update(perim)
    d_area.update(area)

    # note that we're not doing prjections when calculating percent inclusion
    for dist_geoid in state_districts["geoid"]:
        data[dist_geoid].extend(d_perim[dist_geoid])
        data[dist_geoid].extend(d_area[dist_geoid])
    os.chdir("../../")

    os.chdir("./tables")
    print(time.time() - start)
    # save_d_data(data, name, path)
    with open(plan_name + "_" + state + "_" + unit + '.csv', 'w', newline='') as csvfile:
        metric_writer = csv.writer(csvfile, delimiter=',',\
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)
        metric_writer.writerow(header_list)
        for d_geoid in data.keys():
            metric_writer.writerow([d_geoid,*data[d_geoid]])

        print(time.time() - start)

def threaded_states(state_queue):
    start = time.time()    
    # the queue of statess that still need to be checked
    # state_queue = ["00", "01", "02"]

    # This function grabs an element of the list of state and applies our function to it.
    def process_queue():
        while True:
            try:
                statex = state_queue.pop()
            except IndexError:
                # crawl queue is empty
                break
            else:
                compute_measures(statex)
                
    threads = []
    while state_queue:
        # If there the state list is not empty proceed:
        # print(os.getcwd())
        # print(state_queue)
        # print(threads)
        # the crawl is still active
        for thread in threads:
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        # If machine under too much pressure wait a second and try again
        while ((psutil.cpu_percent() < 60.) and
               (os.getloadavg()[0] < 3.) and
               (psutil.virtual_memory().percent < 50.) and
               state_queue):
            # can start some more threads
            thread = threading.Thread(target=process_queue)
            # set daemon so main thread can exit when receives ctrl-c
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
            # all threads have been processed
            # sleep temporarily so CPU can focus execution elsewhere
            time.sleep(SLEEP_TIME)


# You call this like this
# threaded_states(["00", "01", "02"])
threaded_states(["00"])
