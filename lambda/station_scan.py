#!/usr/bin/python2.7

import requests
import time
import boto3

TABLENAME='biketown_station_scan'

def create_dynamodb_item(station_id, station_count, last_updated):
  return {
    'Item': {
      'station_id': {
        'S': str(station_id)
      },
      'scan_epoch': {
        'N': str(last_updated)
      },
      'station_count': {
        'N': str(station_count)
      }
    }
  }

def create_batchlist(items):
  ret = []
  for item in items:
    if not item:
      raise("wat, empty item")
    ret.append({ 'PutRequest': item })

  # after it works, use this?
  #return [{ 'PutRequest': item } for item in items]
  return ret

def scan(event, context):
  dy = boto3.client('dynamodb')

  stations = requests.get("http://biketownpdx.socialbicycles.com/opendata/station_status.json")
  stations_json = stations.json()
  last_updated = stations_json.get('last_updated')
  stale_seconds = time.time() - last_updated
  if stale_seconds > 600:
    raise Exception('eep, station status appears stale; last updated {} seconds ago.'.format(stale_seconds))

  items = []
  for station in stations.json()['data']['stations']:
    item = create_dynamodb_item(station['station_id'], station['num_bikes_available'], station['last_reported'])
    items.append(item)

  # max 25 put/del requests; chunk and look for 'UnprocessedItems'
  while len(items): 
    print("item count: {}".format(len(items)))
    # can only do max 25 records at a time
    curritems = items[len(items)-23:]
    items = items[:len(items)-23]
    print(" sliced: {} / {}".format(len(curritems), len(items)))
    print(" {}".format(curritems))


    write_ret = dy.batch_write_item(
      RequestItems={
        TABLENAME: create_batchlist(curritems),
        #TABLENAME: [create_batchlist(items[:25])],
      }
      #ReturnConsumedCapacity='INDEXES/TOTAL',
      #ReturnItemCollectionMetrics='SIZE'
    )
    unproc = write_ret.get('UnprocessedItems', {}).get(TABLENAME)
    if unproc and len(unproc):
      items.extend(unproc)

    #iteration += 1
    if len(items):
      # sleep 100msec between bulk writes
      time.sleep(100/1000)

  return "done"

scan(None, None)

