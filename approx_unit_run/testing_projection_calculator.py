# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 13:41:28 2018

@author: assaf
"""

import geopandas as gpd
import math

UTMS = ["02", "04", "05", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "55"]

class ProjectionCalculator:
    """
    Take a dataframe from Shapefile of census cells and assign respective UTM zones
    """
    def __init__(self, gdf):
        """
        param gdf: dataframe containing census cells (usually VTDs)
        """
        self.gdf = gdf.copy(deep=True)
        self.gdf.columns = map(str.lower, self.gdf.columns)
        self.perim_dict = {}
        self.area_dict = {}
        self.find_utms()
        self.calc_continuous()

    def find_utms(self):
        utm_list = []
        """
        Assign appropriate UTM zone for proper projection.
        """
        for index, dist in self.gdf.iterrows():
            utm = math.floor((dist.geometry.centroid.x+180)*59/354)+1
            utm = str(utm).zfill(2)
            utm_list.append(utm)
        self.gdf['utm'] = utm_list

    def calc_continuous(self):
        """
        Calculate continuous area and perimeters.
        """
        for utm in UTMS:
            my_epsg = '269' + utm
            self.gdf = self.gdf.to_crs({"init": "epsg:" + my_epsg})
            zone = self.gdf.loc[self.gdf['utm'] == utm][['geoid', 'geometry', 'utm']]
            zone["area"] = zone.geometry.area / 1000**2
            zone["perim"] = zone.geometry.length / 1000
            for i, row in zone.iterrows():
                self.area_dict.update({row["geoid"]: row["area"]})
                self.perim_dict.update({row["geoid"]: row["perim"]})

df = gpd.GeoDataFrame.from_file("./districting_plans/cb_2013_us_cd113_20m/cb_2013_us_cd113_20m.shp")

calculator = ProjectionCalculator(df)
new_df = calculator.gdf
