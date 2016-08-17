#!/usr/bin/env python3

import csv
import sys
import requests
import json

if len(sys.argv) < 2:
  print("need input csv as first arg")
  sys.exit(-1)

# 0    1    2             3   4
#rank,Name,Rentals total,lat,lon

stations_ret = requests.get("http://biketownpdx.socialbicycles.com/opendata/station_information.json").json()
stations = { station['name']: station for station in stations_ret['data']['stations'] }

geojson = {
  'type': 'FeatureCollection',
  'features': []
}

with open(sys.argv[1]) as csvfile:
  creader = csv.reader(csvfile)
  cwriter = csv.writer(sys.stdout)
  next(creader) #cwriter.writerow(next(creader)) # header
  for row in creader:
    # make sure the row is the length we need
    ret = [None]*5
    for i in range(len(row)):
      ret[i] = row[i]

    station_name = row[1]
    station = stations.get(station_name)
    if not station:
      print("couldn't find station: {}, row: {}".format(row[1], ','.join(row))) 
      sys.exit(0)
    ret[3] = station['lat']
    ret[4] = station['lon']
    #cwriter.writerow(ret)
    percentage_of_max = (int(row[2])/4011) # hardcoding the max station usage as 4011. shade them to that.
    shading = int(255-(percentage_of_max*255))
    color = '#{0:02X}{0:02X}FF'.format(shading)
    #color = '#0000{:02X}'.format(shading)
    sys.stderr.write("color: {}, percentage: {}, count: {}\n".format(color, percentage_of_max, row[2]))

    geojson['features'].append({
      'type': 'Feature',
      'geometry': {
        'type': 'Point',
        'coordinates': [
          station['lon'],
          station['lat']
        ]
      },
      'properties': {
        'title': "{} dockings, {}".format(row[2], row[1]),
        'marker-color': color
      }
    })
    

print(json.dumps(geojson))
