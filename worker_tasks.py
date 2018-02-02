import os, json
import redis
import datetime as dt
from mnist import random_image

REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'chat'
redis = redis.from_url(REDISCLOUD_URL)
start_time = dt.datetime.now()
interval = 10 # seconds

def publish(value):
    message = json.dumps({
                           'id': 'worker',
                           'time_stamp': str(dt.datetime.now())
                         })
    message.update(value)
    redis.publish(REDIS_CHAN, message)

def print_time():
    t = dt.datetime.now()
    i = 1

    while True:
      delta=dt.datetime.now()-t
      if delta.seconds >= interval:
         value = i
         publish(random_image())
         i += 1
         t = dt.datetime.now()