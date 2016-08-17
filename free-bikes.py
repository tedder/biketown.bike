#!/usr/local/bin/python3

import requests
from geopy.distance import vincenty

# lat, lon
myloc = (45.532807, -122.698514)

fbs = requests.get('http://biketownpdx.socialbicycles.com/opendata/free_bike_status.json')
nearest = (None, None, None)
for bike in fbs.json()['data']['bikes']:
  dist_ft = vincenty(myloc, (bike['lat'], bike['lon'])).feet
  #print(dist_ft, bike['lat'], bike['lon'])
  if not nearest or not nearest[0] or dist_ft < nearest[0]:
    nearest = (dist_ft, bike['lat'], bike['lon'])
  if dist_ft < 1000:
    print(dist_ft, bike['lat'], bike['lon'])
print("nearest: ", nearest)
print("http://www.openstreetmap.org/index.html?lat={0}&lon={1}&mlat={0}&mlon={1}&zoom=16".format(nearest[1], nearest[2]))
