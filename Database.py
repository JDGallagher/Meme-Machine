from tinydb import TinyDB, Query
import pprint

def clear_data(group_id):
    db = TinyDB('data/{}.json'.format(group_id))
    db.purge()

def user_messages(group_id, user_id):
    db = TinyDB('data/{}.json'.format(group_id))
    Message = Query()
    result = db.search(Message.user_id == user_id)
    return result

def user_full_text(group_id, user_id, min_likes = 0):
    text = [str(item['text']) for item in user_messages(group_id, user_id) if len(item['favorited_by']) >= min_likes]
    full_text = '. '.join(text)
    return full_text

def group_full_text(group_id, min_likes = 0):
    db = TinyDB('data/{}.json'.format(group_id))
    text = [str(item['text']) for item in db.all() if len(item['favorited_by']) >= min_likes]
    full_text = '. '.join(text)
    return full_text

def saved_message_ids(group_id):
    db = TinyDB('data/{}.json'.format(group_id))
    return [item['id'] for item in db.all()]

def message_entry(m):
    try:
        name = str(m.name.encode('ascii', 'backslashreplace'))[2:-1]
    except AttributeError:
        name = None

    try:
        text = str(m.text.encode('ascii', 'backslashreplace'))[2:-1]
    except AttributeError:
        text = None

    attachments = []
    for item in m.attachments:
        if item.type == 'emoji':
            attachments.append('Emoji(charmap={})'.format(item.charmap))
        else:
            attachments.append(str(item))
    
    entry = {'created_at': str(m.created_at),
           'id': m.id,
           'user_id': m.user_id,
           'name': name,
           'text': text,
           'favorited_by': m.favorited_by,
           'avatar_url': m.avatar_url,
           'attachments': attachments,
           'source_guid': m.source_guid}

    return entry

def save_message(m):
    db = TinyDB('data/{}.json'.format(m.group_id))
    db.insert(message_entry(m))

def save_multiple(messages):
    db = TinyDB('data/{}.json'.format(messages[0].group_id))
    entries = []
    for m in messages:
        entries.append(message_entry(m))
    db.insert_multiple(entries)