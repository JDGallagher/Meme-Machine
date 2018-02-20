import groupy
import random
import markovify
from time import time, sleep
import Database as db
import json

VERSION = '7.0.0'
TESTING = True
START_TIME = time()

with open('admins.json','r') as fp:
    ADMINS = json.load(fp)

with open('groups.json','r') as fp:
    GROUPS = json.load(fp)

#enable correct groups if in testing mode or not
active_group_names = ['Test','Log'] if TESTING else [item['name'] for item in GROUPS]

#fill group dicts with groupy objects
for g in groupy.Group.list():
    for item in GROUPS:
        if g.id == item['id']:
            item['group'] = g

#list of active groupy group objects
active_groups = [item['group'] for item in GROUPS if item['name'] in active_group_names]

def log(string):
    group = [item['group'] for item in GROUPS if item['name'] =='Log'][0]

    try:
        print(string)
        if not TESTING:
            group.post(string)
    except:
        pass

log('Meme Machine {0}'.format(VERSION))
log('Active groups - {}'.format(', '.join([group.name for group in active_groups])))

for group in active_groups:
    log('Catching up to {}'.format(group.name))
    db.save_recent_messages(group)
