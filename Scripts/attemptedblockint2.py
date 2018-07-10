if unit=="block":
    header_list.extend(["dperim_", "dpperim_", "dperim_pro_", "dpperim_pro_"])
    header_list.extend(["darea_", "dparea_", "darea_pro_", "dparea_pro_"])
    header_list.extend(["carea_", "cperim_"])

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
