# -*- coding: utf-8 -*-
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import tqdm
import pickle
import googlemaps

ZONE_GPD = 'data/NYC Taxi Zones/NYC Taxi Zones.geojson'
nycZones = gpd.read_file(ZONE_GPD)

API_KEY = 'AIzaSyB2gMJIVVvlpgRoGkHOzWqe_s6WcEXN9Eo'
gmaps = googlemaps.Client(key=API_KEY)


def Create_Proximity_Edges(zones_gpd):
    connectionList = []
    for i in tqdm.trange(len(zones_gpd)):
        currGeom = zones_gpd.loc[i]['geometry']
        currGeomBuffed = currGeom.buffer(0.0005)
        for j in range(len(zones_gpd)):
            if i == j:
                continue
            matchGeom = zones_gpd.loc[j]['geometry']
            intsec_ = currGeomBuffed.intersection(matchGeom)
            if not intsec_.is_empty:
                connectionList.append([i,j])
    return connectionList
            
def save_file(file, path):
    with open(path, 'wb') as savepath:
        pickle.dump(file, savepath)
    
def get_travel_time(zoneid_o, zoneid_d, mode='driving'):
    lat_o = nycZones.loc[zoneid_o]['geometry'].centroid.xy[1][0]
    lng_o = nycZones.loc[zoneid_o]['geometry'].centroid.xy[0][0]
    lat_d = nycZones.loc[zoneid_d]['geometry'].centroid.xy[1][0]
    lng_d = nycZones.loc[zoneid_d]['geometry'].centroid.xy[0][0]
    if mode == 'driving':
        dm = gmaps.distance_matrix((lat_d, lng_d), (lat_o, lng_o), mode='driving')
        stringOfTravelTime = dm['rows'][0]['elements'][0]['duration']['text']
        travelTimeMinutes = get_minutes_from_timestring(stringOfTravelTime)
    elif mode == 'transit':
        dm_rail = gmaps.distance_matrix((lat_d, lng_d), (lat_o, lng_o), mode='transit', transit_mode='rail')
        railTimeStr = dm_rail['rows'][0]['elements'][0]['duration']['text']
        railMins = get_minutes_from_timestring(railTimeStr)
        print (railTimeStr)
        dm_bus = gmaps.distance_matrix((lat_d, lng_d), (lat_o, lng_o), mode='transit', transit_mode='bus')
        busTimeStr = dm_bus['rows'][0]['elements'][0]['duration']['text']
        busMins = get_minutes_from_timestring(busTimeStr)
        travelTimeMinutes = min(railMins, busMins)
    else:
        raise ('Invalid mode!')
    return travelTimeMinutes

def get_minutes_from_timestring(timestring):
    extractedNums = [int(str_) for str_ in timestring.split() if str_.isdigit() ]
    traveltimemins = sum([ extractedNums[-_i-1] * [60, 1][-_i-1]  for _i, timedigit in enumerate(extractedNums)  ])    
    return traveltimemins


if __name__ == "__main__":
    
    
    dm = get_travel_time(4,237,'driving')
    # dm = gmaps.distance_matrix((41.6, -74.2), (40.65, -74.1), mode='walking')
    
    # zones_gpd = 'data/NYC Taxi Zones/NYC Taxi Zones.geojson'
    # nycZones = gpd.read_file(zones_gpd)
    
    # proxConn_ = Create_Proximity_Edges(nycZones)
    
    # save_file(proxConn_, 'data/proxList')
    
    # testGeomBuffed = nycZones.loc[0]['geometry'].buffer(0.001)
    # x, y = testGeomBuffed.exterior.xy
    # plt.plot(x, y)