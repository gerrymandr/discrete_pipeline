#import math
import geopandas as gpd
import shapely.wkt
import networkx as nx
import pysal
   
def make_membership_dict(districts, units):
    '''
    
    '''
    membership = {}

    for i, dist in districts.iterrows():
        d_geoid = dist["geoid"]
        membership[d_geoid] = {}

        for j, unit in units.iterrows():
            u_geoid = unit["geoid"]
            if unit.geometry.intersects(dist.geometry):
                joint_area = (dist.geometry.intersection(unit.geometry)).area #Get intersecting area
                percent_inside = joint_area/unit.geometry.area
                membership[d_geoid].update({u_geoid: percent_inside})
            else:
                membership[d_geoid].update({u_geoid: 0})
    return membership

def make_approx_geometries(units, membership, inclusion_percent):
    approx_geoms = []
    geoids = []
    approx_df = gpd.GeoDataFrame()
    approx_assignment = {}
    
    for d_geoid in membership.keys():
        approx_assignment[d_geoid] = []
        tmp_geom = shapely.wkt.loads("GEOMETRYCOLLECTION EMPTY") #Create empty object to reform geometry
        for j, unit in units.iterrows():
            if membership[d_geoid][unit["geoid"]] > inclusion_percent:
                tmp_geom = tmp_geom.union(unit.geometry) # add the geometry to the approximation
                approx_assignment[d_geoid].append(unit["geoid"])
        approx_geoms.append(tmp_geom)
        geoids.append(d_geoid)
    
    approx_df["geometry"] = approx_geoms
    approx_df["geoid"] = geoids
    return (approx_df, approx_assignment)

def make_adj_graph(units, membership, inclusion_percent):
    graph_dict = {}
    for d_geoid in membership.keys():
        indices_in_dist = []
        for j, unit in units.iterrows():
            if membership[d_geoid][unit["geoid"]] > inclusion_percent:
                indices_in_dist.append(j)
        unit_indices = [index in indices_in_dist for index in range(len(df_units))]
        approx_dist_df = units[unit_indices]

        #build contiguity matrix - uses rook contiguity - queen is available
        contig_matrix = pysal.weights.Rook.from_dataframe(approx_dist_df, idVariable = "geoid")

        #build list of edges - this will create edges going both ways from connected nodes, so you might need to remove duplicates
        nodes = contig_matrix.keys()
        edges = [(node,neighbour) for node in nodes for neighbour in contig_matrix[node]]
        my_graph = nx.Graph(edges)
        graph_dict.update({d_geoid, my_graph})