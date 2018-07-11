# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:03:11 2018

@author: assaf
"""

new_dict = []
with open('assignment.csv', 'w', newline='') as csvfile:
    for district in membership.keys():
        for unit in membership[district]:
            metric_writer = csv.writer(csvfile, delimiter=',',\
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
            metric_writer.writerow([unit, district])