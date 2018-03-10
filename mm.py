import groupy
import random
import markovify
from time import time, sleep
import Database as db
import json
import re

VERSION = '7.0.3 dev build'
TESTING = False
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

#list of active group objects
active_groups = [item['group'] for item in GROUPS if item['name'] in active_group_names]
group_dict = {item['id']:item['group'] for item in GROUPS}
for item in GROUPS:
    g = item['group']
    g.simple_name = item['name']
    g.imitation_allowed = item['imitation']

#Setup Log group

LOG_GROUP = [item['group'] for item in GROUPS if item['name'] =='Log'][0]

def log(string):
    try:
        print(string)
        if not TESTING:
            LOG_GROUP.post(string)
    except:
        pass

## Reaction Functions

def imitate(m,g):
    try:
        text = m.text.lower()
        if 'good' in text:
            pattern = re.compile('good(\d+)')
            match = pattern.search(text)
            goodness = 5 if match==None else int(match.group()[4:])
        else:
            goodness = 0

        log('{2}: Imitating {0} with {1} goodness'.format(m.name,goodness,g.simple_name))

        model = markovify.Text(db.user_full_text(g.group_id, m.user_id,goodness))
        for i in range(5):
            imitation = model.make_short_sentence(200)
            if imitation != None:
                break
            else:
                imitation = 'Insufficient data for imitation.'
        g.post('{0}: {1}'.format(m.name,imitation))
    except:
        log('Imitation failed - message [{0} - {1}] in [{2} - {3}]'.format(m.id,m.text,g.id,g.name))

def execute_command(command,permission):
    log('Commands not active.')

def read_log_message(m, g):
    if m.text.startswith('/'):
        command = m.text[1:].split()
        permission = True if m.user_id in ADMINS else False
        execute_command(command,permission)

def read_message(m, g):
    if g == LOG_GROUP:
        read_log_message(m,g)
    if m.mentions_me() and g.imitation_allowed:
        imitate(m,g)

## Loading Functions

def group_messages(group):
    try:
        messages = group.messages()
    except groupy.api.errors.ApiError:
        messages = group_messages(group)
    return messages

def save_all_messages(group):
    messages = group_messages(group)

    print('loading all messages - {}'.format(group.name))
    while messages.iolder():
        pass
    print('saving messages')
    db.clear_data(group.id)
    db.save_multiple(messages)

def save_recent_messages(group,read=False):
    messages = group_messages(group)
    saved_messages = db.saved_message_ids(group.id)
    
    #Load messages until previously saved appear
    while messages.iolder():
        saved = False
        
        for m in messages:
            if m.id in saved_messages:
                saved = True
                break

        if saved:
            break
   
   #For all loaded messages, execute read function and save message to db
    entry = []
    for m in messages:
        if m.id not in saved_messages:
            if read:
                read_message(m,group)
            entry.append(m)
    if len(entry)>0:
        db.save_multiple(entry)



log('Meme Machine {0}'.format(VERSION))
log('Active groups - {}'.format(', '.join([group.name for group in active_groups])))

for group in active_groups:
    log('Catching up to {}'.format(group.name))
    save_recent_messages(group)

log('Ready to meme')

while True:
    for group in active_groups:
        save_recent_messages(group,True)
    #sleep(0.01)